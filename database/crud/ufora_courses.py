from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.schemas.relational import UforaCourse, UforaCourseAlias

__all__ = ["get_all_courses", "get_course_by_name"]


async def get_all_courses(session: AsyncSession) -> list[UforaCourse]:
    """Get a list of all courses in the database"""
    statement = select(UforaCourse)
    return list((await session.execute(statement)).scalars().all())


async def get_course_by_name(session: AsyncSession, query: str) -> Optional[UforaCourse]:
    """Try to find a course by its name

    This checks for regular name first, and then aliases
    """
    # Search case-insensitively
    query = query.lower()

    statement = select(UforaCourse).where(UforaCourse.name.ilike(f"%{query}%"))
    result = (await session.execute(statement)).scalars().first()
    if result:
        return result

    statement = select(UforaCourseAlias).where(UforaCourseAlias.alias.ilike(f"%{query}%"))
    result = (await session.execute(statement)).scalars().first()
    return result.course if result else None
