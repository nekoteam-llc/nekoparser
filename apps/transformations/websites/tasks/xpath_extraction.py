import asyncio
import hashlib
import re
from datetime import datetime
from urllib.parse import urlparse

from lxml import etree
from prefect import flow, task
from sqlalchemy.dialects.postgresql import insert

from packages.database import Product, TheSession, WebsiteSource, WebsiteSourceState
from packages.log import get_logger
from packages.schemas.satu import UserFilledData
from transformations.utils import reload_sources

from .scrape_website import scrape_website


def process_image(url: str, img: etree._Element) -> str:
    if img.tag == "img":
        img_url = img.get("src", "")
        if img_url.startswith("/"):
            return f"{urlparse(url).scheme}://{urlparse(url).hostname}{img_url}"

        return str(img_url)

    closest_imgs = img.xpath(".//img")
    if not isinstance(closest_imgs, list) or not closest_imgs:
        return "N/A"

    closest_img = list(
        sorted(
            filter(
                lambda x: isinstance(x, etree._Element) and hasattr(x, "get"),
                closest_imgs,
            ),
            key=lambda x: len(x.get("src", "")),  # type: ignore
            reverse=True,
        )
    )[0]

    img_url = closest_img.get("src", "")  # type: ignore
    if img_url.startswith("/"):
        return f"{urlparse(url).scheme}://{urlparse(url).hostname}{img_url}"

    return str(img_url)


def process_price(price: str) -> float:
    try:
        return float(re.sub(r"[^\d.]", "", price.replace(",", ".")))
    except ValueError:
        return -1


def process_arbitrary_string(currency: str) -> str:
    return re.sub(r"[^A-Za-zА-Яа-яЁёÀ-ÿ.]", "", currency)


def process_description(description: str) -> str:
    return (
        re.sub(
            r"\n{2,}",
            "\n",
            description.replace("\t", "").replace("\r", "").strip(),
        )
        .removeprefix("Описание")
        .strip()
    )


PAGES_CHUNK_SIZE = 5
PRODUCTS_CHUNK_SIZE = 30
CUSTOM_TRANSFORMERS = {
    "price": process_price,
    "currency": process_arbitrary_string,
    "measure_unit": process_arbitrary_string,
    "description": process_description,
    "properties": process_description,
}
CUSTOM_EXTRACTORS = {
    "main_image": process_image,
}
MANDATORY_FIELDS = ["name", "price", "currency", "measure_unit", "description"]


@task(name="Extract product info", tags=["lxml"])
async def extract_product(url: str, props_xpaths: dict[str, str]):
    """
    Extract product info

    :param url: The URL of the product
    :return: The scraped data
    """

    logger = get_logger()

    result = await scrape_website(url)
    if result["state"] == WebsiteSourceState.UNAVAILABLE or not result["contents"]:
        return

    parser = etree.HTMLParser()
    tree = etree.fromstring(result["contents"], parser)

    data = {}
    for field in UserFilledData.model_fields.keys():
        xpath = props_xpaths.get(field)
        if not xpath:
            logger.warning("Failed to extract product info", extra={"url": url})
            return None

        if field in CUSTOM_EXTRACTORS:
            elems = tree.xpath(xpath)
            if isinstance(elems, list) and elems and isinstance(elems[0], etree._Element):
                data[field] = CUSTOM_EXTRACTORS[field](url, elems[0])
            else:
                if field in MANDATORY_FIELDS:
                    logger.warning("Failed to extract product info", extra={"url": url})
                    return None

                data[field] = "N/A"
        else:
            elems = tree.xpath(f"{xpath}//text()")
            if isinstance(elems, list) and elems:
                data[field] = "".join(map(str, elems))
                if field in CUSTOM_TRANSFORMERS:
                    data[field] = CUSTOM_TRANSFORMERS[field](data[field])
            else:
                if field in MANDATORY_FIELDS:
                    logger.warning("Failed to extract product info", extra={"url": url})
                    return None

                data[field] = "N/A"

    meta_keywords = tree.xpath("//meta[@name='keywords']/@content")
    if meta_keywords and isinstance(meta_keywords, list) and meta_keywords[0]:
        data["keywords"] = meta_keywords[0]
    else:
        data["keywords"] = "N/A"

    data["url"] = url
    logger.info("Extracted product info", extra={"url": url, "data": data})

    return data


