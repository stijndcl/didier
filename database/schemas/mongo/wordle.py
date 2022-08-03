import datetime

from overrides import overrides
from pydantic import Field, validator

from database.constants import WORDLE_GUESS_COUNT
from database.schemas.mongo.common import MongoCollection
from database.utils.datetime import today_only_date

__all__ = ["WordleGame"]


class WordleGame(MongoCollection):
    """Collection that holds people's active Wordle games"""

    day: datetime.datetime = Field(default_factory=lambda: today_only_date())
    guesses: list[str] = Field(default_factory=list)
    user_id: int

    @staticmethod
    @overrides
    def collection() -> str:
        return "wordle"

    @validator("guesses")
    def validate_guesses_length(cls, value: list[int]):
        """Check that the amount of guesses is of the correct length"""
        if len(value) > 6:
            raise ValueError(f"guess_distribution must be no longer than 6 elements, found {len(value)}")

        return value

    def is_game_over(self, word: str) -> bool:
        """Check if the current game is over"""
        # No guesses yet
        if not self.guesses:
            return False

        # Max amount of guesses allowed
        if len(self.guesses) == WORDLE_GUESS_COUNT:
            return True

        # Found the correct word
        return self.guesses[-1] == word
