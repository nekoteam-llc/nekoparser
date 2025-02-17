# pyright: reportUnusedCoroutine=false, reportFunctionMemberAccess=false, reportArgumentType=false
"""Deploys everything to prefect. Run with `python3 -m transformations`"""

from prefect import serve

from .excel.pipeline import excel_processing
from .websites.pipeline import extract_products, initial_processing, reprocess_products


def serve_all():
    """
    Serves all the flows
    """

    serve(
        initial_processing.to_deployment(
            name=initial_processing.name,
            tags=["websites"],
        ),
        extract_products.to_deployment(
            name=extract_products.name,
            tags=["websites"],
        ),
        reprocess_products.to_deployment(
            name=reprocess_products.name,
            tags=["websites"],
        ),
        excel_processing.to_deployment(
            name=excel_processing.name,
            tags=["excel"],
        ),
    )
