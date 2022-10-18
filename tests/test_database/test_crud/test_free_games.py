from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import free_games as crud
from database.schemas import FreeGame


async def test_add_games(postgres: AsyncSession):
    """Test adding new games"""
    statement = select(FreeGame)
    games = (await postgres.execute(statement)).scalars().all()
    assert not games

    await crud.add_free_games(postgres, [1, 2, 3, 4])

    games = (await postgres.execute(statement)).scalars().all()
    assert len(games) == 4
