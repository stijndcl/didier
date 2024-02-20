from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.schemas import Jail

__all__ = ["get_jail", "get_user_jail", "imprison"]


async def get_jail(session: AsyncSession) -> list[Jail]:
    """Get the entire Didier Jail"""
    statement = select(Jail)
    return list((await session.execute(statement)).scalars().all())


async def get_user_jail(session: AsyncSession, user_id: int) -> Optional[Jail]:
    """Check how long a given user is still in jail for"""
    statement = select(Jail).where(Jail.user_id == user_id)
    return (await session.execute(statement)).scalar_one_or_none()


async def imprison(session: AsyncSession, user_id: int, until: datetime):
    """Put a user in Didier Jail"""
    jail = Jail(user_id=user_id, until=until)
    session.add(jail)
    await session.commit()
