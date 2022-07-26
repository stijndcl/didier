from typing import Optional

from database.enums import TempStorageKey
from database.mongo_types import MongoCollection
from database.schemas.mongo import WordleGame
from database.utils.datetime import today_only_date

__all__ = ["get_active_wordle_game", "make_wordle_guess", "start_new_wordle_game"]


async def get_active_wordle_game(collection: MongoCollection, user_id: int) -> Optional[WordleGame]:
    """Find a player's active game"""
    return await collection.find_one({"user_id": user_id})


async def start_new_wordle_game(collection: MongoCollection, user_id: int) -> WordleGame:
    """Start a new game"""
    game = WordleGame(user_id=user_id)
    await collection.insert_one(game.dict(by_alias=True))
    return game


async def make_wordle_guess(collection: MongoCollection, user_id: int, guess: str):
    """Make a guess in your current game"""
    await collection.update_one({"user_id": user_id}, {"$push": {"guesses": guess}})


async def get_daily_word(collection: MongoCollection) -> Optional[str]:
    """Get the word of today"""
    result = await collection.find_one({"key": TempStorageKey.WORDLE_WORD, "day": today_only_date()})
    if result is None:
        return None

    return result["word"]


async def set_daily_word(collection: MongoCollection, word: str):
    """Set the word of today

    This does NOT overwrite the existing word if there is one, so that it can safely run
    on startup every time
    """
    current_word = await get_daily_word(collection)
    if current_word is not None:
        return

    await collection.update_one(
        {"key": TempStorageKey.WORDLE_WORD}, {"day": today_only_date(), "word": word}, upsert=True
    )
