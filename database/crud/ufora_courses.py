from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.schemas import UforaCourse, UforaCourseAlias

__all__ = ["get_all_courses", "get_course_by_code", "get_course_by_name"]


async def get_all_courses(session: AsyncSession) -> list[UforaCourse]:
    """Get a list of all courses in the database"""
    statement = select(UforaCourse)
    return list((await session.execute(statement)).scalars().all())


async def get_course_by_code(session: AsyncSession, code: str) -> Optional[UforaCourse]:
    """Try to find a course by its code"""
    statement = select(UforaCourse).where(UforaCourse.code == code)
    return (await session.execute(statement)).scalar_one_or_none()


async def get_course_by_name(session: AsyncSession, query: str) -> Optional[UforaCourse]:
    """Try to find a course by its name

    This checks for regular name first, and then aliases
    """
    # Search case-insensitively
    query = query.lower()

    course_statement = select(UforaCourse).where(UforaCourse.name.ilike(f"%{query}%"))
    course_result = (await session.execute(course_statement)).scalars().first()
    if course_result:
        return course_result

    alias_statement = select(UforaCourseAlias).where(UforaCourseAlias.alias.ilike(f"%{query}%"))
    alias_result = (await session.execute(alias_statement)).scalars().first()
    return alias_result.course if alias_result else None
