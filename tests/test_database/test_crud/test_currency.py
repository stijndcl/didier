import datetime

import pytest
from freezegun import freeze_time

from database.crud import currency as crud
from database.exceptions import currency as exceptions
from database.models import Bank


async def test_add_dinks(postgres, bank: Bank):
    """Test adding dinks to an account"""
    assert bank.dinks == 0
    await crud.add_dinks(postgres, bank.user_id, 10)
    await postgres.refresh(bank)
    assert bank.dinks == 10


@freeze_time("2022/07/23")
async def test_claim_nightly_available(postgres, bank: Bank):
    """Test claiming nightlies when it hasn't been done yet"""
    await crud.claim_nightly(postgres, bank.user_id)
    await postgres.refresh(bank)
    assert bank.dinks == crud.NIGHTLY_AMOUNT

    nightly_data = await crud.get_nightly_data(postgres, bank.user_id)
    assert nightly_data.last_nightly == datetime.date(year=2022, month=7, day=23)


@freeze_time("2022/07/23")
async def test_claim_nightly_unavailable(postgres, bank: Bank):
    """Test claiming nightlies twice in a day"""
    await crud.claim_nightly(postgres, bank.user_id)

    with pytest.raises(exceptions.DoubleNightly):
        await crud.claim_nightly(postgres, bank.user_id)

    await postgres.refresh(bank)
    assert bank.dinks == crud.NIGHTLY_AMOUNT


async def test_invest(postgres, bank: Bank):
    """Test investing some Dinks"""
    bank.dinks = 100
    postgres.add(bank)
    await postgres.commit()

    await crud.invest(postgres, bank.user_id, 20)
    await postgres.refresh(bank)

    assert bank.dinks == 80
    assert bank.invested == 20


async def test_invest_all(postgres, bank: Bank):
    """Test investing all dinks"""
    bank.dinks = 100
    postgres.add(bank)
    await postgres.commit()

    await crud.invest(postgres, bank.user_id, "all")
    await postgres.refresh(bank)

    assert bank.dinks == 0
    assert bank.invested == 100


async def test_invest_more_than_owned(postgres, bank: Bank):
    """Test investing more Dinks than you own"""
    bank.dinks = 100
    postgres.add(bank)
    await postgres.commit()

    await crud.invest(postgres, bank.user_id, 200)
    await postgres.refresh(bank)

    assert bank.dinks == 0
    assert bank.invested == 100
