from typing import Optional
from zoneinfo import ZoneInfo

from dateutil.parser import parse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.schemas.relational import Deadline, UforaCourse

__all__ = ["add_deadline", "get_deadlines"]


async def add_deadline(session: AsyncSession, course_id: int, name: str, date_str: str):
    """Add a new deadline"""
    date_dt = parse(date_str).replace(tzinfo=ZoneInfo("Europe/Brussels"))

    # If we only have a day, assume it's the end of the day
    if date_dt.hour == date_dt.minute == date_dt.second == 0:
        date_dt.replace(hour=23, minute=59, second=59)

    deadline = Deadline(course_id=course_id, name=name, deadline=date_dt)
    session.add(deadline)
    await session.commit()


async def get_deadlines(session: AsyncSession, *, course: Optional[UforaCourse] = None) -> list[Deadline]:
    """Get a list of all deadlines that are currently known

    This includes deadlines that have passed already
    """
    statement = select(Deadline)

    if course is not None:
        statement = statement.where(Deadline.course_id == course.course_id)

    statement = statement.options(selectinload(Deadline.course))
    return (await session.execute(statement)).scalars().all()
