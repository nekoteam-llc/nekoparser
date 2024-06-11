import enum
import uuid

from sqlalchemy import DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import mapped_column

from ..database import Base

__all__ = ["WebsiteSource", "FileSource", "FileType", "Product"]


class WebsiteSourceState(enum.Enum):
    """
    Represents the state of the website source
    """

    CREATED = "created"
    UNAVAILABLE = "unavailable"
    SCRAPED = "scraped"
    XREFS_PENDING_APPROVAL = "xrefs_pending_approval"
    XREFS_APPROVED = "xrefs_approved"
    XREFS_DISCARDED = "xrefs_discarded"
    DATA_PENDING_APPROVAL = "data_pending_approval"
    DATA_DISCARDED = "data_discarded"
    DATA_APPROVED = "data_approved"


class WebsiteSource(Base):
    """
    Represents a data scraping source in the form of the website
    """

    __tablename__ = "website_source"

    id = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    url = mapped_column(Text, nullable=False)
    contents = mapped_column(Text, comment="The contents of the website")
    ui_name = mapped_column(Text, comment="Website title")
    ui_description = mapped_column(Text, comment="Website meta description")
    ui_image = mapped_column(Text, comment="Website meta image / favicon")
    product_card_xref = mapped_column(
        Text, comment="The cross-reference to the product card"
    )
    product_properties_mapping_xref = mapped_column(
        JSONB,
        comment="The dictionary which maps the Satu.kz fields to the website cross-references",
    )
    last_processed = mapped_column(
        DateTime,
        comment="The last time the website was processed",
    )
    state = mapped_column(
        Enum(WebsiteSourceState),
        nullable=False,
        default=WebsiteSourceState.CREATED,
        comment="The FSM state of the website source",
    )


class FileType(enum.Enum):
    """
    Represents the type of the file
    """

    CSV = "csv"
    XLSX = "xlsx"
    PDF = "pdf"


class FileSource(Base):
    """
    Represents a data scraping source in the form of the file
    """

    __tablename__ = "file_source"

    id = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    minio_uuid = mapped_column(
        UUID(as_uuid=False),
        comment="The UUID of the file in the MinIO storage",
    )
    file_type = mapped_column(Enum(FileType), nullable=False)
    file_metadata = mapped_column(
        JSONB,
        comment="The metadata of the file used to transform the data",
    )
    last_processed = mapped_column(
        DateTime,
        comment="The last time the file was processed",
    )


class Product(Base):
    """
    Represents a product
    """

    __tablename__ = "product"

    id = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    data = mapped_column(
        JSONB,
        comment="The data of the product for Satu.kz",
    )
    last_processed = mapped_column(
        DateTime,
        comment="The last time the product was processed",
    )
    source_id = mapped_column(
        UUID(as_uuid=False),
        comment="The UUID of the source",
    )
