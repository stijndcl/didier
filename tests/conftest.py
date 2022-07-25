import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import engine
from database.migrations import ensure_latest_migration, migrate
from didier import Didier


@pytest.fixture(scope="session", autouse=True)
def event_loop() -> Generator:
    """Fixture to change the event loop

    This fixes a lot of headaches during async tests
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def tables():
    """Fixture to initialize a database before the tests, and then tear it down again

    Checks that the migrations were successful by asserting that we are currently
    on the latest migration
    """
    await migrate(up=True)
    await ensure_latest_migration()
    yield
    await migrate(up=False)


@pytest.fixture
async def postgres(tables) -> AsyncGenerator[AsyncSession, None]:
    """Fixture to create a session for every test

    Rollbacks the transaction afterwards so that the future tests start with a clean database
    """
    connection = await engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)

    yield session

    # Clean up session & rollback transactions
    await session.close()
    if transaction.is_valid:
        await transaction.rollback()

    await connection.close()


@pytest.fixture
def mock_client() -> Didier:
    """Fixture to get a mock Didier instance

    The mock uses 0 as the id
    """
    mock_client = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 0
    mock_client.user = mock_user

    return mock_client
