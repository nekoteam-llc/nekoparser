from typing import Union
from urllib.parse import urlparse

from fastapi import APIRouter, File, HTTPException, UploadFile, WebSocket
from pydantic import BaseModel

from packages.database import (
    ExcelSource,
    ExcelSourceState,
    Product,
    TheSession,
    WebsiteSource,
)
from packages.filestorage import filestorage
from transformations.excel.connector import schedule_excel_processing
from transformations.websites.connector import (
    schedule_initial_processing,
    schedule_reprocessing,
)

from .source_manager import ExcelSourceModel, WebsiteSourceModel, source_manager

router = APIRouter(
    prefix="/api/v1/sources",
    tags=["sources"],
)


class SourcesResponse(BaseModel):
    sources: list[WebsiteSourceModel]


class SourceCreateResponse(BaseModel):
    id: str


class MessageResponse(BaseModel):
    message: str


class ReprocessRequest(BaseModel):
    products: list[str]


@router.get("/")
async def get_sources() -> SourcesResponse:
    """
    Get the sources
    """

    with TheSession() as session:
        sources = session.query(WebsiteSource).all()

        return SourcesResponse(
            sources=[
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
async def get_source(source_id: str) -> Union[WebsiteSourceModel, ExcelSourceModel]:
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
        if session.query(WebsiteSource).filter(WebsiteSource.id == source_id).first():
            session.query(WebsiteSource).filter(WebsiteSource.id == source_id).delete()
        elif session.query(ExcelSource).filter(ExcelSource.id == source_id).first():
            session.query(ExcelSource).filter(ExcelSource.id == source_id).delete()
            filestorage.delete(source_id)
        else:
            raise HTTPException(status_code=404, detail="Source not found")

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


@router.post("/reprocess")
async def reprocess_products(data: ReprocessRequest) -> MessageResponse:
    """
    Reprocess the products
    """

    with TheSession() as session:
        for product_id in data.products:
            if not (
                product := session.query(Product).filter(Product.id == product_id).first()
            ):
                raise HTTPException(status_code=404, detail="Product not found")

            product.reprocessing = True

        session.commit()
        await source_manager.reload_sources()

    await schedule_reprocessing()

    return MessageResponse(message="Scheduled.")


@router.websocket("/wss")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await source_manager.handle_connection(websocket)


@router.websocket("/wss/{source_id}/data")
async def websocket_data_endpoint(websocket: WebSocket, source_id: str):
    await websocket.accept()
    await source_manager.handle_data_connection(source_id, websocket)


@router.post("/excel")
async def upload_excel_file(file: UploadFile = File(...)) -> SourceCreateResponse:
    """
    Upload an Excel file and add it to the database
    """

    file_bytes = await file.read()
    minio_uuid = filestorage.upload(file_bytes)

    with TheSession() as session:
        excel_source = ExcelSource(
            minio_uuid=minio_uuid,
            filename=file.filename,
            state=ExcelSourceState.CREATED,
        )
        session.add(excel_source)
        session.commit()
        await source_manager.reload_sources()
        await schedule_excel_processing(excel_source.id)

    return SourceCreateResponse(id=excel_source.id)
