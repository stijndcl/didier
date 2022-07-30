from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time

from database.crud import wordle as crud
from database.enums import TempStorageKey
from database.mongo_types import MongoCollection, MongoDatabase
from database.schemas.mongo import TemporaryStorage, WordleGame


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


@pytest.mark.mongo
async def test_start_new_game(mongodb: MongoDatabase, wordle_collection: MongoCollection, test_user_id: int):
    """Test starting a new game"""
    result = await wordle_collection.find_one({"user_id": test_user_id})
    assert result is None

    await crud.start_new_wordle_game(mongodb, test_user_id)

    result = await wordle_collection.find_one({"user_id": test_user_id})
    assert result is not None


@pytest.mark.mongo
async def test_get_active_wordle_game_none(mongodb: MongoDatabase, test_user_id: int):
    """Test getting an active game when there is none"""
    result = await crud.get_active_wordle_game(mongodb, test_user_id)
    assert result is None


@pytest.mark.mongo
async def test_get_active_wordle_game(mongodb: MongoDatabase, wordle_game: WordleGame):
    """Test getting an active game when there is one"""
    result = await crud.get_active_wordle_game(mongodb, wordle_game.user_id)
    assert result.dict(by_alias=True) == wordle_game.dict(by_alias=True)


@pytest.mark.mongo
async def test_get_daily_word_none(mongodb: MongoDatabase):
    """Test getting the daily word when the database is empty"""
    result = await crud.get_daily_word(mongodb)
    assert result is None


@pytest.mark.mongo
@freeze_time("2022-07-30")
async def test_get_daily_word_not_today(mongodb: MongoDatabase):
    """Test getting the daily word when there is an entry, but not for today"""
    day = datetime.today() - timedelta(days=1)
    collection = mongodb[TemporaryStorage.collection()]

    word = "testword"
    await collection.insert_one({"key": TempStorageKey.WORDLE_WORD, "day": day, "word": word})

    assert await crud.get_daily_word(mongodb) is None


@pytest.mark.mongo
@freeze_time("2022-07-30")
async def test_get_daily_word_present(mongodb: MongoDatabase):
    """Test getting the daily word when there is one for today"""
    day = datetime.today()
    collection = mongodb[TemporaryStorage.collection()]

    word = "testword"
    await collection.insert_one({"key": TempStorageKey.WORDLE_WORD, "day": day, "word": word})

    assert await crud.get_daily_word(mongodb) == word


@pytest.mark.mongo
@freeze_time("2022-07-30")
async def test_set_daily_word_none_present(mongodb: MongoDatabase):
    """Test setting the daily word when there is none"""
    assert await crud.get_daily_word(mongodb) is None
    word = "testword"
    await crud.set_daily_word(mongodb, word)
    assert await crud.get_daily_word(mongodb) == word


@pytest.mark.mongo
@freeze_time("2022-07-30")
async def test_set_daily_word_present(mongodb: MongoDatabase):
    """Test setting the daily word when there already is one"""
    word = "testword"
    await crud.set_daily_word(mongodb, word)
    await crud.set_daily_word(mongodb, "another word")
    assert await crud.get_daily_word(mongodb) == word


@pytest.mark.mongo
@freeze_time("2022-07-30")
async def test_set_daily_word_force_overwrite(mongodb: MongoDatabase):
    """Test setting the daily word when there already is one, but "forced" is set to True"""
    word = "testword"
    await crud.set_daily_word(mongodb, word)
    word = "anotherword"
    await crud.set_daily_word(mongodb, word, forced=True)
    assert await crud.get_daily_word(mongodb) == word


@pytest.mark.mongo
async def test_make_wordle_guess(mongodb: MongoDatabase, wordle_game: WordleGame, test_user_id: int):
    """Test making a guess in your current game"""
    guess = "guess"
    await crud.make_wordle_guess(mongodb, test_user_id, guess)
    wordle_game = await crud.get_active_wordle_game(mongodb, test_user_id)
    assert wordle_game.guesses == [guess]

    other_guess = "otherguess"
    await crud.make_wordle_guess(mongodb, test_user_id, other_guess)
    wordle_game = await crud.get_active_wordle_game(mongodb, test_user_id)
    assert wordle_game.guesses == [guess, other_guess]


@pytest.mark.mongo
async def test_reset_wordle_games(mongodb: MongoDatabase, wordle_game: WordleGame, test_user_id: int):
    """Test dropping the collection of active games"""
    assert await crud.get_active_wordle_game(mongodb, test_user_id) is not None
    await crud.reset_wordle_games(mongodb)
    assert await crud.get_active_wordle_game(mongodb, test_user_id) is None
