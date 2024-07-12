import enum
import uuid

from sqlalchemy import Boolean, DateTime, Enum, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import mapped_column

from ..database import Base

__all__ = [
    "WebsiteSource",
    "ExcelSource",
    "Product",
    "ExcelSourceState",
    "WebsiteSourceState",
    "Config",
]


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


class ExcelSourceState(enum.Enum):
    """
    Represents the state of the Excel source
    """

    # The file has just been added to the database
    CREATED = "created"

    # The file is being processed
    PROCESSING = "processing"

    # The file has been processed
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


class ExcelSource(Base):
    """
    Represents a data scraping source in the form of the .xlsx file
    """

    __tablename__ = "xlsx_source"

    id = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    filename = mapped_column(
        Text,
        nullable=False,
        comment="The name of the file",
    )
    minio_uuid = mapped_column(
        UUID(as_uuid=False),
        comment="The UUID of the file in the MinIO storage",
    )
    column_mapping = mapped_column(
        JSONB,
        comment="The mapping between the file columns and the Satu fields",
    )
    last_processed = mapped_column(
        DateTime,
        comment="The last time the file was processed",
    )
    state = mapped_column(
        Enum(ExcelSourceState),
        nullable=False,
        default=ExcelSourceState.CREATED,
        comment="The FSM state of the Excel source",
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
    reprocessing = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="Whether the product is being reprocessed",
    )


class Config(Base):
    """
    Represents the configuration
    """

    __tablename__ = "config"

    id = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    chatgpt_key = mapped_column(
        Text,
        nullable=False,
        comment="The ChatGPT API key",
    )
    model = mapped_column(
        Text,
        nullable=False,
        comment="The model to use for the ChatGPT",
    )
    pages_concurrency = mapped_column(
        Integer,
        nullable=False,
        comment="The number of concurrent pages to scrape",
    )
    products_concurrency = mapped_column(
        Integer,
        nullable=False,
        comment="The number of concurrent products to scrape",
    )
    required = mapped_column(
        JSONB,
        nullable=False,
        comment="The required fields for the product",
    )
    not_reprocess = mapped_column(
        JSONB,
        nullable=False,
        comment="The fields that should not be reprocessed",
    )
    description_prompt = mapped_column(
        Text,
        nullable=False,
        comment="The prompt for the description",
    )
    keywords_prompt = mapped_column(
        Text,
        nullable=False,
        comment="The prompt for the keywords",
    )
    properties_prompt = mapped_column(
        Text,
        nullable=False,
        comment="The prompt for the properties",
    )
