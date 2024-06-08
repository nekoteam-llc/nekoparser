from httpx import AsyncClient

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
