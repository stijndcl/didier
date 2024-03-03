from datetime import datetime
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.schemas import Jail

__all__ = [
    "get_jail",
    "get_jail_entry_by_id",
    "get_next_jail_release",
    "get_user_jail",
    "imprison",
    "delete_prisoner_by_id",
]


async def get_jail(session: AsyncSession) -> list[Jail]:
    """Get the entire Didier Jail"""
    statement = select(Jail)
    return list((await session.execute(statement)).scalars().all())


async def get_jail_entry_by_id(session: AsyncSession, jail_id: int) -> Optional[Jail]:
    """Get a jail entry by its id"""
    statement = select(Jail).where(Jail.jail_entry_id == jail_id)
    return (await session.execute(statement)).scalar_one_or_none()


async def get_next_jail_release(session: AsyncSession) -> Optional[Jail]:
    """Get the next person being released from jail"""
    statement = select(Jail).order_by(Jail.until)
    return (await session.execute(statement)).scalars().first()


async def get_user_jail(session: AsyncSession, user_id: int) -> Optional[Jail]:
    """Check how long a given user is still in jail for"""
    statement = select(Jail).where(Jail.user_id == user_id)
    return (await session.execute(statement)).scalar_one_or_none()


async def imprison(session: AsyncSession, user_id: int, until: datetime) -> Jail:
    """Put a user in Didier Jail"""
    jail = Jail(user_id=user_id, until=until)
    session.add(jail)
    await session.commit()
    await session.refresh(jail)

    return jail


async def delete_prisoner_by_id(session: AsyncSession, jail_id: int):
    """Release a user from jail using their jail entry id"""
    statement = delete(Jail).where(Jail.jail_entry_id == jail_id)
    await session.execute(statement)
    await session.commit()
