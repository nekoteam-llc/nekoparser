import hashlib
from datetime import timedelta
from typing import Optional, TypedDict

from lxml import etree
from prefect import task
from prefect.context import TaskRunContext

from packages.database import WebsiteSourceState
from packages.log import get_logger


class ScrapedMeta(TypedDict):
    """
    Represents the scraped website data
    """

    name: Optional[str]
    description: Optional[str]
    favicon: Optional[str]
    state: WebsiteSourceState


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
    tags=["lxml"],
)
async def extract_website_meta(base_url: str, contents: str) -> ScrapedMeta:
    """
    Scrape the website for the data

    :param base_url: The base URL of the website
    :param contents: The contents of the website
    :return: The scraped data
    """

    logger = get_logger()

    name, description, favicon = None, None, None

    parser = etree.HTMLParser()
    tree = etree.fromstring(contents, parser)

    title_tag = tree.find(".//title")
    name = title_tag.text if title_tag is not None else None

    description_tags = [
        tree.find(".//meta[@name='description']"),
        tree.find(".//meta[@property='og:description']"),
        tree.find(".//meta[@property='twitter:description']"),
    ]

    for description_tag in description_tags:
        if description_tag is not None:
            description = description_tag.get("content")
            break

    links = tree.findall(".//link")
    for link in links:
        rel = link.get("rel")
        if rel is not None and "icon" in rel:
            favicon = link.get("href")
            break
    else:
        image_tags = [
            tree.find(".//meta[@property='og:image']"),
            tree.find(".//meta[@property='twitter:image']"),
            tree.find(".//meta[@name='twitter:image']"),
            tree.find(".//link[@rel='image_src']"),
        ]

        for image_tag in image_tags:
            if image_tag is not None:
                favicon = image_tag.get("content")
                break

    if favicon and favicon.startswith("/"):
        favicon = f"{base_url}{favicon}"

    logger.info(
        "Extracted the website meta",
        extra={"name": name, "description": description, "favicon": favicon},
    )

    return ScrapedMeta(
        name=name,
        description=description,
        favicon=favicon,
        state=WebsiteSourceState.XPATHS_PENDING,
    )
