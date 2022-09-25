from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.schemas import EasterEgg

__all__ = ["get_all_easter_eggs"]


async def get_all_easter_eggs(session: AsyncSession) -> list[EasterEgg]:
    """Return a list of all easter eggs"""
    statement = select(EasterEgg)
    return (await session.execute(statement)).scalars().all()
