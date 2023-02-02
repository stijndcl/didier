from typing import Optional
from zoneinfo import ZoneInfo

from dateutil.parser import parse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.schemas import Event

__all__ = ["add_event", "get_event_by_id", "get_events", "get_next_event"]


async def add_event(
    session: AsyncSession, *, name: str, description: Optional[str], date_str: str, channel_id: int
) -> Event:
    """Create a new event"""
    date_dt = parse(date_str, dayfirst=True).replace(tzinfo=ZoneInfo("Europe/Brussels"))

    event = Event(name=name, description=description, timestamp=date_dt, notification_channel=channel_id)
    session.add(event)
    await session.commit()

    return event


async def get_event_by_id(session: AsyncSession, event_id: int) -> Optional[Event]:
    """Get an event by its id"""
    statement = select(Event).where(Event.event_id == event_id)
    return (await session.execute(statement)).scalar_one_or_none()


async def get_events(session: AsyncSession) -> list[Event]:
    """Get a list of all upcoming events"""
    statement = select(Event)
    return (await session.execute(statement)).scalars().all()


async def get_next_event(session: AsyncSession) -> Optional[Event]:
    """Get the first upcoming event"""
    statement = select(Event).order_by(Event.timestamp)
    return (await session.execute(statement)).scalar_one_or_none()
