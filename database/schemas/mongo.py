import datetime
from abc import ABC, abstractmethod
from typing import Optional

from bson import ObjectId
from overrides import overrides
from pydantic import BaseModel, Field, validator

from database.constants import WORDLE_GUESS_COUNT

__all__ = ["MongoBase", "TemporaryStorage", "WordleGame"]

from database.utils.datetime import today_only_date


class PyObjectId(ObjectId):
    """Custom type for bson ObjectIds"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: str):
        """Check that a string is a valid bson ObjectId"""
        if not ObjectId.is_valid(value):
            raise ValueError(f"Invalid ObjectId: '{value}'")

        return ObjectId(value)

    @classmethod
    def __modify_schema__(cls, field_schema: dict):
        field_schema.update(type="string")


class MongoBase(BaseModel):
    """Base model that properly sets the _id field, and adds one by default"""

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        """Configuration for encoding and construction"""

        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, PyObjectId: str}
        use_enum_values = True


class MongoCollection(MongoBase, ABC):
    """Base model for the 'main class' in a collection

    This field stores the name of the collection to avoid making typos against it
    """

    @staticmethod
    @abstractmethod
    def collection() -> str:
        raise NotImplementedError


class TemporaryStorage(MongoCollection):
    """Collection for lots of random things that don't belong in a full-blown collection"""

    key: str

    @staticmethod
    @overrides
    def collection() -> str:
        return "temporary"


class WordleStats(BaseModel):
    """Model that holds stats about a player's Wordle performance"""

    guess_distribution: list[int] = Field(default_factory=lambda: [0, 0, 0, 0, 0, 0])
    last_guess: Optional[datetime.date] = None
    win_rate: float = 0
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
    wordle: Optional[WordleStats] = None

    @staticmethod
    @overrides
    def collection() -> str:
        return "game_stats"


class WordleGame(MongoCollection):
    """Collection that holds people's active Wordle games"""

    day: datetime.date = Field(default_factory=lambda: today_only_date())
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