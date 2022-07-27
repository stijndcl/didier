import pytest

from database.crud import wordle as crud
from database.mongo_types import MongoCollection, MongoDatabase
from database.schemas.mongo import WordleGame


@pytest.fixture
async def wordle_collection(mongodb: MongoDatabase) -> MongoCollection:
    """Fixture to get a reference to the wordle collection"""
    yield mongodb[WordleGame.collection()]


@pytest.fixture
async def wordle_game(wordle_collection: MongoCollection, test_user_id: int) -> WordleGame:
    """Fixture to create a new game"""
    game = WordleGame(user_id=test_user_id)
    await wordle_collection.insert_one(game.dict(by_alias=True))
    yield game


async def test_start_new_game(mongodb: MongoDatabase, wordle_collection: MongoCollection, test_user_id: int):
    """Test starting a new game"""
    result = await wordle_collection.find_one({"user_id": test_user_id})
    assert result is None

    await crud.start_new_wordle_game(mongodb, test_user_id)

    result = await wordle_collection.find_one({"user_id": test_user_id})
    assert result is not None


async def test_get_active_wordle_game_none(mongodb: MongoDatabase, test_user_id: int):
    """Test getting an active game when there is none"""
    result = await crud.get_active_wordle_game(mongodb, test_user_id)
    assert result is None


async def test_get_active_wordle_game(mongodb: MongoDatabase, wordle_game: WordleGame):
    """Test getting an active game when there is none"""
    result = await crud.get_active_wordle_game(mongodb, wordle_game.user_id)
    assert result.dict(by_alias=True) == wordle_game.dict(by_alias=True)
