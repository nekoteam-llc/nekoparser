from packages.config import BaseConfig


class DatabaseConfig(BaseConfig):
    """
    Database configuration
    """

    host: str
    port: int
    user: str
    password: str
    name: str


config = DatabaseConfig()  # pyright: ignore[reportCallIssue]
