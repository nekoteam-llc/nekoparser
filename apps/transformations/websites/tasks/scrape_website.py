from datetime import timedelta
from typing import Optional, TypedDict

from fake_useragent import UserAgent
from httpx import AsyncClient, HTTPError
from prefect import task
from prefect.tasks import task_input_hash

from packages.database import WebsiteSourceState
from packages.log import get_logger


class ScrapedWebsite(TypedDict):
    """
    Represents the scraped website data
    """

    contents: Optional[str]
    state: WebsiteSourceState


@task(
    name="Scrape website",
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(days=1),
    tags=["websites"],
)
async def scrape_website(url: str) -> ScrapedWebsite:
    """
    Scrape the website for the data
    """

    logger = get_logger()

    try:
        async with AsyncClient() as client:
            response = await client.get(
                url,
                follow_redirects=True,
                headers={
                    "User-Agent": UserAgent(
                        browsers=["chrome"],
                        os=["macos"],
                        platforms=["pc"],
                    ).random
                },
            )
    except HTTPError:
        logger.error("Failed to scrape the website", extra={"url": url})
        return ScrapedWebsite(
            contents=None,
            state=WebsiteSourceState.UNAVAILABLE,
        )

    logger.info(
        "Scraped the website",
        extra={"url": url, "content_length": len(response.text)},
    )

    return ScrapedWebsite(
        contents=response.text,
        state=WebsiteSourceState.SCRAPED,
    )
