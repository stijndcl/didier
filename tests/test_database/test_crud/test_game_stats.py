import pytest
from freezegun import freeze_time

from database.crud import game_stats as crud
from database.mongo_types import MongoDatabase
from database.schemas.mongo.game_stats import GameStats
from database.utils.datetime import today_only_date


async def insert_game_stats(mongodb: MongoDatabase, stats: GameStats):
    """Helper function to insert some stats"""
    collection = mongodb[GameStats.collection()]
    await collection.insert_one(stats.dict(by_alias=True))


@pytest.mark.mongo
async def test_get_stats_non_existent_creates(mongodb: MongoDatabase, test_user_id: int):
    """Test getting a user's stats when the db is empty"""
    collection = mongodb[GameStats.collection()]
    assert await collection.find_one({"user_id": test_user_id}) is None
    await crud.get_game_stats(mongodb, test_user_id)
    assert await collection.find_one({"user_id": test_user_id}) is not None


@pytest.mark.mongo
async def test_get_stats_existing_returns(mongodb: MongoDatabase, test_user_id: int):
    """Test getting a user's stats when there's already an entry present"""
    stats = GameStats(user_id=test_user_id)
    stats.wordle.games = 20
    await insert_game_stats(mongodb, stats)
    found_stats = await crud.get_game_stats(mongodb, test_user_id)
    assert found_stats.wordle.games == 20


@pytest.mark.mongo
@freeze_time("2022-07-30")
async def test_complete_wordle_game_won(mongodb: MongoDatabase, test_user_id: int):
    """Test completing a wordle game when you win"""
    await crud.complete_wordle_game(mongodb, test_user_id, win=True, guesses=2)
    stats = await crud.get_game_stats(mongodb, test_user_id)
    assert stats.wordle.guess_distribution == [0, 1, 0, 0, 0, 0]
    assert stats.wordle.games == 1
    assert stats.wordle.wins == 1
    assert stats.wordle.current_streak == 1
    assert stats.wordle.max_streak == 1
    assert stats.wordle.last_win == today_only_date()


@pytest.mark.mongo
@freeze_time("2022-07-30")
async def test_complete_wordle_game_lost(mongodb: MongoDatabase, test_user_id: int):
    """Test completing a wordle game when you lose"""
    stats = GameStats(user_id=test_user_id)
    stats.wordle.current_streak = 10
    await insert_game_stats(mongodb, stats)

    await crud.complete_wordle_game(mongodb, test_user_id, win=False)
    stats = await crud.get_game_stats(mongodb, test_user_id)

    # Check that streak was broken
    assert stats.wordle.current_streak == 0
    assert stats.wordle.games == 1
    assert stats.wordle.guess_distribution == [0, 0, 0, 0, 0, 0]
