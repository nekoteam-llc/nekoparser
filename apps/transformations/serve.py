# pyright: reportUnusedCoroutine=false, reportFunctionMemberAccess=false, reportArgumentType=false
"""Deploys everything to prefect. Run with `python3 -m transformations`"""

from prefect import serve

from .websites.pipeline import process_websites


def serve_all():
    """
    Serves all the flows
    """

    serve(
        process_websites.to_deployment(
            name="Process Websites",
            tags=["websites"],
        ),
    )
