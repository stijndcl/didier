from datetime import datetime
from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import users
from database.exceptions import currency as exceptions
from database.models import Bank, NightlyData
from database.utils.math.currency import (
    capacity_upgrade_price,
    interest_upgrade_price,
    rob_upgrade_price,
)

__all__ = [
    "add_dinks",
    "claim_nightly",
    "get_bank",
    "get_nightly_data",
    "invest",
    "upgrade_capacity",
    "upgrade_interest",
    "upgrade_rob",
    "NIGHTLY_AMOUNT",
]

NIGHTLY_AMOUNT = 420


async def get_bank(session: AsyncSession, user_id: int) -> Bank:
    """Get a user's bank info"""
    user = await users.get_or_add(session, user_id)
    return user.bank


async def get_nightly_data(session: AsyncSession, user_id: int) -> NightlyData:
    """Get a user's nightly info"""
    user = await users.get_or_add(session, user_id)
    return user.nightly_data


async def invest(session: AsyncSession, user_id: int, amount: Union[str, int]) -> int:
    """Invest all your Dinks"""
    bank = await get_bank(session, user_id)
    if amount == "all":
        amount = bank.dinks

    # Don't allow investing more dinks than you own
    amount = min(bank.dinks, int(amount))

    bank.dinks -= amount
    bank.invested += amount

    session.add(bank)
    await session.commit()

    return amount


async def add_dinks(session: AsyncSession, user_id: int, amount: int):
    """Increase the Dinks counter for a user"""
    bank = await get_bank(session, user_id)
    bank.dinks += amount
    session.add(bank)
    await session.commit()


async def claim_nightly(session: AsyncSession, user_id: int):
    """Claim daily Dinks"""
    nightly_data = await get_nightly_data(session, user_id)

    now = datetime.now()

    if nightly_data.last_nightly is not None and nightly_data.last_nightly == now.date():
        raise exceptions.DoubleNightly

    bank = await get_bank(session, user_id)
    bank.dinks += NIGHTLY_AMOUNT
    nightly_data.last_nightly = now

    session.add(bank)
    session.add(nightly_data)
    await session.commit()


async def upgrade_capacity(session: AsyncSession, user_id: int) -> int:
    """Upgrade capacity level"""
    bank = await get_bank(session, user_id)
    upgrade_price = capacity_upgrade_price(bank.capacity_level)

    # Can't afford this upgrade
    if upgrade_price > bank.dinks:
        raise exceptions.NotEnoughDinks

    bank.dinks -= upgrade_price
    bank.capacity_level += 1

    session.add(bank)
    await session.commit()

    return bank.capacity_level


async def upgrade_interest(session: AsyncSession, user_id: int) -> int:
    """Upgrade interest level"""
    bank = await get_bank(session, user_id)
    upgrade_price = interest_upgrade_price(bank.interest_level)

    # Can't afford this upgrade
    if upgrade_price > bank.dinks:
        raise exceptions.NotEnoughDinks

    bank.dinks -= upgrade_price
    bank.interest_level += 1

    session.add(bank)
    await session.commit()

    return bank.interest_level


async def upgrade_rob(session: AsyncSession, user_id: int) -> int:
    """Upgrade rob level"""
    bank = await get_bank(session, user_id)
    upgrade_price = rob_upgrade_price(bank.rob_level)

    # Can't afford this upgrade
    if upgrade_price > bank.dinks:
        raise exceptions.NotEnoughDinks

    bank.dinks -= upgrade_price
    bank.rob_level += 1

    session.add(bank)
    await session.commit()

    return bank.rob_level
