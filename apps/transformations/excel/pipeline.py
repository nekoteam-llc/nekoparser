from typing import Optional

from prefect import flow

__all__ = ["excel_processing"]


@flow(name="Excel Processing", log_prints=True)
async def excel_processing(id: str) -> Optional[str]:
    """
    Processes the Excel file

    :param id: The ID of the Excel file
    :return: The flow run ID or None
    """

    raise NotImplementedError
