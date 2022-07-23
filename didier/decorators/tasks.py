from __future__ import annotations

import functools
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from didier.cogs.tasks import Tasks

from database import enums
from database.crud.tasks import set_last_task_execution_time

__all__ = ["timed_task"]


def timed_task(task: enums.TaskType):
    """Decorator to log the last execution time of a task"""

    def _decorator(func):
        @functools.wraps(func)
        async def _wrapper(tasks_cog: Tasks, *args, **kwargs):
            await func(tasks_cog, *args, **kwargs)

            async with tasks_cog.client.db_session as session:
                await set_last_task_execution_time(session, task)

        return _wrapper

    return _decorator
