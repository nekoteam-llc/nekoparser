from packages.config import BaseConfig


class TransformationsConfig(BaseConfig):
    """
    Transformations configuration
    """

    gemini_api_key: str


config = TransformationsConfig()  # pyright: ignore[reportCallIssue]
