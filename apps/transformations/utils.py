import re

from httpx import AsyncClient

from packages.chatgpt import (
    ExtractKeywords,
    NormalizeDescription,
    chatgpt,
)
from packages.log import get_logger

from .config import config


async def reload_sources():
    """
    Send the notification to backend to reload the sources
    """

    logger = get_logger()

    try:
        async with AsyncClient() as client:
            await client.post(f"{config.backend_url}/api/v1/sources/reload")
    except Exception as e:
        logger.exception(f"Failed to reload sources: {e}")


def arbitrary_cleanup(text: str) -> str:
    return (
        re.sub(
            r"\n{2,}",
            "\n",
            text.replace("\t", "").replace("\r", "").strip(),
        )
        .removeprefix("Описание")
        .strip()
    )


async def process_description(description: str) -> str:
    description = arbitrary_cleanup(description)
    if not description:
        return "N/A"

    try:
        return await chatgpt(NormalizeDescription(description))
    except Exception as e:
        get_logger().exception(
            "Failed to normalize description",
            extra={"error": str(e)},
        )
        return "N/A"


async def process_keywords(text: str) -> str:
    text = arbitrary_cleanup(text)
    if not text:
        return ""

    try:
        return ", ".join(await chatgpt(ExtractKeywords(text)))
    except Exception as e:
        get_logger().exception("Failed to extract keywords", extra={"error": str(e)})
        return ""
