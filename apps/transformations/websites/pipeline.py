from urllib.parse import urlparse

from prefect import flow
from prefect.states import Completed, Failed

from packages.database import TheSession, WebsiteSource, WebsiteSourceState
from transformations.utils import reload_sources

from .tasks import extract_website_meta, scrape_website
from .tasks.xpath_extraction import extract_products, reprocess_products

__all__ = ["initial_processing", "extract_products", "reprocess_products"]


@flow(name="Initial Website Processing", log_prints=True)
async def initial_processing(id: str):
    """
    Initial processing of the website

    :param url: The URL of the website
    """

    with TheSession() as session:
        if not (
            website := session.query(WebsiteSource).filter(WebsiteSource.id == id).first()
        ):
            return Failed(message="Website not found")

        scraped_website = await scrape_website(url=website.url)
        website.contents = scraped_website["contents"]
        website.state = scraped_website["state"]
        session.commit()
        await reload_sources()

        if website.state != WebsiteSourceState.SCRAPED or not website.contents:
            return Completed(message="Website does not exist or is not available")

        scraped_meta = await extract_website_meta(
            base_url=f"{urlparse(website.url).scheme}://{urlparse(website.url).hostname}",
            contents=website.contents,
        )

        website.name = scraped_meta["name"]
        website.description = scraped_meta["description"]
        website.favicon = scraped_meta["favicon"]
        website.state = scraped_meta["state"]
        session.commit()
        await reload_sources()

        return Completed(
            message=f"Finished processing {website.url} with state {website.state}"
        )
