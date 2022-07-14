from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import ufora_courses as crud
from database.models import UforaCourse


async def test_get_course_by_name_exact(database_session: AsyncSession, ufora_course: UforaCourse):
    """Test getting a course by its name when the query is an exact match"""
    match = await crud.get_course_by_name(database_session, "Test")
    assert match == ufora_course


async def test_get_course_by_name_substring(database_session: AsyncSession, ufora_course: UforaCourse):
    """Test getting a course by its name when the query is a substring"""
    match = await crud.get_course_by_name(database_session, "es")
    assert match == ufora_course


async def test_get_course_by_name_alias(database_session: AsyncSession, ufora_course_with_alias: UforaCourse):
    """Test getting a course by its name when the name doesn't match, but the alias does"""
    match = await crud.get_course_by_name(database_session, "ali")
    assert match == ufora_course_with_alias
