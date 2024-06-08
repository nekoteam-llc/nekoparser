from psycopg2.extensions import register_adapter
from psycopg2.extras import Json
from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import config

SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="postgresql",
    username=config.db_user,
    host=config.db_host,
    password=config.db_password,
    port=config.db_port,
    database=config.db_name,
)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
metadata = MetaData(
    # https://stackoverflow.com/a/29153957
    naming_convention={
        "pk": "pk_%(table_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
    }
)
metadata.bind = engine  # pyright: ignore[reportAttributeAccessIssue]


class Base(DeclarativeBase):
    metadata = metadata


TheSession = sessionmaker(autocommit=False, autoflush=True, bind=engine)

# Automatically convert all dictionaries passed as parameters to JSON
# https://stackoverflow.com/a/55939024
register_adapter(dict, Json)
