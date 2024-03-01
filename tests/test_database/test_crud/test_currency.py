import datetime

import pytest
from freezegun import freeze_time
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import currency as crud
from database.exceptions import currency as exceptions
from database.schemas import Bank, BankSavings


async def test_add_dinks(postgres: AsyncSession, bank: Bank):
    """Test adding dinks to an account"""
    assert bank.dinks == 0
    await crud.add_dinks(postgres, bank.user_id, 10)
    await postgres.refresh(bank)
    assert bank.dinks == 10


@freeze_time("2022/07/23")
async def test_claim_nightly_available(postgres: AsyncSession, bank: Bank):
    """Test claiming nightlies when it hasn't been done yet"""
    await crud.claim_nightly(postgres, bank.user_id)
    await postgres.refresh(bank)
    assert bank.dinks == crud.NIGHTLY_AMOUNT

    nightly_data = await crud.get_nightly_data(postgres, bank.user_id)
    assert nightly_data.last_nightly == datetime.date(year=2022, month=7, day=23)


@freeze_time("2022/07/23")
async def test_claim_nightly_unavailable(postgres: AsyncSession, bank: Bank):
    """Test claiming nightlies twice in a day"""
    await crud.claim_nightly(postgres, bank.user_id)

    with pytest.raises(exceptions.DoubleNightly):
        await crud.claim_nightly(postgres, bank.user_id)

    await postgres.refresh(bank)
    assert bank.dinks == crud.NIGHTLY_AMOUNT


async def test_save(postgres: AsyncSession, bank: Bank, savings: BankSavings):
    """Test saving some Dinks"""
    bank.dinks = 100
    postgres.add(bank)
    await postgres.commit()

    await crud.save(postgres, bank.user_id, 20, bank=bank, savings=savings)
    await postgres.refresh(bank)
    await postgres.refresh(savings)

    assert bank.dinks == 80
    assert savings.saved == 20


async def test_save_all(postgres: AsyncSession, bank: Bank, savings: BankSavings):
    """Test saving all dinks"""
    bank.dinks = 100
    postgres.add(bank)
    await postgres.commit()

    await crud.save(postgres, bank.user_id, "all", bank=bank, savings=savings)
    await postgres.refresh(bank)
    await postgres.refresh(savings)

    assert bank.dinks == 0
    assert savings.saved == 100


async def test_save_more_than_owned(postgres: AsyncSession, bank: Bank, savings: BankSavings):
    """Test saving more Dinks than you own"""
    bank.dinks = 100
    postgres.add(bank)
    await postgres.commit()

    await crud.save(postgres, bank.user_id, 200, bank=bank, savings=savings)
    await postgres.refresh(bank)
    await postgres.refresh(savings)

    assert bank.dinks == 0
    assert savings.saved == 100
