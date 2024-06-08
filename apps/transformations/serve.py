# pyright: reportUnusedCoroutine=false, reportFunctionMemberAccess=false, reportArgumentType=false
"""Deploys everything to prefect. Run with `python3 -m transformations`"""

from prefect import serve

from .websites.pipeline import extract_products, initial_processing


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
    )
