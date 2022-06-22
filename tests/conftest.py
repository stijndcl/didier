import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock

import pytest

from alembic import command, config
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import engine
from didier import Didier


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def tables(event_loop):
    """Initialize a database before the tests, and then tear it down again
    Starts from an empty database and runs through all the migrations to check those as well
    while we're at it
    """
    alembic_config = config.Config("alembic.ini")
    command.upgrade(alembic_config, "head")
    yield
    command.downgrade(alembic_config, "base")


@pytest.fixture
async def database_session(tables, event_loop) -> AsyncGenerator[AsyncSession, None]:
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
