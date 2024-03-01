from datetime import date
from typing import List, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import users
from database.exceptions import currency as exceptions
from database.schemas import Bank, BankSavings, NightlyData
from database.utils.math.currency import (
    capacity_upgrade_price,
    interest_rate,
    interest_upgrade_price,
    rob_upgrade_price,
    savings_cap,
)

__all__ = [
    "add_dinks",
    "apply_daily_interest",
    "claim_nightly",
    "deduct_dinks",
    "gamble_dinks",
    "get_bank",
    "get_nightly_data",
    "save",
    "upgrade_capacity",
    "upgrade_interest",
    "upgrade_rob",
    "withdraw",
    "NIGHTLY_AMOUNT",
]

NIGHTLY_AMOUNT = 420


async def get_bank(session: AsyncSession, user_id: int) -> Bank:
    """Get a user's bank info"""
    user = await users.get_or_add_user(session, user_id)
    return user.bank


async def get_savings(session: AsyncSession, user_id: int) -> BankSavings:
    """Get a user's savings info"""
    user = await users.get_or_add_user(session, user_id)
    return user.savings


async def get_nightly_data(session: AsyncSession, user_id: int) -> NightlyData:
    """Get a user's nightly info"""
    user = await users.get_or_add_user(session, user_id)
    return user.nightly_data


async def save(
    session: AsyncSession,
    user_id: int,
    amount: Union[str, int],
    *,
    bank: Optional[Bank] = None,
    savings: Optional[BankSavings] = None
) -> int:
    """Invest some of your Dinks"""
    bank = bank or await get_bank(session, user_id)
    savings = savings or await get_savings(session, user_id)

    if amount == "all":
        amount = bank.dinks

    if bank.dinks <= 0:
        return 0

    # Don't allow investing more dinks than you own
    amount = min(bank.dinks, int(amount))

    # Don't allow exceeding the limit
    limit = savings_cap(bank.capacity_level)

    if savings.saved >= limit:
        raise exceptions.SavingsCapExceeded

    if savings.saved + amount > limit:
        amount = max(0, limit - savings.saved)

    bank.dinks -= amount
    savings.saved += amount

    session.add(bank)
    session.add(savings)
    await session.commit()

    return amount


async def withdraw(session: AsyncSession, user_id: int, amount: Union[str, int], *, bank: Optional[Bank] = None) -> int:
    """Withdraw your saved Dinks"""
    bank = bank or await get_bank(session, user_id)
    savings = await get_savings(session, user_id)

    if amount == "all":
        amount = savings.saved

    # Don't allow withdrawing more dinks than you own
    amount = min(savings.saved, int(amount))

    bank.dinks += amount
    savings.saved -= amount
    savings.daily_minimum = min(savings.daily_minimum, savings.saved)

    session.add(bank)
    session.add(savings)
    await session.commit()

    return amount


async def add_dinks(session: AsyncSession, user_id: int, amount: int, *, bank: Optional[Bank] = None):
    """Increase the Dinks counter for a user"""
    bank = bank or await get_bank(session, user_id)
    bank.dinks += amount
    session.add(bank)
    await session.commit()


async def deduct_dinks(session: AsyncSession, user_id: int, amount: int, *, bank: Optional[Bank] = None) -> int:
    """Decrease the Dinks counter for a user"""
    bank = bank or await get_bank(session, user_id)

    deducted_amount = min(amount, bank.dinks)

    bank.dinks -= deducted_amount
    session.add(bank)
    await session.commit()

    return deducted_amount


async def claim_nightly(session: AsyncSession, user_id: int, *, bank: Optional[Bank] = None):
    """Claim daily Dinks"""
    nightly_data = await get_nightly_data(session, user_id)

    now = date.today()

    if nightly_data.last_nightly is not None and nightly_data.last_nightly == now:
        raise exceptions.DoubleNightly

    bank = bank or await get_bank(session, user_id)
    bank.dinks += NIGHTLY_AMOUNT
    nightly_data.last_nightly = now

    session.add(bank)
    session.add(nightly_data)
    await session.commit()


async def upgrade_capacity(session: AsyncSession, user_id: int, *, bank: Optional[Bank] = None) -> int:
    """Upgrade capacity level"""
    bank = bank or await get_bank(session, user_id)
    upgrade_price = capacity_upgrade_price(bank.capacity_level)

    # Can't afford this upgrade
    if upgrade_price > bank.dinks:
        raise exceptions.NotEnoughDinks

    bank.dinks -= upgrade_price
    bank.capacity_level += 1

    session.add(bank)
    await session.commit()

    return bank.capacity_level


async def upgrade_interest(session: AsyncSession, user_id: int, *, bank: Optional[Bank] = None) -> int:
    """Upgrade interest level"""
    bank = bank or await get_bank(session, user_id)
    upgrade_price = interest_upgrade_price(bank.interest_level)

    # Can't afford this upgrade
    if upgrade_price > bank.dinks:
        raise exceptions.NotEnoughDinks

    bank.dinks -= upgrade_price
    bank.interest_level += 1

    session.add(bank)
    await session.commit()

    return bank.interest_level


async def upgrade_rob(session: AsyncSession, user_id: int, *, bank: Optional[Bank] = None) -> int:
    """Upgrade rob level"""
    bank = bank or await get_bank(session, user_id)
    upgrade_price = rob_upgrade_price(bank.rob_level)

    # Can't afford this upgrade
    if upgrade_price > bank.dinks:
        raise exceptions.NotEnoughDinks

    bank.dinks -= upgrade_price
    bank.rob_level += 1

    session.add(bank)
    await session.commit()

    return bank.rob_level


async def gamble_dinks(
    session: AsyncSession,
    user_id: int,
    amount: Union[str, int],
    payout_factor: int,
    won: bool,
    *,
    bank: Optional[Bank] = None
) -> int:
    """Gamble some of your Didier Dinks"""
    bank = bank or await get_bank(session, user_id)
    if amount == "all":
        amount = bank.dinks

    if bank.dinks <= 0:
        return 0

    amount = min(int(amount), bank.dinks)

    sign = 1 if won else -1
    factor = (payout_factor - 1) if won else 1
    await add_dinks(session, user_id, sign * amount * factor, bank=bank)

    return amount * factor


async def rob(
    session: AsyncSession,
    amount: int,
    robber_id: int,
    robbed_id: int,
    *,
    robber_bank: Optional[Bank] = None,
    robbed_bank: Optional[Bank] = None
):
    """Rob another user's Didier Dinks"""
    robber = robber_bank or await get_bank(session, robber_id)
    robbed = robbed_bank or await get_bank(session, robbed_id)

    robber.dinks += amount
    robbed.dinks -= amount

    session.add(robber)
    session.add(robbed)
    await session.commit()


async def apply_daily_interest(session: AsyncSession):
    """Apply daily interest rates to all accounts with saved Dinks"""
    statement = select(BankSavings)
    all_savings: List[BankSavings] = list((await session.execute(statement)).scalars().all())

    for savings_account in all_savings:
        if savings_account.saved == 0:
            continue

        bank = await get_bank(session, savings_account.user_id)
        rate = interest_rate(bank.interest_level)

        savings_account.saved = float(savings_account.saved * rate)
        savings_account.daily_minimum = savings_account.saved
        session.add(savings_account)

    await session.commit()
