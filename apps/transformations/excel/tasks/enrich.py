from datetime import timedelta

import aiohttp
from lxml import etree
from prefect import task

from transformations.utils import process_description, process_keywords


@task(
    name="Enrich product",
    result_serializer="json",
    cache_expiration=timedelta(days=1),
    tags=["lxml"],
)
async def enrich_product(sku: str, exists: bool = False) -> tuple[str, dict]:
    """
    Search for the product information

    :param sku: The SKU of the product
    :param exists: Whether the product already exists
    :return: The product information
    """

    async with aiohttp.ClientSession() as session:
        response = await session.get(
            f"https://kz.obo-bettermann.com/poisk/?searchparam={sku}"
        )
        if response.status != 200:
            raise ValueError("Invalid response from the server")

        data = await response.text()

    parser = etree.HTMLParser()
    tree = etree.fromstring(data, parser)

    def extract(xpath: str) -> str:
        elems = tree.xpath(f"{xpath}//text()")
        if isinstance(elems, list):
            return " ".join(map(str, elems)).strip()

        return ""

    properties = {}
    props_wrapper = tree.find(".//div[@id='variants']")
    if props_wrapper is not None:
        props = props_wrapper.findall(".//form")
        for prop in props:
            table = prop.find(".//table")
            if table is not None:
                rows = table.findall(".//tr")
                for row in rows:
                    cells = row.findall(".//th") + row.findall(".//td")
                    if len(cells) == 2:
                        key_elem = cells[0].xpath(".//text()")
                        value_elem = cells[1].xpath(".//text()")
                        if isinstance(key_elem, list) and isinstance(value_elem, list):
                            properties["".join(map(str, key_elem)).strip()] = "".join(
                                map(str, value_elem)
                            ).strip()

    img_xpath = tree.xpath(".//a[@id='zoom-v']//img/@src")
    if not isinstance(img_xpath, list) or not img_xpath:
        img_xpath = [None]

    description = None
    if not exists:
        description = await process_description(
            extract(".//div[@id='productDescriptionText']")
        )

    return (
        sku,
        {
            "name": extract(".//h1[@id='productTitle']") or None,
            "price": "N/A",
            "currency": "N/A",
            "measure_unit": extract(
                ".//div[@class='amount-field-wrapper']//div[2]//label"
            )
            or "N/A",
            "main_image": img_xpath[0] or "N/A",
            "properties": properties or "N/A",
            **({"description": description} if not exists else {}),
            **(
                {"keywords": await process_keywords(description) or "N/A"}
                if not exists and description
                else {}
            ),
        },
    )
