import asyncio
from datetime import timedelta
from typing import Optional, TypedDict

from httpx import AsyncClient, HTTPError
from prefect import flow, task
from prefect.tasks import task_input_hash
from sqlalchemy import bindparam, update

from packages.database import SessionLocal, WebsiteSource, WebsiteSourceState
from packages.log import get_logger


class ScrapedWebsite(TypedDict):
    """
    Represents the scraped website data
    """

    id: str
    contents: Optional[str]
    state: WebsiteSourceState


@task(
    name="Scrape website",
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(days=1),
    tags=["websites"],
)
async def scrape_website(id: str, url: str) -> ScrapedWebsite:
    """
    Scrape the website for the data
    """

    logger = get_logger()

    try:
        async with AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
    except HTTPError:
        logger.error("Failed to scrape the website", extra={"id": id, "url": url})
        return ScrapedWebsite(
            id=id,
            contents=None,
            state=WebsiteSourceState.UNAVAILABLE,
        )

    logger.info(
        "Scraped the website",
        extra={"id": id, "url": url, "content_length": len(response.text)},
    )

    return ScrapedWebsite(
        id=id,
        contents=response.text,
        state=WebsiteSourceState.SCRAPED,
    )


@flow(name="Scrape websites", log_prints=True)
async def scrape_websites():
    """
    Scrape the websites for the data
    """

    with SessionLocal() as session:
        websites = (
            session.query(WebsiteSource.id, WebsiteSource.url)
            .filter(WebsiteSource.state == WebsiteSourceState.CREATED)
            .all()
        )

    if not websites:
        return

    results = await asyncio.gather(
        *[scrape_website(website.id, website.url) for website in websites]
    )

    with SessionLocal() as session:
        session.execute(
            (
                update(WebsiteSource)
                .values(contents=bindparam("contents"), state=bindparam("state"))
                .execution_options(synchronize_session=False)
            ),
            results,
        )
        session.commit()
