from packages.config import BaseConfig


class ChatGPTConfig(BaseConfig):
    """
    ChatGPT configuration
    """

    chatgpt_api_url: str


config = ChatGPTConfig()  # pyright: ignore[reportCallIssue]
