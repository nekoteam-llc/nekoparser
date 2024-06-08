from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, WebSocket
from pydantic import BaseModel

from packages.database import TheSession, WebsiteSource
from transformations.websites.connector import schedule_initial_processing

from .source_manager import Source, source_manager

router = APIRouter(
    prefix="/api/v1/sources",
    tags=["sources"],
)


class SourcesResponse(BaseModel):
    sources: list[Source]


class SourceCreateResponse(BaseModel):
    id: str


class MessageResponse(BaseModel):
    message: str


@router.get("/")
async def get_sources() -> SourcesResponse:
    """
    Get the sources
    """

    with TheSession() as session:
        sources = session.query(WebsiteSource).all()

        return SourcesResponse(
            sources=[
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
        )


@router.post("/")
async def create_source(url: str) -> SourceCreateResponse:
    """
    Create the source
    """

    with TheSession() as session:
        website_source = WebsiteSource(url=url)
        session.add(website_source)
        session.commit()
        await source_manager.reload_sources()

        await schedule_initial_processing(website_source.id)
        return SourceCreateResponse(id=website_source.id)


@router.get("/{source_id}")
async def get_source(source_id: str) -> Source:
    """
    Get the source by id
    """

    if not (source := source_manager.get_source(source_id)):
        raise HTTPException(status_code=404, detail="Source not found")

    return source


@router.delete("/{source_id}")
async def delete_source(source_id: str) -> MessageResponse:
    """
    Delete the source by id
    """

    if not source_manager.get_source(source_id):
        raise HTTPException(status_code=404, detail="Source not found")

    with TheSession() as session:
        session.query(WebsiteSource).filter(WebsiteSource.id == source_id).delete()
        session.commit()
        await source_manager.reload_sources()

    return MessageResponse(message="The source has been deleted")


@router.post("/reload")
async def reload_sources() -> MessageResponse:
    """
    Reload the sources
    """

    await source_manager.reload_sources()
    return MessageResponse(message="The sources have been reloaded")


@router.websocket("/wss")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await source_manager.handle_connection(websocket)


@router.websocket("/wss/{source_id}/data")
async def websocket_data_endpoint(websocket: WebSocket, source_id: str):
    await websocket.accept()
    await source_manager.handle_data_connection(source_id, websocket)
