import json
from typing import Any

import aiohttp

from packages.database import Config, TheSession

from .config import config
from .exceptions import ChatGPTException
from .models import ChatGPTQuery
from .prompt import Prompt


class ChatGPTClient:
    def __init__(self):
        self.api_url = config.chatgpt_api_url

    async def _request(self, query: ChatGPTQuery) -> dict:
        with TheSession() as session:
            global_config = session.query(Config).one()

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                json={
                    "model": global_config.model,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": query.system_message},
                        {"role": "user", "content": query.user_message},
                    ],
                    "temperature": 0.1,
                },
                headers={
                    "Authorization": f"Bearer {global_config.chatgpt_key}",
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
