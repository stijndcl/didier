from sqlalchemy import select

from database.crud import users as crud
from database.schemas.relational import User


async def test_get_or_add_non_existing(postgres):
    """Test get_or_add for a user that doesn't exist"""
    await crud.get_or_add(postgres, 1)
    statement = select(User)
    res = (await postgres.execute(statement)).scalars().all()

    assert len(res) == 1
    assert res[0].bank is not None
    assert res[0].nightly_data is not None


async def test_get_or_add_existing(postgres):
    """Test get_or_add for a user that does exist"""
    user = await crud.get_or_add(postgres, 1)
    bank = user.bank

    assert await crud.get_or_add(postgres, 1) == user
    assert (await crud.get_or_add(postgres, 1)).bank == bank
