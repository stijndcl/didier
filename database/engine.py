from urllib.parse import quote_plus

import motor.motor_asyncio
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

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

DBSession = sessionmaker(
    autocommit=False, autoflush=False, bind=postgres_engine, class_=AsyncSession, expire_on_commit=False
)

# MongoDB client
if not settings.TESTING:
    encoded_mongo_username = quote_plus(settings.MONGO_USER)
    encoded_mongo_password = quote_plus(settings.MONGO_PASS)
    mongo_url = (
        f"mongodb://{encoded_mongo_username}:{encoded_mongo_password}@{settings.MONGO_HOST}:{settings.MONGO_PORT}/"
    )
else:
    # Require no authentication when testing
    mongo_url = f"mongodb://{settings.MONGO_HOST}:{settings.MONGO_PORT}/"

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
