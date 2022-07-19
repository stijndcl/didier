import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import users
from database.models import Bank, UforaAnnouncement, UforaCourse, UforaCourseAlias, User


@pytest.fixture(scope="session")
def test_user_id() -> int:
    """User id used when creating the debug user

    Fixture is useful when comparing, fetching data, ...
    """
    return 1


@pytest.fixture
async def user(database_session: AsyncSession, test_user_id) -> User:
    """Fixture to create a user"""
    _user = await users.get_or_add(database_session, test_user_id)
    await database_session.refresh(_user)
    return _user


@pytest.fixture
async def bank(database_session: AsyncSession, user: User) -> Bank:
    """Fixture to fetch the test user's bank"""
    _bank = user.bank
    await database_session.refresh(_bank)
    return _bank


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
