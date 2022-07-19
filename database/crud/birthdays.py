from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Birthday

__all__ = ["add_birthday", "get_birthday_for_user"]


async def add_birthday(session: AsyncSession, user_id: int, birthday: date):
    """Add a user's birthday into the database"""
    bd = Birthday(user_id=user_id, birthday=birthday)
    session.add(bd)
    await session.commit()


async def get_birthday_for_user(session: AsyncSession, user_id: int) -> Optional[Birthday]:
    """Find a user's birthday"""
    statement = select(Birthday).where(Birthday.user_id == user_id)
    return (await session.execute(statement)).scalar_one_or_none()
