from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import users
from database.exceptions import currency as exceptions
from database.models import Bank
from database.utils.math.currency import rob_upgrade_price, interest_upgrade_price, capacity_upgrade_price


NIGHTLY_AMOUNT = 420


async def get_bank(session: AsyncSession, user_id: int) -> Bank:
    """Get a user's bank info"""
    user = await users.get_or_add(session, user_id)
    return user.bank


async def add_dinks(session: AsyncSession, user_id: int, amount: int):
    """Increase the Dinks counter for a user"""
    bank = await get_bank(session, user_id)
    bank.dinks += amount
    session.add(bank)
    await session.commit()


async def claim_nightly(session: AsyncSession, user_id: int):
    """Claim daily Dinks"""
    user = await users.get_or_add(session, user_id)
    nightly_data = user.nightly_data

    now = datetime.now()

    if nightly_data.last_nightly is not None and nightly_data.last_nightly.date() == now.date():
        raise exceptions.DoubleNightly

    bank = user.bank
    bank.dinks += NIGHTLY_AMOUNT
    nightly_data.last_nightly = now

    session.add(bank)
    session.add(nightly_data)
    await session.commit()


async def upgrade_capacity(database_session: AsyncSession, user_id: int) -> int:
    """Upgrade capacity level"""
    bank = await get_bank(database_session, user_id)
    upgrade_price = capacity_upgrade_price(bank.capacity_level)

    # Can't afford this upgrade
    if upgrade_price > bank.dinks:
        raise exceptions.NotEnoughDinks

    bank.dinks -= upgrade_price
    bank.capacity_level += 1

    database_session.add(bank)
    await database_session.commit()

    return bank.capacity_level


async def upgrade_interest(database_session: AsyncSession, user_id: int) -> int:
    """Upgrade interest level"""
    bank = await get_bank(database_session, user_id)
    upgrade_price = interest_upgrade_price(bank.interest_level)

    # Can't afford this upgrade
    if upgrade_price > bank.dinks:
        raise exceptions.NotEnoughDinks

    bank.dinks -= upgrade_price
    bank.interest_level += 1

    database_session.add(bank)
    await database_session.commit()

    return bank.interest_level


async def upgrade_rob(database_session: AsyncSession, user_id: int) -> int:
    """Upgrade rob level"""
    bank = await get_bank(database_session, user_id)
    upgrade_price = rob_upgrade_price(bank.rob_level)

    # Can't afford this upgrade
    if upgrade_price > bank.dinks:
        raise exceptions.NotEnoughDinks

    bank.dinks -= upgrade_price
    bank.rob_level += 1

    database_session.add(bank)
    await database_session.commit()

    return bank.rob_level
