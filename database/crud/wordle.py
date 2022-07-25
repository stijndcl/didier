from typing import Optional

from database.mongo_types import MongoCollection
from database.schemas.mongo import WordleGame

__all__ = ["get_active_wordle_game", "make_wordle_guess", "start_new_wordle_game"]


async def get_active_wordle_game(collection: MongoCollection, user_id: int) -> Optional[WordleGame]:
    """Find a player's active game"""
    return await collection.find_one({"user_id": user_id})


async def start_new_wordle_game(collection: MongoCollection, user_id: int, word: str) -> WordleGame:
    """Start a new game"""
    game = WordleGame(user_id=user_id, word=word)
    await collection.insert_one(game.dict(by_alias=True))
    return game


async def make_wordle_guess(collection: MongoCollection, user_id: int, guess: str):
    """Make a guess in your current game"""
    await collection.update_one({"user_id": user_id}, {"$push": {"guesses": guess}})
