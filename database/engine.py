from urllib.parse import quote_plus

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import settings

encoded_postgres_password = quote_plus(settings.POSTGRES_PASS)

# PostgreSQL engine
postgres_engine = create_async_engine(
    URL.create(
        drivername="postgresql+asyncpg",
        username=settings.POSTGRES_USER,
        password=encoded_postgres_password,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
    ),
    pool_pre_ping=True,
    future=True,
)

DBSession = async_sessionmaker(autocommit=False, autoflush=False, bind=postgres_engine, expire_on_commit=False)
