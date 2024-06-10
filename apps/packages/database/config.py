from packages.config import BaseConfig


class DatabaseConfig(BaseConfig):
    """
    Database configuration
    """

    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str


config = DatabaseConfig()  # pyright: ignore[reportCallIssue]
