from abc import ABC, abstractmethod

from discord import app_commands
from overrides import overrides
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import links, memes, ufora_courses, wordle

__all__ = ["CacheManager", "LinkCache", "UforaCourseCache"]


class DatabaseCache(ABC):
    """Base class for a simple cache-like structure

    The goal of this class is to store data for Discord auto-completion results
    that would otherwise potentially put heavy load on the database.

    This only stores strings, to avoid having to constantly refresh these objects.
    Once a choice has been made, it can just be pulled out of the database.

    Considering the fact that a user isn't obligated to choose something from the suggestions,
    chances are high we have to go to the database for the final action either way.

    Also stores the data in lowercase to allow fast searching.
    """

    data: list[str] = []
    data_transformed: list[str] = []

    def clear(self):
        """Remove everything"""
        self.data.clear()

    @abstractmethod
    async def invalidate(self, database_session: AsyncSession):
        """Invalidate the data stored in this cache"""

    def get_autocomplete_suggestions(self, query: str) -> list[app_commands.Choice[str]]:
        """Filter the cache to find everything that matches the search query"""
        query = query.lower()
        # Return the original (non-transformed) version of the data for pretty display in Discord
        suggestions = [self.data[index] for index, value in enumerate(self.data_transformed) if query in value]

        return [app_commands.Choice(name=suggestion, value=suggestion.lower()) for suggestion in suggestions]


class LinkCache(DatabaseCache):
    """Cache to store the names of links"""

    @overrides
    async def invalidate(self, database_session: AsyncSession):
        self.clear()

        all_links = await links.get_all_links(database_session)
        self.data = list(map(lambda l: l.name, all_links))
        self.data.sort()
        self.data_transformed = list(map(str.lower, self.data))


class MemeCache(DatabaseCache):
    """Cache to store the names of meme templates"""

    @overrides
    async def invalidate(self, database_session: AsyncSession):
        self.clear()

        all_memes = await memes.get_all_memes(database_session)
        self.data = list(map(lambda m: m.name, all_memes))
        self.data.sort()
        self.data_transformed = list(map(str.lower, self.data))


class UforaCourseCache(DatabaseCache):
    """Cache to store the names of Ufora courses"""

    # Also store the aliases to add additional support
    aliases: dict[str, str] = {}

    @overrides
    def clear(self):
        self.aliases.clear()
        super().clear()

    @overrides
    async def invalidate(self, database_session: AsyncSession):
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
    def get_autocomplete_suggestions(self, query: str) -> list[app_commands.Choice[str]]:
        query = query.lower()
        results = set()

        # Return the original (not-lowercase) version
        for index, course in enumerate(self.data_transformed):
            if query in course:
                results.add(self.data[index])

        for alias, course in self.aliases.items():
            if query in alias:
                results.add(course)

        suggestions = sorted(list(results))
        return [app_commands.Choice(name=suggestion, value=suggestion.lower()) for suggestion in suggestions]


class WordleCache(DatabaseCache):
    """Cache to store the current daily Wordle word"""

    async def invalidate(self, database_session: AsyncSession):
        word = await wordle.get_daily_word(database_session)
        if word is not None:
            self.data = [word]


class CacheManager:
    """Class that keeps track of all caches"""

    links: LinkCache
    memes: MemeCache
    ufora_courses: UforaCourseCache
    wordle_word: WordleCache

    def __init__(self):
        self.links = LinkCache()
        self.memes = MemeCache()
        self.ufora_courses = UforaCourseCache()
        self.wordle_word = WordleCache()

    async def initialize_caches(self, postgres_session: AsyncSession):
        """Initialize the contents of all caches"""
        await self.links.invalidate(postgres_session)
        await self.memes.invalidate(postgres_session)
        await self.ufora_courses.invalidate(postgres_session)
        await self.wordle_word.invalidate(postgres_session)
