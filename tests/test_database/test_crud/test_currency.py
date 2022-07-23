import datetime

import pytest
from freezegun import freeze_time
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import currency as crud
from database.exceptions import currency as exceptions
from database.models import Bank


async def test_add_dinks(database_session: AsyncSession, bank: Bank):
    """Test adding dinks to an account"""
    assert bank.dinks == 0
    await crud.add_dinks(database_session, bank.user_id, 10)
    await database_session.refresh(bank)
    assert bank.dinks == 10


@freeze_time("2022/07/23")
async def test_claim_nightly_available(database_session: AsyncSession, bank: Bank):
    """Test claiming nightlies when it hasn't been done yet"""
    await crud.claim_nightly(database_session, bank.user_id)
    await database_session.refresh(bank)
    assert bank.dinks == crud.NIGHTLY_AMOUNT

    nightly_data = await crud.get_nightly_data(database_session, bank.user_id)
    assert nightly_data.last_nightly == datetime.date(year=2022, month=7, day=23)


@freeze_time("2022/07/23")
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
