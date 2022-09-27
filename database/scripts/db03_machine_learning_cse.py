from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import DBSession
from database.schemas import UforaCourse

__all__ = ["main"]


async def main():
    """Add a missing Ufora course (Machine Learning - CSE)"""
    session: AsyncSession
    async with DBSession() as session:
        mlcse = UforaCourse(
            code="E061330",
            name="Machine Learning (CSE)",
            role_id=1024355572256092170,
            overarching_role_id=1023300434800164914,
        )

        session.add(mlcse)
        await session.commit()
