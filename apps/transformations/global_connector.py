# pyright: reportGeneralTypeIssues=false
import asyncio
from typing import Optional

from prefect import get_client


class PrefectConnector:
    def __init__(self):
        self._deployments: Optional[dict[str, str]] = None

        asyncio.create_task(self._sync_loop())

    async def _fetch_available_deployments(self):
        """
        Fetch all available deployments
        """

        async with get_client() as client:
            deployments = await client.read_deployments()

        self._deployments = {
            deployment.name: str(deployment.id) for deployment in deployments
        }

    async def _sync_loop(self):
        """
        Sync loop
        """

        while True:
            await self._fetch_available_deployments()
            await asyncio.sleep(60)

    async def get_deployment_id(self, name: str) -> Optional[str]:
        """
        Get the deployment ID by the name
        """

        if not self._deployments:
            await self._fetch_available_deployments()

        if not self._deployments:
            return

        return self._deployments.get(name)


connector = PrefectConnector()
