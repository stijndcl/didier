import datetime

import pytest
from freezegun import freeze_time
from sqlalchemy import select

from database.crud import tasks as crud
from database.enums import TaskType
from database.schemas.relational import Task


@pytest.fixture
def task_type() -> TaskType:
    """Fixture to use the same TaskType in every test"""
    return TaskType.BIRTHDAYS


@pytest.fixture
async def task(postgres, task_type: TaskType) -> Task:
    """Fixture to create a task"""
    task = Task(task=task_type)
    postgres.add(task)
    await postgres.commit()
    return task


async def test_get_task_by_enum_present(postgres, task: Task, task_type: TaskType):
    """Test getting a task by its enum type when it exists"""
    result = await crud.get_task_by_enum(postgres, task_type)
    assert result is not None
    assert result == task


async def test_get_task_by_enum_not_present(postgres, task_type: TaskType):
    """Test getting a task by its enum type when it doesn't exist"""
    result = await crud.get_task_by_enum(postgres, task_type)
    assert result is None


@freeze_time("2022/07/24")
async def test_set_execution_time_exists(postgres, task: Task, task_type: TaskType):
    """Test setting the execution time of an existing task"""
    await postgres.refresh(task)
    assert task.previous_run is None

    await crud.set_last_task_execution_time(postgres, task_type)
    await postgres.refresh(task)
    assert task.previous_run == datetime.datetime(year=2022, month=7, day=24)


@freeze_time("2022/07/24")
async def test_set_execution_time_doesnt_exist(postgres, task_type: TaskType):
    """Test setting the execution time of a non-existing task"""
    statement = select(Task).where(Task.task == task_type)
    results = list((await postgres.execute(statement)).scalars().all())
    assert len(results) == 0

    await crud.set_last_task_execution_time(postgres, task_type)
    results = list((await postgres.execute(statement)).scalars().all())
    assert len(results) == 1
    task = results[0]
    assert task.previous_run == datetime.datetime(year=2022, month=7, day=24)
