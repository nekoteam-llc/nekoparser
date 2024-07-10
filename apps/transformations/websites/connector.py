# pyright: reportGeneralTypeIssues=false
from typing import Optional
from uuid import UUID

from prefect import get_client

from ..global_connector import connector
from .pipeline import extract_products, initial_processing, reprocess_products


async def schedule_initial_processing(id: str) -> Optional[str]:
    """
    Schedules the initial processing of the website

    :param id: The ID of the website
    :return: The flow run ID or None
    """

    if not (deployment_id := await connector.get_deployment_id(initial_processing.name)):
        return

    async with get_client() as client:
        flow_run_id = await client.create_flow_run_from_deployment(
            deployment_id=UUID(deployment_id),
            parameters={"id": id},
        )

    return flow_run_id


async def schedule_data_collection(id: str) -> Optional[str]:
    """
    Schedules the data collection of the website

    :param id: The ID of the website
    :return: The flow run ID or None
    """

    if not (deployment_id := await connector.get_deployment_id(extract_products.name)):
        return

    async with get_client() as client:
        flow_run_id = await client.create_flow_run_from_deployment(
            deployment_id=UUID(deployment_id),
            parameters={"id": id},
        )

    return flow_run_id


async def schedule_reprocessing() -> Optional[str]:
    """
    Schedules the reprocessing of the products

    :return: The flow run ID or None
    """

    if not (deployment_id := await connector.get_deployment_id(reprocess_products.name)):
        return

    async with get_client() as client:
        flow_run_id = await client.create_flow_run_from_deployment(
            deployment_id=UUID(deployment_id),
        )

    return flow_run_id
