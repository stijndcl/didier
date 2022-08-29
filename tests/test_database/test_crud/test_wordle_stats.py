import datetime

import pytest
from freezegun import freeze_time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import wordle_stats as crud
from database.schemas import User, WordleStats


async def insert_game_stats(postgres: AsyncSession, stats: WordleStats):
    """Helper function to insert some stats"""
    postgres.add(stats)
    await postgres.commit()


@pytest.mark.postgres
async def test_get_stats_non_existent_creates(postgres: AsyncSession, user: User):
    """Test getting a user's stats when the db is empty"""
    test_user_id = user.user_id

    statement = select(WordleStats).where(WordleStats.user_id == test_user_id)
    assert (await postgres.execute(statement)).scalar_one_or_none() is None

    await crud.get_wordle_stats(postgres, test_user_id)
    assert (await postgres.execute(statement)).scalar_one_or_none() is not None


@pytest.mark.postgres
async def test_get_stats_existing_returns(postgres: AsyncSession, user: User):
    """Test getting a user's stats when there's already an entry present"""
    test_user_id = user.user_id

    stats = WordleStats(user_id=test_user_id)
    stats.games = 20
    await insert_game_stats(postgres, stats)
    found_stats = await crud.get_wordle_stats(postgres, test_user_id)
    assert found_stats.games == 20


@pytest.mark.postgres
@freeze_time("2022-07-30")
async def test_complete_wordle_game_won(postgres: AsyncSession, user: User):
    """Test completing a wordle game when you win"""
    test_user_id = user.user_id

    await crud.complete_wordle_game(postgres, test_user_id, win=True)
    stats = await crud.get_wordle_stats(postgres, test_user_id)
    assert stats.games == 1
    assert stats.wins == 1
    assert stats.current_streak == 1
    assert stats.highest_streak == 1
    assert stats.last_win == datetime.date.today()


@pytest.mark.postgres
@freeze_time("2022-07-30")
async def test_complete_wordle_game_lost(postgres: AsyncSession, user: User):
    """Test completing a wordle game when you lose"""
    test_user_id = user.user_id

    stats = WordleStats(user_id=test_user_id)
    stats.current_streak = 10
    await insert_game_stats(postgres, stats)

    await crud.complete_wordle_game(postgres, test_user_id, win=False)
    stats = await crud.get_wordle_stats(postgres, test_user_id)

    # Check that streak was broken
    assert stats.current_streak == 0
    assert stats.games == 1
