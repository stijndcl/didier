import datetime
from typing import Union

from database.mongo_types import MongoDatabase
from database.schemas.mongo.game_stats import GameStats

__all__ = ["get_game_stats", "complete_wordle_game"]

from database.utils.datetime import today_only_date


async def get_game_stats(database: MongoDatabase, user_id: int) -> GameStats:
    """Get a user's game stats

    If no entry is found, it is first created
    """
    collection = database[GameStats.collection()]
    stats = await collection.find_one({"user_id": user_id})
    if stats is not None:
        return GameStats(**stats)

    stats = GameStats(user_id=user_id)
    await collection.insert_one(stats.dict(by_alias=True))
    return stats


async def complete_wordle_game(database: MongoDatabase, user_id: int, win: bool, guesses: int):
    """Update the user's Wordle stats"""
    stats = await get_game_stats(database, user_id)

    update: dict[str, dict[str, Union[int, datetime.datetime]]] = {"$inc": {"wordle.games": 1}}

    if win:
        update["$inc"]["wordle.wins"] = 1
        update["$inc"][f"wordle.guess_distribution.{guesses}"] = 1

        # Update streak
        today = today_only_date()
        last_win = stats.wordle.last_win
        update["$set"]["wordle.last_win"] = today

        if last_win is None or (today - last_win).days > 1:
            # Never won a game before or streak is over
            update["$set"]["wordle.current_streak"] = 1
            stats.wordle.current_streak = 1
        else:
            # On a streak: increase counter
            update["$inc"]["wordle.current_streak"] = 1
            stats.wordle.current_streak += 1

        # Update max streak if necessary
        if stats.wordle.current_streak > stats.wordle.max_streak:
            update["$set"]["wordle.max_streak"] = stats.wordle.current_streak
    else:
        # Streak is over
        update["$set"]["wordle.current_streak"] = 0

    collection = database[GameStats.collection()]
    collection.update_one({"_id": stats.id}, update)
