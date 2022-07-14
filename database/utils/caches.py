from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import ufora_courses

__all__ = ["CacheManager"]


class DatabaseCache(ABC):
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
    async def refresh(self, database_session: AsyncSession):
        """Refresh the data stored in this cache"""

    async def invalidate(self, database_session: AsyncSession):
        """Invalidate the data stored in this cache"""
        await self.refresh(database_session)

    def get_autocomplete_suggestions(self, query: str):
        """Filter the cache to find everything that matches the search query"""
        query = query.lower()
        # Return the original (non-transformed) version of the data for pretty display in Discord
        return [self.data[index] for index, value in enumerate(self.data_transformed) if query in value]


class UforaCourseCache(DatabaseCache):
    """Cache to store the names of Ufora courses"""

    async def refresh(self, database_session: AsyncSession):
        self.clear()

        courses = await ufora_courses.get_all_courses(database_session)

        # Load the course names + all the aliases
        for course in courses:
            aliases = list(map(lambda x: x.alias, course.aliases))
            self.data.extend([course.name, *aliases])

        self.data.sort()
        self.data_transformed = list(map(str.lower, self.data))


class CacheManager:
    """Class that keeps track of all caches"""

    ufora_courses: UforaCourseCache

    def __init__(self):
        self.ufora_courses = UforaCourseCache()

    async def initialize_caches(self, database_session: AsyncSession):
        """Initialize the contents of all caches"""
        await self.ufora_courses.refresh(database_session)
