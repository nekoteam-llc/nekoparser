from packages.config import BaseConfig


class TransformationsConfig(BaseConfig):
    """
    Transformations configuration
    """

    gemini_api_key: str
    backend_url: str


config = TransformationsConfig()  # pyright: ignore[reportCallIssue]
