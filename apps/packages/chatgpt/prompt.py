from abc import ABC, abstractmethod
from typing import Any

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


class ExtractProperties(Prompt):
    def __init__(self, keywords: str):
        self._keywords = keywords

    async def generate(self) -> ChatGPTQuery:
        return ChatGPTQuery(
            system_message='You are a data scientist. You are given the set of data from the website and your goal is to extract the properties of the product from the text. You must respond with a valid JSON object, containing the dictionary of the extracted properties. For example: {"color": "red", "size": "small"}.',
            user_message=self._keywords,
        )

    async def parse_response(self, response: dict) -> dict:
        return response


class NormalizeDescription(Prompt):
    def __init__(self, description: str):
        self._description = description

    async def generate(self) -> ChatGPTQuery:
        return ChatGPTQuery(
            system_message='You are a data scientist. You are given a product description and your goal is to normalize the text. Remove any shop-specific parts, keep only the relevant information and technical specs of the product to showcase to the customer. Respond with a valid JSON object containing a single field - "text" with the normalized text.',
            user_message=self._description,
        )

    async def parse_response(self, response: dict) -> str:
        if "text" not in response:
            raise ChatGPTException("Invalid response from ChatGPT.")

        return response["text"]
