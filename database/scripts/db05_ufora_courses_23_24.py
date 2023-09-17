from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import DBSession
from database.schemas import UforaCourse

__all__ = ["main"]


async def main():
    """Add the Ufora courses for the 2023-2024 academic year"""
    session: AsyncSession
    async with DBSession() as session:
        # Remove Advanced Databases (which no longer exists)
        stmt = select(UforaCourse).where(UforaCourse.code == "E018441")
        advanced_databases_course: Optional[UforaCourse] = (await session.execute(stmt)).scalar_one_or_none()

        await session.delete(advanced_databases_course)
        await session.commit()

        # TODO rest of courses when I know them
