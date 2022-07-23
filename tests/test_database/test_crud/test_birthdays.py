from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import birthdays as crud
from database.models import User


async def test_add_birthday_not_present(database_session: AsyncSession, user: User):
    """Test setting a user's birthday when it doesn't exist yet"""
    assert user.birthday is None

    bd_date = datetime.today().date()
    await crud.add_birthday(database_session, user.user_id, bd_date)
    await database_session.refresh(user)
    assert user.birthday is not None
    assert user.birthday.birthday == bd_date


async def test_add_birthday_overwrite(database_session: AsyncSession, user: User):
    """Test that setting a user's birthday when it already exists overwrites it"""
    bd_date = datetime.today().date()
    await crud.add_birthday(database_session, user.user_id, bd_date)
    await database_session.refresh(user)
    assert user.birthday is not None

    new_bd_date = bd_date + timedelta(weeks=1)
    await crud.add_birthday(database_session, user.user_id, new_bd_date)
    await database_session.refresh(user)
    assert user.birthday.birthday == new_bd_date


async def test_get_birthday_exists(database_session: AsyncSession, user: User):
    """Test getting a user's birthday when it exists"""
    bd_date = datetime.today().date()
    await crud.add_birthday(database_session, user.user_id, bd_date)
    await database_session.refresh(user)

    bd = await crud.get_birthday_for_user(database_session, user.user_id)
    assert bd is not None
    assert bd.birthday == bd_date


async def test_get_birthday_not_exists(database_session: AsyncSession, user: User):
    """Test getting a user's birthday when it doesn't exist"""
    bd = await crud.get_birthday_for_user(database_session, user.user_id)
    assert bd is None
