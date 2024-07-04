from packages.config import BaseConfig


class ChatGPTConfig(BaseConfig):
    """
    ChatGPT configuration
    """

    chatgpt_api_key: str
    chatgpt_api_url: str
    chatgpt_model: str = "gpt-3.5-turbo"


config = ChatGPTConfig()  # pyright: ignore[reportCallIssue]
