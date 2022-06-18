from urllib.parse import quote_plus

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import settings

# Run local tests against SQLite instead of Postgres
if settings.TESTING and settings.DB_TEST_SQLITE:
    engine = create_async_engine(
        URL.create(
            drivername="sqlite+aiosqlite",
            database="tests.db",
        ),
        connect_args={"check_same_thread": False},
    )
else:
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
    )

DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)
