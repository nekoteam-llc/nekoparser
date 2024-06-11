from prefect import flow

from .tasks import extract_website_meta_many, scrape_websites


@flow(name="Process websites", log_prints=True)
async def process_websites():
    """
    Process the websites
    """

    await scrape_websites()
    await extract_website_meta_many()
