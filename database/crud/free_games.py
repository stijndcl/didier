from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.schemas import FreeGame

__all__ = ["add_free_games", "filter_present_games"]


async def add_free_games(session: AsyncSession, game_ids: list[int]):
    """Bulk-add a list of IDs into the database"""
    games = [FreeGame(free_game_id=game_id) for game_id in game_ids]
    session.add_all(games)
    await session.commit()


async def filter_present_games(session: AsyncSession, game_ids: list[int]) -> list[int]:
    """Filter a list of game IDs down to the ones that aren't in the database yet"""
    statement = select(FreeGame.free_game_id).where(FreeGame.free_game_id.in_(game_ids))
    matches: list[int] = list((await session.execute(statement)).scalars().all())
    return list(set(game_ids).difference(matches))
