from datetime import datetime, timedelta

from freezegun import freeze_time
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import birthdays as crud
from database.crud import users
from database.schemas import User


async def test_add_birthday_not_present(postgres: AsyncSession, user: User):
    """Test setting a user's birthday when it doesn't exist yet"""
    assert user.birthday is None

    bd_date = datetime.today().date()
    await crud.add_birthday(postgres, user.user_id, bd_date)
    await postgres.refresh(user)
    assert user.birthday is not None
    assert user.birthday.birthday == bd_date


async def test_add_birthday_overwrite(postgres: AsyncSession, user: User):
    """Test that setting a user's birthday when it already exists overwrites it"""
    bd_date = datetime.today().date()
    await crud.add_birthday(postgres, user.user_id, bd_date)
    await postgres.refresh(user)
    assert user.birthday is not None

    new_bd_date = bd_date + timedelta(weeks=1)
    await crud.add_birthday(postgres, user.user_id, new_bd_date)
    await postgres.refresh(user)
    assert user.birthday.birthday == new_bd_date


async def test_get_birthday_exists(postgres: AsyncSession, user: User):
    """Test getting a user's birthday when it exists"""
    bd_date = datetime.today().date()
    await crud.add_birthday(postgres, user.user_id, bd_date)
    await postgres.refresh(user)

    bd = await crud.get_birthday_for_user(postgres, user.user_id)
    assert bd is not None
    assert bd.birthday == bd_date


async def test_get_birthday_not_exists(postgres: AsyncSession, user: User):
    """Test getting a user's birthday when it doesn't exist"""
    bd = await crud.get_birthday_for_user(postgres, user.user_id)
    assert bd is None


@freeze_time("2022/07/23")
async def test_get_birthdays_on_day(postgres: AsyncSession, user: User):
    """Test getting all birthdays on a given day"""
    await crud.add_birthday(postgres, user.user_id, datetime.today().replace(year=2001))

    user_2 = await users.get_or_add_user(postgres, user.user_id + 1)
    await crud.add_birthday(postgres, user_2.user_id, datetime.today() + timedelta(weeks=1))
    birthdays = await crud.get_birthdays_on_day(postgres, datetime.today())
    assert len(birthdays) == 1
    assert birthdays[0].user_id == user.user_id


@freeze_time("2022/07/23")
async def test_get_birthdays_none_present(postgres: AsyncSession):
    """Test getting all birthdays when there are none"""
    birthdays = await crud.get_birthdays_on_day(postgres, datetime.today())
    assert len(birthdays) == 0

    # Add a random birthday that is not today
    await crud.add_birthday(postgres, 1, datetime.today() + timedelta(days=1))

    birthdays = await crud.get_birthdays_on_day(postgres, datetime.today())
    assert len(birthdays) == 0
