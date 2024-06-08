import time
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from fastapi import FastAPI
    from starlette.requests import Request
    from starlette.responses import Response

from uvicorn.protocols.utils import get_path_with_query_string

from .custom_logging import custom_logging, get_logger

__all__ = ["hook_fastapi"]


def hook_fastapi(app: "FastAPI") -> structlog.stdlib.AsyncBoundLogger:
    """
    Initialize the logging system for a FastAPI application.

    :param app: The FastAPI application to attach the middleware to.
    :example:
        .. code-block:: python
            import structlog
            from fastapi import FastAPI
            from packages.log import hook_fastapi
            app = FastAPI()
            logger = hook_fastapi(app)

            @app.get("/")
            async def root():
                await logger.info("message")
    """

    get_logger(use_async=True)
    custom_logging.mark_fastapi()
    access_logger = structlog.stdlib.get_logger("api.access")

    @app.middleware("http")
    async def _(request: "Request", call_next) -> "Response":
        from starlette.responses import Response

        structlog.contextvars.clear_contextvars()
        request_id = request.headers.get("x-request-id")
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter_ns()
        response = Response(status_code=500)

        try:
            response = await call_next(request)
        except Exception:
            await structlog.stdlib.get_logger("api.error").exception("Uncaught exception")
            raise
        finally:
            process_time = time.perf_counter_ns() - start_time
            status_code = response.status_code

            url = get_path_with_query_string(request.scope)  # pyright: ignore[reportArgumentType]

            if request.client:
                client_host = request.client.host
                client_port = request.client.port
            else:
                client_host = ""
                client_port = ""

            proxy = request.headers.get("x-forwarded-for", "")
            proxy = f" ({proxy})" if proxy else ""
            http_method = request.method
            http_version = request.scope["http_version"]
            path = request.scope["path"]

            if path != "/ping":
                await access_logger.info(
                    (
                        f'{client_host}:{client_port}{proxy} - "{http_method} '
                        f'{url} HTTP/{http_version}" {status_code}'
                    ),
                    http={
                        "url": url,
                        "status_code": status_code,
                        "method": http_method,
                        "request_id": request_id,
                        "version": http_version,
                    },
                    duration=process_time,
                )
            response.headers["X-Process-Time"] = str(process_time / 10**9)
            return response

    return structlog.get_logger()
