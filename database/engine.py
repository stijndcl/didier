from urllib.parse import quote_plus

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import settings

encoded_password = quote_plus(settings.DB_PASSWORD)
engine = create_async_engine(
    URL.create(
        drivername="postgresql+asyncpg",
        username=settings.DB_USERNAME,
        password=encoded_password,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
    ),
    pool_pre_ping=True,
    future=True,
)

DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)
