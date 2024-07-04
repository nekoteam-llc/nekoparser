import json
from typing import Any

import aiohttp

from .config import config
from .exceptions import ChatGPTException
from .models import ChatGPTQuery
from .prompt import Prompt


class ChatGPTClient:
    def __init__(self):
        self.api_key = config.chatgpt_api_key
        self.api_url = config.chatgpt_api_url

    async def _request(self, query: ChatGPTQuery) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                json={
                    "max_tokens": 3000,
                    "llm_model": config.chatgpt_model,
                    "json_only": True,
                    **query.model_dump(),
                },
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json",
                },
            ) as response:
                return await response.json()

    async def __call__(self, prompt: Prompt) -> Any:
        query = await prompt.generate()
        response = await self._request(query)
        try:
            result = json.loads(response["choices"][0]["message"]["content"])
        except (KeyError, IndexError):
            raise ChatGPTException("Invalid response from ChatGPT.")

        return await prompt.parse_response(result)


chatgpt = ChatGPTClient()
