from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from packages.database import TheSession, WebsiteSource, WebsiteSourceState
from packages.schemas.satu import UserFilledData
from transformations.websites import connector

from ..sources.source_manager import source_manager

router = APIRouter(
    prefix="/api/v1/connector",
    tags=["connector"],
)


class ConnectorSource(BaseModel):
    id: str
    domain: str


class ConnectorSourcesResponse(BaseModel):
    sources: list[ConnectorSource]


class SourceUpdateResponse(BaseModel):
    message: str


class RegExesInput(BaseModel):
    product: str
    pagination: str


class Property(BaseModel):
    name: str
    description: str


class PropertiesResponse(BaseModel):
    properties: list[Property]


class PropertyInput(BaseModel):
    property: str
    xpath: str


class SourceUpdateInput(BaseModel):
    xpaths: list[PropertyInput]
    regexes: RegExesInput


@router.get("/sources")
async def get_active_sources() -> ConnectorSourcesResponse:
    """
    Get the list of websites for which the connector should be activated.
    """

    with TheSession() as session:
        sources = (
            session.query(WebsiteSource.id, WebsiteSource.url)
            .filter(WebsiteSource.state == WebsiteSourceState.XPATHS_PENDING)
            .all()
        )

        return ConnectorSourcesResponse(
            sources=[
                ConnectorSource(id=id, domain=urlparse(url).hostname)
                for id, url in sources
            ]
        )


@router.get("/properties")
async def get_properties() -> PropertiesResponse:
    """
    Get the list of available properties of the product.
    """

    return PropertiesResponse(
        properties=[
            Property(name=field_name, description=field_info.description or field_name)
            for field_name, field_info in UserFilledData.model_fields.items()
        ]
    )


@router.post("/sources/{source_id}")
async def update_source_xpaths(
    source_id: str,
    data: SourceUpdateInput,
) -> SourceUpdateResponse:
    """
    Update the cross-references for the source.
    """

    with TheSession() as session:
        if not (
            source := session.query(WebsiteSource)
            .filter(WebsiteSource.id == source_id)
            .first()
        ):
            raise HTTPException(status_code=404, detail="Source not found")

        source.props_xpaths = {prop.property: prop.xpath for prop in data.xpaths}
        source.product_regex = data.regexes.product
        source.pagination_regex = data.regexes.pagination
        source.state = WebsiteSourceState.XPATHS_READY
        session.commit()

    await source_manager.reload_sources()
    await connector.schedule_data_collection(source_id)

    return SourceUpdateResponse(message="XPATHs updated")
