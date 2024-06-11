import contextlib
import logging
import sys
import warnings
from typing import Literal, Optional, Union, overload

import structlog
from structlog.types import EventDict, Processor

from .config import config

__all__ = ["get_logger"]


class PrefectRedirectLogger:
    def __init__(self, level):
        self.level = level

    def write(self, message):
        if message != "\n":
            self.level(message)

    def flush(self):
        self.level(sys.stderr)


class CustomLogging:
    def __init__(self):
        self._setup_complete: bool = False
        self._current_use_async: Optional[bool] = None
        self._fastapi: bool = False

        timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")
        self._processors: list[Processor] = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.stdlib.ExtraAdder(),
            self._drop_color_message_key,
            timestamper,
            structlog.processors.StackInfoRenderer(),
        ]

    def mark_fastapi(self) -> None:
        """
        Mark that the current environment is FastAPI
        """

        self._fastapi = True

    def get_logger(
        self,
        use_async: bool = False,
    ) -> Union[
        structlog.BoundLogger,
        structlog.stdlib.AsyncBoundLogger,
        logging.Logger,
        logging.LoggerAdapter,
    ]:
        """
        Initialize the logging system with the configuration from the environment.

        * For Prefect environment `structlog` + Prefect's internal logger will be used
        ! Warning: If attempted to use `use_async` in Prefect environment,
        ! a RuntimeError will be raised.
        ? For FastAPI environment use `hook_fastapi` instead
        ? For other environments use this function

        :param use_async: Whether to use async loggers. This is useful when running in an
                          async context, like a FastAPI application.
                          If you pass `True`, you should await each call to logging like so:
                          `await logger.info("message")`.
        """

        if self._fastapi and not use_async:
            raise RuntimeError("FastAPI environment requires async loggers")

        if self._setup_complete:
            if self._current_use_async != use_async:
                structlog.configure(
                    wrapper_class=(
                        structlog.stdlib.AsyncBoundLogger
                        if use_async
                        else structlog.stdlib.BoundLogger
                    ),
                )

            self._current_use_async = use_async
            return structlog.get_logger()

        self._init_sentry()

        running_in_prefect = False
        with contextlib.suppress(ImportError, RuntimeError):
            from prefect.context import get_run_context

            if get_run_context():
                running_in_prefect = True

        self._current_use_async = use_async

        if not running_in_prefect:
            # Should be handled by logging.yml in Prefect environment
            self._reset_default_logging()

        self._setup_logging(
            json_logs=config.json_logs,
            log_level=config.log_level,
            use_async=use_async,
        )
        self._setup_complete = True

        if running_in_prefect:
            if use_async:
                raise RuntimeError("Prefect environment does not support async loggers")

            from prefect import get_run_logger

            logging.getLogger("httpx").setLevel(logging.WARNING)
            run_logger = get_run_logger()
            sys.stdout = PrefectRedirectLogger(run_logger.info)
            sys.stderr = PrefectRedirectLogger(run_logger.error)
            return run_logger

        return structlog.get_logger()

    def _init_sentry(self):
        """
        Initialize Sentry for error tracking
        Will only be called if the `SENTRY_DSN` environment variable is set
        """

        if not config.sentry_dsn:
            return

        import sentry_sdk

        sentry_sdk.init(dsn=config.sentry_dsn)

    @staticmethod
    def _normalize_sentry_event(_, __, event_dict: EventDict) -> EventDict:
        """
        Normalize the event dict for Sentry
        """

        if "event" in event_dict:
            event_dict["msg"] = event_dict.pop("event")

        return event_dict

    def _setup_logging(
        self,
        json_logs: bool,
        log_level: str,
        use_async: bool,
    ):
        processors = self._processors.copy()

        if json_logs:
            # Format the exception only for JSON logs, as we want to pretty-print them when
            # using the ConsoleRenderer
            processors.append(structlog.processors.format_exc_info)

        structlog.configure(
            processors=processors
            + [
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=(
                structlog.stdlib.AsyncBoundLogger
                if use_async
                else structlog.stdlib.BoundLogger
            ),
            cache_logger_on_first_use=True,
        )

        log_renderer: Processor
        if json_logs:
            log_renderer = structlog.processors.JSONRenderer()
        else:
            log_renderer = structlog.dev.ConsoleRenderer()

        formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=self._processors,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                log_renderer,
            ],
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(log_level.upper())

        def handle_exception(exc_type, exc_value, exc_traceback):
            """
            Log any uncaught exception instead of letting it be printed by Python
            (but leave KeyboardInterrupt untouched to allow users to Ctrl+C to stop)
            See https://stackoverflow.com/a/16993115/3641865
            """
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            root_logger.error(
                "Uncaught exception",
                exc_info=(exc_type, exc_value, exc_traceback),
            )

        sys.excepthook = handle_exception

        showwarning_legacy = warnings.showwarning

        def showwarning(message, *args, **kwargs):
            """
            Log warnings using the root logger instead of printing them to stderr
            See https://loguru.readthedocs.io/en/stable/resources/migration.html#replacing-capturewarnings-function
            """
            root_logger.warning(message)
            showwarning_legacy(message, *args, **kwargs)

        warnings.showwarning = showwarning

    @staticmethod
    def _drop_color_message_key(_, __, event_dict: EventDict) -> EventDict:
        """
        Uvicorn logs the message a second time in the extra `color_message`, but we don't
        need it. This processor drops the key from the event dict if it exists.
        """
        event_dict.pop("color_message", None)
        return event_dict

    @staticmethod
    def _reset_default_logging():
        root_logger = logging.getLogger()

        for h in root_logger.handlers:
            root_logger.removeHandler(h)


custom_logging = CustomLogging()


@overload
def get_logger(
    use_async: Literal[False],
) -> Union[structlog.BoundLogger, logging.Logger, logging.LoggerAdapter]: ...


@overload
def get_logger(
    use_async: Literal[True],
) -> structlog.stdlib.AsyncBoundLogger: ...


@overload
def get_logger(
    use_async: bool = False,
) -> Union[
    structlog.BoundLogger,
    structlog.stdlib.AsyncBoundLogger,
    logging.Logger,
    logging.LoggerAdapter,
]: ...


def get_logger(
    use_async: bool = False,
) -> Union[
    structlog.BoundLogger,
    structlog.stdlib.AsyncBoundLogger,
    logging.Logger,
    logging.LoggerAdapter,
]:
    """
    Initialize the logging system with the configuration from the environment.

    * For Prefect environment `structlog` + Prefect's internal logger will be used
    ! Warning: If attempted to use `use_async` in Prefect environment,
    ! a RuntimeError will be raised.
    ? For FastAPI environment use `hook_fastapi` instead
    ? For other environments use this function

    :param use_async: Whether to use async loggers. This is useful when running in an
                      async context, like a FastAPI application.
                      If you pass `True`, you should await each call to logging like so:
                      `await logger.info("message")`.
    :example:
        .. code-block:: python
            from packages.log import get_logger

            logger = get_logger()
            logger.info("message")

            async_logger = get_logger(use_async=True)
            await async_logger.info("message")
    """

    return custom_logging.get_logger(use_async=use_async)
