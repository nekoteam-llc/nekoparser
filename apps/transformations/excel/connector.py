# pyright: reportGeneralTypeIssues=false
from typing import Optional
from uuid import UUID

from prefect import get_client

from ..global_connector import connector
from .pipeline import excel_processing

__all__ = ["schedule_excel_processing"]


async def schedule_excel_processing(id: str) -> Optional[str]:
    """
    Schedules the initial processing of the Excel file

    :param id: The ID of the Excel file
    :return: The flow run ID or None
    """

    if not (deployment_id := await connector.get_deployment_id(excel_processing.name)):
        return

    async with get_client() as client:
        flow_run_id = await client.create_flow_run_from_deployment(
            deployment_id=UUID(deployment_id),
            parameters={"id": id},
        )

    return flow_run_id
