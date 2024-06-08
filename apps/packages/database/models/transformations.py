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

    # The site has just been added to the database
    CREATED = "created"

    # The scraping has been attempted and the non 2xx response was received
    UNAVAILABLE = "unavailable"

    # The website has been successfully scraped and is awaiting XPATHs extraction
    SCRAPED = "scraped"

    # Waiting for user to select XPATHs
    XPATHS_PENDING = "xpaths_pending"

    # User selected XPATHs and the data is to be collected
    XPATHS_READY = "xpaths_ready"

    # The data is being collected
    DATA_COLLECTING = "data_collecting"

    # The data is awaiting approval
    DATA_PENDING_APPROVAL = "data_pending_approval"

    # The data has been approved
    FINISHED = "finished"

    # Exporting to Satu.kz
    EXPORTING = "exporting"

    # Export complete
    EXPORTED = "exported"


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
    name = mapped_column(Text, comment="Website title")
    description = mapped_column(Text, comment="Website meta description")
    favicon = mapped_column(Text, comment="Website favicon")
    product_regex = mapped_column(
        Text,
        comment="Regex that matches the product URLs on the website",
    )
    pagination_regex = mapped_column(
        Text,
        comment="Regex that matches the pagination URLs on the website",
    )
    props_xpaths = mapped_column(
        JSONB,
        comment="Mapping between the website properties and the XPATHs",
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
    url = mapped_column(
        Text,
        nullable=False,
        comment="The URL of the product",
    )
    hash = mapped_column(
        Text,
        nullable=False,
        comment="The hash of the product",
        unique=True,
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
