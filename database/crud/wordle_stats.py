from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.schemas import WordleStats

__all__ = ["get_wordle_stats", "complete_wordle_game"]


async def get_wordle_stats(session: AsyncSession, user_id: int) -> WordleStats:
    """Get a user's wordle stats

    If no entry is found, it is first created
    """
    statement = select(WordleStats).where(WordleStats.user_id == user_id)
    stats = (await session.execute(statement)).scalar_one_or_none()
    if stats is not None:
        return stats

    stats = WordleStats(user_id=user_id)
    session.add(stats)
    await session.commit()
    await session.refresh(stats)

    return stats


async def complete_wordle_game(session: AsyncSession, user_id: int, win: bool):
    """Update the user's Wordle stats"""
    stats = await get_wordle_stats(session, user_id)
    stats.games += 1

    if win:
        stats.wins += 1

        # Update streak
        today = date.today()
        last_win = stats.last_win
        stats.last_win = today

        if last_win is None or (today - last_win).days > 1:
            # Never won a game before or streak is over
            stats.current_streak = 1
        else:
            # On a streak: increase counter
            stats.current_streak += 1

        # Update max streak if necessary
        if stats.current_streak > stats.highest_streak:
            stats.highest_streak = stats.current_streak
    else:
        # Streak is over
        stats.current_streak = 0

    session.add(stats)
    await session.commit()
