import asyncio
import datetime
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import engine
from database.models import Base, UforaAnnouncement, UforaCourse, UforaCourseAlias
from didier import Didier

"""General fixtures"""


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def tables():
    """Initialize a database before the tests, and then tear it down again"""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


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


"""Fixtures to put fake data in the database"""


@pytest.fixture
async def ufora_course(database_session: AsyncSession) -> UforaCourse:
    """Fixture to create a course"""
    course = UforaCourse(name="test", code="code", year=1, log_announcements=True)
    database_session.add(course)
    await database_session.commit()
    return course


@pytest.fixture
async def ufora_course_with_alias(database_session: AsyncSession, ufora_course: UforaCourse) -> UforaCourse:
    """Fixture to create a course with an alias"""
    alias = UforaCourseAlias(course_id=ufora_course.course_id, alias="alias")
    database_session.add(alias)
    await database_session.commit()
    await database_session.refresh(ufora_course)
    return ufora_course


@pytest.fixture
async def ufora_announcement(ufora_course: UforaCourse, database_session: AsyncSession) -> UforaAnnouncement:
    """Fixture to create an announcement"""
    announcement = UforaAnnouncement(course_id=ufora_course.course_id, publication_date=datetime.datetime.now())
    database_session.add(announcement)
    await database_session.commit()
    return announcement
