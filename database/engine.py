from urllib.parse import quote_plus

import motor.motor_asyncio
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import settings

encoded_password = quote_plus(settings.POSTGRES_PASS)

# PostgreSQL engine
postgres_engine = create_async_engine(
    URL.create(
        drivername="postgresql+asyncpg",
        username=settings.POSTGRES_USER,
        password=encoded_password,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
    ),
    pool_pre_ping=True,
    future=True,
)

DBSession = sessionmaker(
    autocommit=False, autoflush=False, bind=postgres_engine, class_=AsyncSession, expire_on_commit=False
)

# MongoDB client
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_HOST, settings.MONGO_PORT)
