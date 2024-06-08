import asyncio
import json
from typing import Optional
from urllib.parse import urlparse

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from packages.database import Product, TheSession, WebsiteSource


class Source(BaseModel):
    id: str
    url: str
    title: str
    description: str
    icon: str
    state: str


class SourceManager:
    def __init__(self):
        self._active_connections: list[WebSocket] = []
        self._sources = []

        asyncio.create_task(self._ocassional_reloads())

    async def reload_sources(self):
        """
        Update the sources
        Should be called when the changes to any of the sources occur
        """

        with TheSession() as session:
            sources = session.query(WebsiteSource).all()
            self._sources = [
                Source(
                    id=source.id,
                    url=source.url,
                    title=source.name or urlparse(source.url).hostname,
                    description=(
                        source.description
                        or "🐻 Bear with us while we are waiting for the website description."
                    ),
                    icon=(
                        source.favicon or "https://cataas.com/cat?width=100&height=100"
                    ),
                    state=source.state.value,
                )
                for source in sources
            ]

        for connection in self._active_connections:
            await connection.send_text(json.dumps(jsonable_encoder(self._sources)))

    def get_source(self, id: str) -> Optional[Source]:
        """
        Get the source by id

        :param id: The ID of the source
        :return: The source or None
        """

        return next((source for source in self._sources if source.id == id), None)

    async def handle_connection(self, connection: WebSocket):
        """
        Handle the connection

        :param connection: The WebSocket connection
        """

        self._active_connections.append(connection)
        await connection.send_text(json.dumps(jsonable_encoder(self._sources)))

        try:
            while True:
                await connection.receive_text()
        except WebSocketDisconnect:
            self._active_connections.remove(connection)

    async def handle_data_connection(self, source_id: str, connection: WebSocket):
        """
        Handle the connection

        :param connection: The WebSocket connection
        """

        try:
            while True:
                await connection.send_text(
                    json.dumps(jsonable_encoder(self._get_products(source_id)))
                )
                await asyncio.sleep(2)
        except WebSocketDisconnect:
            pass

    def _get_products(self, source_id: str) -> Optional[list[Product]]:
        """
        Get the products by source id

        :param id: The ID of the source
        :return: The products or None
        """
        with TheSession() as session:
            return session.query(Product).filter(Product.source_id == source_id).all()

    async def _ocassional_reloads(self):
        """
        Reload the sources occasionally
        """

        while True:
            await self.reload_sources()
            await asyncio.sleep(5)


source_manager = SourceManager()
