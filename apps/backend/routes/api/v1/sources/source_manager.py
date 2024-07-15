import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional, Union
from urllib.parse import urlparse

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from packages.database import ExcelSource, Product, TheSession, WebsiteSource
from packages.filestorage import filestorage


class WebsiteSourceModel(BaseModel):
    id: str
    url: str
    title: str
    description: str
    icon: str
    state: str
    type: str


class ExcelSourceModel(BaseModel):
    id: str
    filename: str
    state: str
    type: str
    url: str


class SourceManager:
    def __init__(self):
        self._active_connections: list[WebSocket] = []
        self._web_sources: list[WebsiteSourceModel] = []
        self._excel_sources: list[ExcelSourceModel] = []

        asyncio.create_task(self._ocassional_reloads())

    async def reload_sources(self):
        """
        Update the sources
        Should be called when the changes to any of the sources occur
        """

        with TheSession() as session:
            web_sources = (
                session.query(WebsiteSource).order_by(WebsiteSource.url.desc()).all()
            )
            excel_sources = (
                session.query(ExcelSource).order_by(ExcelSource.id.desc()).all()
            )
            self._web_sources = [
                WebsiteSourceModel(
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
                    type="web",
                )
                for source in web_sources
            ]

            for source in excel_sources:
                if not source.url_expires or source.url_expires < datetime.now():
                    source.url = filestorage.get_url(source.filename)
                    source.url_expires = datetime.now() + timedelta(days=7)
                    session.commit()

            self._excel_sources = [
                ExcelSourceModel(
                    id=source.id,
                    filename=source.filename,
                    state=source.state.value,
                    type="excel",
                    url=source.url,
                )
                for source in excel_sources
            ]

        for connection in self._active_connections:
            await connection.send_text(
                json.dumps(
                    jsonable_encoder(
                        {
                            "web_sources": self._web_sources,
                            "excel_sources": self._excel_sources,
                        }
                    )
                )
            )

    def get_source(
        self,
        id: str,
    ) -> Optional[Union[WebsiteSourceModel, ExcelSourceModel]]:
        """
        Get the source by id

        :param id: The ID of the source
        :return: The source or None
        """

        return next(
            (
                source
                for source in (self._web_sources + self._excel_sources)
                if source.id == id
            ),
            None,
        )

    async def handle_connection(self, connection: WebSocket):
        """
        Handle the connection

        :param connection: The WebSocket connection
        """

        self._active_connections.append(connection)
        await self.reload_sources()

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
            return (
                session.query(Product)
                .filter(Product.source_id == source_id)
                .order_by(Product.url.desc())
                .all()
            )

    async def _ocassional_reloads(self):
        """
        Reload the sources occasionally
        """

        while True:
            await self.reload_sources()
            await asyncio.sleep(5)


source_manager = SourceManager()
