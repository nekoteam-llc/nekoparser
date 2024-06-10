# pyright: reportUnusedCoroutine=false, reportFunctionMemberAccess=false, reportArgumentType=false
"""Deploys everything to prefect. Run with `python3 -m transformations`"""

import logging

from prefect import serve

from .sample.pipeline import sample_pipeline


def serve_all():
    """
    Serves all the flows
    """

    logging.getLogger("httpx").setLevel(logging.WARNING)

    serve(
        sample_pipeline.to_deployment(
            name="sample_pipeline",
            tags=["sample"],
            cron="*/15 * * * *",
        ),
    )
