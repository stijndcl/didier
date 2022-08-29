from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import ufora_courses as crud
from database.schemas import UforaCourse


async def test_get_course_by_name_exact(postgres: AsyncSession, ufora_course: UforaCourse):
    """Test getting a course by its name when the query is an exact match"""
    match = await crud.get_course_by_name(postgres, "Test")
    assert match == ufora_course


async def test_get_course_by_name_substring(postgres: AsyncSession, ufora_course: UforaCourse):
    """Test getting a course by its name when the query is a substring"""
    match = await crud.get_course_by_name(postgres, "es")
    assert match == ufora_course


async def test_get_course_by_name_alias(postgres: AsyncSession, ufora_course_with_alias: UforaCourse):
    """Test getting a course by its name when the name doesn't match, but the alias does"""
    match = await crud.get_course_by_name(postgres, "ali")
    assert match == ufora_course_with_alias
