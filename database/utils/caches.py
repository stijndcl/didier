from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from overrides import overrides
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import ufora_courses, wordle
from database.mongo_types import MongoDatabase

__all__ = ["CacheManager", "UforaCourseCache"]

T = TypeVar("T")


class DatabaseCache(ABC, Generic[T]):
    """Base class for a simple cache-like structure

    The goal of this class is to store data for Discord auto-completion results
    that would otherwise potentially put heavy load on the database.

    This only stores strings, to avoid having to constantly refresh these objects.
    Once a choice has been made, it can just be pulled out of the database.

    Considering the fact that a user isn't obligated to choose something from the suggestions,
    chances are high we have to go to the database for the final action either way.

    Also stores the data in lowercase to allow fast searching
    """

    data: list[str] = []
    data_transformed: list[str] = []

    def clear(self):
        """Remove everything"""
        self.data.clear()

    @abstractmethod
    async def refresh(self, database_session: T):
        """Refresh the data stored in this cache"""

    async def invalidate(self, database_session: T):
        """Invalidate the data stored in this cache"""
        await self.refresh(database_session)

    def get_autocomplete_suggestions(self, query: str):
        """Filter the cache to find everything that matches the search query"""
        query = query.lower()
        # Return the original (non-transformed) version of the data for pretty display in Discord
        return [self.data[index] for index, value in enumerate(self.data_transformed) if query in value]


class UforaCourseCache(DatabaseCache[AsyncSession]):
    """Cache to store the names of Ufora courses"""

    # Also store the aliases to add additional support
    aliases: dict[str, str] = {}

    @overrides
    def clear(self):
        self.aliases.clear()
        super().clear()

    @overrides
    async def refresh(self, database_session: AsyncSession):
        self.clear()

        courses = await ufora_courses.get_all_courses(database_session)

        self.data = list(map(lambda c: c.name, courses))

        # Load the aliases
        for course in courses:
            for alias in course.aliases:
                # Store aliases in lowercase
                self.aliases[alias.alias.lower()] = course.name

        self.data.sort()
        self.data_transformed = list(map(str.lower, self.data))

    @overrides
    def get_autocomplete_suggestions(self, query: str):
        query = query.lower()
        results = set()

        # Return the original (not-lowercase) version
        for index, course in enumerate(self.data_transformed):
            if query in course:
                results.add(self.data[index])

        for alias, course in self.aliases.items():
            if query in alias:
                results.add(course)

        return sorted(list(results))


class WordleCache(DatabaseCache[MongoDatabase]):
    """Cache to store the current daily Wordle word"""

    async def refresh(self, database_session: MongoDatabase):
        word = await wordle.get_daily_word(database_session)
        if word is not None:
            self.data = [word]


class CacheManager:
    """Class that keeps track of all caches"""

    ufora_courses: UforaCourseCache
    wordle_word: WordleCache

    def __init__(self):
        self.ufora_courses = UforaCourseCache()
        self.wordle_word = WordleCache()

    async def initialize_caches(self, postgres_session: AsyncSession, mongo_db: MongoDatabase):
        """Initialize the contents of all caches"""
        await self.ufora_courses.refresh(postgres_session)
        await self.wordle_word.refresh(mongo_db)
