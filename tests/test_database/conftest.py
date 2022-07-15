import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UforaAnnouncement, UforaCourse, UforaCourseAlias


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
