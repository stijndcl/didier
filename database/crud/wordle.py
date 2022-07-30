from typing import Optional

from database.enums import TempStorageKey
from database.mongo_types import MongoDatabase
from database.schemas.mongo import TemporaryStorage, WordleGame
from database.utils.datetime import today_only_date

__all__ = [
    "get_active_wordle_game",
    "make_wordle_guess",
    "start_new_wordle_game",
    "set_daily_word",
    "reset_wordle_games",
]


async def get_active_wordle_game(database: MongoDatabase, user_id: int) -> Optional[WordleGame]:
    """Find a player's active game"""
    collection = database[WordleGame.collection()]
    result = await collection.find_one({"user_id": user_id})
    if result is None:
        return None

    return WordleGame(**result)


async def start_new_wordle_game(database: MongoDatabase, user_id: int) -> WordleGame:
    """Start a new game"""
    collection = database[WordleGame.collection()]
    game = WordleGame(user_id=user_id)
    await collection.insert_one(game.dict(by_alias=True))
    return game


async def make_wordle_guess(database: MongoDatabase, user_id: int, guess: str):
    """Make a guess in your current game"""
    collection = database[WordleGame.collection()]
    await collection.update_one({"user_id": user_id}, {"$push": {"guesses": guess}})


async def get_daily_word(database: MongoDatabase) -> Optional[str]:
    """Get the word of today"""
    collection = database[TemporaryStorage.collection()]

    result = await collection.find_one({"key": TempStorageKey.WORDLE_WORD, "day": today_only_date()})
    if result is None:
        return None

    return result["word"]


async def set_daily_word(database: MongoDatabase, word: str, *, forced: bool = False) -> str:
    """Set the word of today

    This does NOT overwrite the existing word if there is one, so that it can safely run
    on startup every time.

    In order to always overwrite the current word, set the "forced"-kwarg to True.

    Returns the word that was chosen. If one already existed, return that instead.
    """
    collection = database[TemporaryStorage.collection()]

    current_word = None if forced else await get_daily_word(database)
    if current_word is not None:
        return current_word

    await collection.update_one(
        {"key": TempStorageKey.WORDLE_WORD}, {"$set": {"day": today_only_date(), "word": word}}, upsert=True
    )

    # Remove all active games
    await reset_wordle_games(database)

    return word


async def reset_wordle_games(database: MongoDatabase):
    """Reset all active games"""
    collection = database[WordleGame.collection()]
    await collection.drop()
