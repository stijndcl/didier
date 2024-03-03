from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.schemas import CFStats

__all__ = ["get_cf_stats", "update_cf_stats"]


async def get_cf_stats(session: AsyncSession, user_id: int) -> CFStats:
    """Get a user's coinflip stats"""
    statement = select(CFStats).where(CFStats.user_id == user_id)
    result = (await session.execute(statement)).scalar_one_or_none()

    if result is None:
        result = CFStats(user_id=user_id)
        session.add(result)
        await session.commit()
        await session.refresh(result)

    return result


async def update_cf_stats(session: AsyncSession, user_id: int, outcome: int):
    """Update a user's coinflip stats"""
    stats = await get_cf_stats(session, user_id)
    if outcome < 0:
        stats.games_lost += 1
        stats.dinks_lost += abs(outcome)
    else:
        stats.games_won += 1
        stats.dinks_won += outcome

    session.add(stats)
    await session.commit()
