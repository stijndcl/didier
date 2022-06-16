import os
from typing import AsyncGenerator

import pytest

from alembic import command, config
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import engine


@pytest.fixture(scope="session")
def tables():
    """Initialize a database before the tests, and then tear it down again
    Starts from an empty database and runs through all the migrations to check those as well
    while we're at it
    """
    print("CWD: ", os.getcwd())
    print("Contents: ", list(os.listdir(os.getcwd())))
    alembic_config = config.Config("alembic.ini")
    command.upgrade(alembic_config, "head")
    yield
    command.downgrade(alembic_config, "base")


@pytest.fixture
async def database_session(tables) -> AsyncGenerator[AsyncSession, None]:
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
