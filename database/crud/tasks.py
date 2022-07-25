import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.enums import TaskType
from database.schemas.relational import Task
from database.utils.datetime import LOCAL_TIMEZONE

__all__ = ["get_task_by_enum", "set_last_task_execution_time"]


async def get_task_by_enum(session: AsyncSession, task: TaskType) -> Optional[Task]:
    """Get a task by its enum value, if it exists

    Returns None if the task does not exist
    """
    statement = select(Task).where(Task.task == task)
    return (await session.execute(statement)).scalar_one_or_none()


async def set_last_task_execution_time(session: AsyncSession, task: TaskType):
    """Set the last time a specific task was executed"""
    _task = await get_task_by_enum(session, task)

    if _task is None:
        _task = Task(task=task)

    _task.previous_run = datetime.datetime.now(tz=LOCAL_TIMEZONE)
    session.add(_task)
    await session.commit()
