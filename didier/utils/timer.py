import asyncio
from datetime import datetime
from typing import Optional

import discord.utils

from database.crud.events import get_next_event
from database.schemas import Event
from didier import Didier
from didier.utils.types.datetime import tz_aware_now

__all__ = ["Timer"]


class Timer:
    """Class for scheduled timers"""

    client: Didier
    upcoming_timer: Optional[datetime]
    upcoming_event_id: Optional[int]
    _task: Optional[asyncio.Task]

    def __init__(self, client: Didier):
        self.client = client

        self.upcoming_timer = None
        self.upcoming_event_id = None
        self._task = None

        self.client.loop.create_task(self.update())

    async def update(self):
        """Get & schedule the closest reminder"""
        async with self.client.postgres_session as session:
            event = await get_next_event(session, now=tz_aware_now())

        # No upcoming events
        if event is None:
            return

        self.maybe_replace_task(event)

    def maybe_replace_task(self, event: Event):
        """Replace the current task if necessary"""
        # If there is a current (pending) task, and the new timer is sooner than the
        # pending one, cancel it
        if self._task is not None and not self._task.done():
            if self.upcoming_timer > event.timestamp:
                self._task.cancel()
            else:
                # The new task happens after the existing task, it has to wait for its turn
                return

        self._task = self.client.loop.create_task(self.end_timer(endtime=event.timestamp, event_id=event.event_id))
        self.upcoming_timer = event.timestamp
        self.upcoming_event_id = event.event_id

    async def end_timer(self, *, endtime: datetime, event_id: int):
        """Wait until a timer runs out, and then trigger an event to send the message"""
        await discord.utils.sleep_until(endtime)
        self.upcoming_timer = None
        self.upcoming_event_id = None
        self.client.dispatch("timer_end", event_id)
