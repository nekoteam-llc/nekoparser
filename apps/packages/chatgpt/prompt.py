import json
from abc import ABC, abstractmethod
from typing import Any

from packages.database import Config, TheSession

from .exceptions import ChatGPTException
from .models import ChatGPTQuery


class Prompt(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    async def generate(self) -> ChatGPTQuery:
        pass

    @abstractmethod
    async def parse_response(self, response: dict) -> Any:
        pass


def get_config() -> Config:
    with TheSession() as session:
        return session.query(Config).one()


class ExtractProperties(Prompt):
    def __init__(self, keywords: str):
        self._keywords = keywords

    async def generate(self) -> ChatGPTQuery:
        return ChatGPTQuery(
            system_message=get_config().properties_prompt,
            user_message=self._keywords,
        )

    async def parse_response(self, response: dict) -> dict:
        return response


class NormalizeDescription(Prompt):
    def __init__(self, description: str):
        self._description = description

    async def generate(self) -> ChatGPTQuery:
        return ChatGPTQuery(
            system_message=get_config().description_prompt,
            user_message=self._description,
        )

    async def parse_response(self, response: dict) -> str:
        if "text" not in response:
            raise ChatGPTException("Invalid response from ChatGPT.")

        return response["text"]


class ExtractKeywords(Prompt):
    def __init__(self, text: str):
        self._text = text

    async def generate(self) -> ChatGPTQuery:
        return ChatGPTQuery(
            system_message=get_config().keywords_prompt,
            user_message=self._text,
        )

    async def parse_response(self, response: dict) -> list:
        if "keywords" not in response:
            raise ChatGPTException("Invalid response from ChatGPT.")

        return response["keywords"]


class FindSKU(Prompt):
    def __init__(self, columns: dict[str, str]):
        self._columns = columns

    async def generate(self) -> ChatGPTQuery:
        return ChatGPTQuery(
            system_message=get_config().columns_prompt,
            user_message=json.dumps(self._columns, ensure_ascii=False),
        )

    async def parse_response(self, response: dict) -> str:
        if "column" not in response:
            raise ChatGPTException("Invalid response from ChatGPT.")

        return response["column"]
