from typing import Optional

from pydantic import Field

from packages.config import BaseConfig


class AppConfig(BaseConfig):
    json_logs: bool = Field(default=False, description="Whether to log in JSON format")
    log_level: str = Field(
        default="INFO",
        description="The log level to use. One of: DEBUG, INFO, WARNING, ERROR, CRITICAL",
    )
    sentry_dsn: Optional[str] = Field(
        default=None,
        description="The DSN for Sentry error tracking",
    )


config = AppConfig()
