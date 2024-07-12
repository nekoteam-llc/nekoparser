from packages.config import BaseConfig


class MinIOConfig(BaseConfig):
    """
    Database configuration
    """

    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str


config = MinIOConfig()  # pyright: ignore[reportCallIssue]
