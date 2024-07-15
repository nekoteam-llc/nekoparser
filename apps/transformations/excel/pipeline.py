import asyncio
from typing import Optional

from prefect import flow
from sqlalchemy.dialects.postgresql import insert

from packages.database import Config, ExcelSource, ExcelSourceState, Product, TheSession
from transformations.utils import reload_sources

from .tasks import enrich_product, initial_excel_processing

__all__ = ["excel_processing"]


@flow(name="Excel Processing", log_prints=True)
async def excel_processing(id: str) -> Optional[str]:
    """
    Processes the Excel file

    :param id: The ID of the Excel file
    :return: The flow run ID or None
    """

    with TheSession() as session:
        if not (
            excel_source := session.query(ExcelSource)
            .filter(ExcelSource.id == id)
            .first()
        ):
            raise ValueError("Excel source not found")

        excel_source.state = ExcelSourceState.EXTRACTING_SKUS
        session.commit()
        await reload_sources()

        products = await initial_excel_processing(id)

        insert_stmt = insert(Product).values(products)
        insert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=["hash"],
            set_={
                "data": insert_stmt.excluded.data,
                "url": insert_stmt.excluded.url,
                "last_processed": insert_stmt.excluded.last_processed,
                "source_id": insert_stmt.excluded.source_id,
                "reprocessing": insert_stmt.excluded.reprocessing,
            },
        )
        session.execute(insert_stmt)

        excel_source.state = ExcelSourceState.SKUS_EXTRACTED
        session.commit()
        await reload_sources()

        global_config = session.query(Config).one()

        chunked_products = [
            products[i : i + global_config.products_concurrency]
            for i in range(0, len(products), global_config.products_concurrency)
        ]

        excel_source.state = ExcelSourceState.PROCESSING
        session.commit()

        product_hashes = [product["hash"] for product in products]
        exists = (
            session.query(Product.hash).filter(Product.hash.in_(product_hashes)).all()
        )

        results = []
        for chunk in chunked_products:
            results.extend(
                await asyncio.gather(
                    *[
                        enrich_product(
                            product["data"]["sku"],
                            exists=product["hash"] in exists,
                        )
                        for product in chunk
                    ]
                )
            )

        for sku, data in results:
            for product in products:
                if product["data"]["sku"] == sku:
                    for key, value in data.items():
                        product["data"].setdefault(key, value)
                    break

        for product in products:
            product["reprocessing"] = False

        insert_stmt = insert(Product).values(
            list(filter(lambda x: x["data"].get("name"), products))
        )
        insert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=["hash"],
            set_={
                "data": insert_stmt.excluded.data,
                "url": insert_stmt.excluded.url,
                "last_processed": insert_stmt.excluded.last_processed,
                "source_id": insert_stmt.excluded.source_id,
                "reprocessing": insert_stmt.excluded.reprocessing,
            },
        )
        session.execute(insert_stmt)

        excel_source.state = ExcelSourceState.DATA_PENDING_APPROVAL
        session.commit()
        await reload_sources()
