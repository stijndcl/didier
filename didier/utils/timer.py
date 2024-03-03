import abc
import asyncio
from datetime import datetime, timedelta
from typing import Generic, Optional, TypeVar

import discord.utils
from overrides import overrides

import settings
from database.crud.events import get_next_event
from database.crud.jail import get_next_jail_release
from database.schemas import Event, Jail
from didier import Didier
from didier.utils.types.datetime import tz_aware_now

__all__ = ["JailTimer", "EventTimer"]

REMINDER_PREDELAY = timedelta(minutes=settings.REMINDER_PRE)


T = TypeVar("T")


class ABCTimer(abc.ABC, Generic[T]):
    """Base class for scheduled timers"""

    client: Didier
    upcoming_timer: Optional[datetime]
    upcoming_event_id: Optional[int]
    _task: Optional[asyncio.Task]

    _delta: Optional[timedelta]
    _event: str

    def __init__(self, client: Didier, *, event: str, delta: Optional[timedelta] = None):
        self.client = client

        self.upcoming_timer = None
        self.upcoming_event_id = None
        self._task = None

        self._delta = delta
        self._event = event

    @abc.abstractmethod
    async def dissect_item(self, item: T) -> tuple[datetime, int]:
        """Method that takes an item and returns the corresponding timestamp and id"""

    @abc.abstractmethod
    async def get_next(self) -> Optional[T]:
        """Method that fetches the next item from the database"""

    async def update(self):
        """Get & schedule the closest item"""
        next_item = await self.get_next()

        # No upcoming items
        if next_item is None:
            return

        self.maybe_replace_task(next_item)

    def cancel(self):
        """Cancel the running task"""
        if self._task is not None:
            self._task.cancel()
            self._task = None

    def maybe_replace_task(self, item: T):
        """Replace the current task if necessary"""
        timestamp, item_id = self.dissect_item(item)

        # If there is a current (pending) task, and the new timer is sooner than the
        # pending one, cancel it
        if self._task is not None and not self._task.done():
            # The upcoming timer will never be None at this point, but Mypy is mad
            if self.upcoming_timer is not None and self.upcoming_timer > timestamp:
                self._task.cancel()
            else:
                # The new task happens after the existing task, it has to wait for its turn
                return

        self.upcoming_timer = timestamp
        self.upcoming_event_id = item_id
        self._task = self.client.loop.create_task(self.end_timer(endtime=timestamp, event_id=item_id))

    async def end_timer(self, *, endtime: datetime, event_id: int):
        """Wait until a timer runs out, and then trigger an event to send the message"""
        until = endtime
        if self._delta is not None:
            until -= self._delta

        await discord.utils.sleep_until(until)
        self.upcoming_timer = None
        self.upcoming_event_id = None
        self.client.dispatch(self._event, event_id)


class EventTimer(ABCTimer[Event]):
    """Timer for upcoming IRL events"""

    def __init__(self, client: Didier):
        super().__init__(client, event="event_reminder", delta=REMINDER_PREDELAY)

    @overrides
    async def dissect_item(self, item: Event) -> tuple[datetime, int]:
        return item.timestamp, item.event_id

    @overrides
    async def get_next(self) -> Optional[Event]:
        async with self.client.postgres_session as session:
            return await get_next_event(session, now=tz_aware_now())


class JailTimer(ABCTimer[Jail]):
    """Timer for people spending time in Didier Jail"""

    def __init__(self, client: Didier):
        super().__init__(client, event="jail_release")

    @overrides
    async def dissect_item(self, item: Jail) -> tuple[datetime, int]:
        return item.until, item.jail_entry_id

    @overrides
    async def get_next(self) -> Optional[Jail]:
        async with self.client.postgres_session as session:
            return await get_next_jail_release(session)
