import datetime
from typing import Optional

from overrides import overrides
from pydantic import BaseModel, Field, validator

from database.schemas.mongo.common import MongoCollection

__all__ = ["GameStats", "WordleStats"]


class WordleStats(BaseModel):
    """Model that holds stats about a player's Wordle performance"""

    guess_distribution: list[int] = Field(default_factory=lambda: [0, 0, 0, 0, 0, 0])
    last_win: Optional[datetime.datetime] = None
    wins: int = 0
    games: int = 0
    current_streak: int = 0
    max_streak: int = 0

    @validator("guess_distribution")
    def validate_guesses_length(cls, value: list[int]):
        """Check that the distribution of guesses is of the correct length"""
        if len(value) != 6:
            raise ValueError(f"guess_distribution must be length 6, found {len(value)}")

        return value


class GameStats(MongoCollection):
    """Collection that holds stats about how well a user has performed in games"""

    user_id: int
    wordle: WordleStats = WordleStats()

    @staticmethod
    @overrides
    def collection() -> str:
        return "game_stats"