@flow(name="Extract products")
async def extract_products(id: str):
    """
    Extract products

    :param base_url: The base URL of the website
    :param contents: The contents of the website
    :return: The scraped data
    """

    logger = get_logger()

    with TheSession() as session:
        website = session.query(WebsiteSource).filter(WebsiteSource.id == id).first()

        if not website:
            logger.error("Website not found", extra={"website_id": id})
            return

        website.state = WebsiteSourceState.DATA_COLLECTING
        session.commit()

        await reload_sources()

        base_url = f"{urlparse(website.url).scheme}://{urlparse(website.url).hostname}"
        pagination = website.pagination_regex

        pagination_regex = re.escape(pagination).replace(r"%swp\-pagination%", r"(\d+)")
        if pagination_regex.startswith("http"):
            pagination_regex = re.sub(
                r"(https?://[^/]+)",
                r"(?:\g<1>)?",
                pagination_regex,
            )

        pages = re.findall(pagination_regex, website.contents)
        if not pages:
            logger.error("Failed to extract pagination", extra={"website_id": id})
            raise ValueError("Failed to extract pagination")

        pages = list(map(int, pages))
        pages.sort()
        last_page_n = pages[-1]
        logger.info("Extracted pagination", extra={"pages": last_page_n})

        current_page = 1
        last_page = False
        while True:
            if current_page > last_page_n:
                break

            tasks = []
            for _ in range(PAGES_CHUNK_SIZE):
                url = pagination.replace(r"%swp-pagination%", str(current_page))
                logger.info("Adding page to queue", extra={"url": url})
                tasks.append(scrape_website(url))
                current_page += 1
                if current_page > last_page_n:
                    break

            results = await asyncio.gather(*tasks)
            product_urls = set()
            total = 0
            for result in results:
                if result["state"] == WebsiteSourceState.UNAVAILABLE:
                    last_page = True
                    break

                parser = etree.HTMLParser()
                tree = etree.fromstring(result["contents"], parser)
                links = [
                    link.get("href") for link in tree.findall(".//a") if link.get("href")
                ]
                total += len(links)
                for link in links:
                    if link and link.startswith("/"):
                        link = f"{base_url}{link}"

                    if link and (product_url := re.search(website.product_regex, link)):
                        product_urls.add(product_url.group(0))

            logger.info(
                "Extracted product URLs",
                extra={"urls": len(product_urls), "total_urls": total},
            )

            if not product_urls:
                break

            product_urls = list(product_urls)
            chunked_product_urls = [
                product_urls[i : i + PRODUCTS_CHUNK_SIZE]
                for i in range(0, len(product_urls), PRODUCTS_CHUNK_SIZE)
            ]
            results = []
            for chunk in chunked_product_urls:
                results.extend(
                    await asyncio.gather(
                        *[extract_product(url, website.props_xpaths) for url in chunk]
                    )
                )

            results = list(filter(lambda x: x is not None, results))
            if not results:
                break

            insert_stmt = insert(Product).values(
                [
                    {
                        "hash": hashlib.sha256(result["name"].encode()).hexdigest(),
                        "data": result,
                        "url": result["url"],
                        "last_processed": datetime.now(),
                        "source_id": id,
                    }
                    for result in results
                ]
            )
            insert_stmt = insert_stmt.on_conflict_do_update(
                index_elements=["hash"],
                set_={
                    "data": insert_stmt.excluded.data,
                    "url": insert_stmt.excluded.url,
                    "last_processed": insert_stmt.excluded.last_processed,
                    "source_id": insert_stmt.excluded.source_id,
                },
            )
            session.execute(insert_stmt)
            session.commit()

            if last_page:
                break

            logger.info(
                "Chunk finished",
                extra={"current_page": current_page, "results": len(results)},
            )

            await asyncio.sleep(3)

        website.state = WebsiteSourceState.DATA_PENDING_APPROVAL
        session.commit()
        await reload_sources()

    logger.info("Extracted products", extra={"website_id": id})
    return id
