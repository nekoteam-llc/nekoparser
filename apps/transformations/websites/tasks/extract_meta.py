import asyncio
import hashlib
from datetime import timedelta
from typing import Optional, TypedDict

from bs4 import BeautifulSoup, Tag
from prefect import flow, task
from prefect.context import TaskRunContext
from sqlalchemy import bindparam, update

from packages.database import SessionLocal, WebsiteSource, WebsiteSourceState
from packages.log import get_logger


class ScrapedMeta(TypedDict):
    """
    Represents the scraped website data
    """

    id: str
    ui_name: Optional[str]
    ui_description: Optional[str]
    ui_image: Optional[str]


def custom_hasher(_: TaskRunContext, arguments: dict) -> str:
    """
    Custom hasher for the task
    """

    return hashlib.sha256(arguments["contents"].encode()).hexdigest()


@task(
    name="Extract website meta",
    cache_key_fn=custom_hasher,
    result_serializer="json",
    cache_expiration=timedelta(days=1),
    tags=["bs4"],
)
async def extract_website_meta_single(id: str, contents: str) -> ScrapedMeta:
    """
    Scrape the website for the data
    """

    logger = get_logger()

    ui_name, ui_description, ui_image = None, None, None

    soup = BeautifulSoup(contents, "html.parser")

    ui_name = soup.title.string if soup.title else None
    if (
        description_tag := soup.find("meta", attrs={"name": "description"})
    ) and isinstance(description_tag, Tag):
        ui_description = description_tag.attrs.get("content")

    if (
        not ui_description
        and (description_tag := soup.find("meta", attrs={"property": "og:description"}))
        and isinstance(description_tag, Tag)
    ):
        ui_description = description_tag.attrs.get("content")

    if (image_tag := soup.find("meta", attrs={"property": "og:image"})) and isinstance(
        image_tag, Tag
    ):
        ui_image = image_tag.attrs.get("content")

    if (
        not ui_image
        and (image_tag := soup.find("link", attrs={"rel": "icon"}))
        and isinstance(image_tag, Tag)
    ):
        ui_image = image_tag.attrs.get("href")

    if (
        not ui_image
        and (image_tag := soup.find("link", attrs={"rel": "image_src"}))
        and isinstance(image_tag, Tag)
    ):
        ui_image = image_tag.attrs.get("content")

    logger.info(
        "Extracted the website meta",
        extra={"id": id, "ui_name": ui_name, "ui_description": ui_description},
    )

    return ScrapedMeta(
        id=id,
        ui_name=ui_name,
        ui_description=ui_description,
        ui_image=ui_image,
    )


@flow(name="Extract websites meta", log_prints=True)
async def extract_website_meta_many():
    """
    Scrape the websites for the data
    """

    with SessionLocal() as session:
        websites = (
            session.query(WebsiteSource.id, WebsiteSource.contents)
            .filter(WebsiteSource.state == WebsiteSourceState.SCRAPED)
            .all()
        )

    if not websites:
        return

    results = await asyncio.gather(
        *[
            extract_website_meta_single(website.id, website.contents)
            for website in websites
        ]
    )

    with SessionLocal() as session:
        session.execute(
            (
                update(WebsiteSource)
                .values(
                    ui_name=bindparam("ui_name"),
                    ui_description=bindparam("ui_description"),
                    ui_image=bindparam("ui_image"),
                )
                .execution_options(synchronize_session=False)
            ),
            results,
        )
        session.commit()
