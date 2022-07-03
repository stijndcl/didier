import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import currency as crud
from database.exceptions import currency as exceptions
from database.models import Bank


DEBUG_USER_ID = 1


@pytest.fixture
async def bank(database_session: AsyncSession) -> Bank:
    _bank = await crud.get_bank(database_session, DEBUG_USER_ID)
    await database_session.refresh(_bank)
    return _bank


async def test_add_dinks(database_session: AsyncSession, bank: Bank):
    """Test adding dinks to an account"""
    assert bank.dinks == 0
    await crud.add_dinks(database_session, bank.user_id, 10)
    await database_session.refresh(bank)
    assert bank.dinks == 10


async def test_claim_nightly_available(database_session: AsyncSession, bank: Bank):
    """Test claiming nightlies when it hasn't been done yet"""
    await crud.claim_nightly(database_session, bank.user_id)
    await database_session.refresh(bank)
    assert bank.dinks == crud.NIGHTLY_AMOUNT


async def test_claim_nightly_unavailable(database_session: AsyncSession, bank: Bank):
    """Test claiming nightlies twice in a day"""
    await crud.claim_nightly(database_session, bank.user_id)

    with pytest.raises(exceptions.DoubleNightly):
        await crud.claim_nightly(database_session, bank.user_id)

    await database_session.refresh(bank)
    assert bank.dinks == crud.NIGHTLY_AMOUNT


async def test_invest(database_session: AsyncSession, bank: Bank):
    """Test investing some Dinks"""
    bank.dinks = 100
    database_session.add(bank)
    await database_session.commit()

    await crud.invest(database_session, bank.user_id, 20)
    await database_session.refresh(bank)

    assert bank.dinks == 80
    assert bank.invested == 20


async def test_invest_all(database_session: AsyncSession, bank: Bank):
    """Test investing all dinks"""
    bank.dinks = 100
    database_session.add(bank)
    await database_session.commit()

    await crud.invest(database_session, bank.user_id, "all")
    await database_session.refresh(bank)

    assert bank.dinks == 0
    assert bank.invested == 100


async def test_invest_more_than_owned(database_session: AsyncSession, bank: Bank):
    """Test investing more Dinks than you own"""
    bank.dinks = 100
    database_session.add(bank)
    await database_session.commit()

    await crud.invest(database_session, bank.user_id, 200)
    await database_session.refresh(bank)

    assert bank.dinks == 0
    assert bank.invested == 100
