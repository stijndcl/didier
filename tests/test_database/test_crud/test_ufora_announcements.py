import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import ufora_announcements as crud
from database.models import UforaAnnouncement, UforaCourse


async def test_get_courses_with_announcements_none(database_session: AsyncSession):
    """Test getting all courses with announcements when there are none"""
    results = await crud.get_courses_with_announcements(database_session)
    assert len(results) == 0


async def test_get_courses_with_announcements(database_session: AsyncSession):
    """Test getting all courses with announcements"""
    course_1 = UforaCourse(name="test", code="code", year=1, log_announcements=True)
    course_2 = UforaCourse(name="test2", code="code2", year=1, log_announcements=False)
    database_session.add_all([course_1, course_2])
    await database_session.commit()

    results = await crud.get_courses_with_announcements(database_session)
    assert len(results) == 1
    assert results[0] == course_1


async def test_create_new_announcement(ufora_course: UforaCourse, database_session: AsyncSession):
    """Test creating a new announcement"""
    await crud.create_new_announcement(
        database_session, 1, course=ufora_course, publication_date=datetime.datetime.now()
    )
    await database_session.refresh(ufora_course)
    assert len(ufora_course.announcements) == 1


async def test_remove_old_announcements(ufora_announcement: UforaAnnouncement, database_session: AsyncSession):
    """Test removing all stale announcements"""
    course = ufora_announcement.course
    ufora_announcement.publication_date -= datetime.timedelta(weeks=2)
    announcement_2 = UforaAnnouncement(course_id=ufora_announcement.course_id, publication_date=datetime.datetime.now())
    database_session.add_all([ufora_announcement, announcement_2])
    await database_session.commit()
    await database_session.refresh(course)
    assert len(course.announcements) == 2

    await crud.remove_old_announcements(database_session)

    await database_session.refresh(course)
    assert len(course.announcements) == 1
    assert announcement_2.course.announcements[0] == announcement_2
