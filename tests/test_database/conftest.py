import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import users
from database.schemas import (
    Bank,
    BankSavings,
    UforaAnnouncement,
    UforaCourse,
    UforaCourseAlias,
    User,
)


@pytest.fixture(scope="session")
def test_user_id() -> int:
    """User id used when creating the debug user

    Fixture is useful when comparing, fetching data, ...
    """
    return 1


@pytest.fixture
async def user(postgres: AsyncSession, test_user_id: int) -> User:
    """Fixture to create a user"""
    _user = await users.get_or_add_user(postgres, test_user_id)
    await postgres.refresh(_user)
    return _user


@pytest.fixture
async def bank(postgres: AsyncSession, user: User) -> Bank:
    """Fixture to fetch the test user's bank"""
    _bank = user.bank
    await postgres.refresh(_bank)
    return _bank


@pytest.fixture
async def savings(postgres: AsyncSession, user: User) -> BankSavings:
    """Fixture to fetch the test user's savings account"""
    _savings = user.savings
    await postgres.refresh(_savings)
    return _savings


@pytest.fixture
async def ufora_course(postgres: AsyncSession) -> UforaCourse:
    """Fixture to create a course"""
    course = UforaCourse(name="test", code="code", year=1, log_announcements=True)
    postgres.add(course)
    await postgres.commit()
    return course


@pytest.fixture
async def ufora_course_with_alias(postgres: AsyncSession, ufora_course: UforaCourse) -> UforaCourse:
    """Fixture to create a course with an alias"""
    alias = UforaCourseAlias(course_id=ufora_course.course_id, alias="alias")
    postgres.add(alias)
    await postgres.commit()
    await postgres.refresh(ufora_course)
    return ufora_course


@pytest.fixture
async def ufora_announcement(postgres: AsyncSession, ufora_course: UforaCourse) -> UforaAnnouncement:
    """Fixture to create an announcement"""
    announcement = UforaAnnouncement(course_id=ufora_course.course_id, publication_date=datetime.datetime.now())
    postgres.add(announcement)
    await postgres.commit()
    return announcement
