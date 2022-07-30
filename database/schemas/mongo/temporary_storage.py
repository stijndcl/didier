from overrides import overrides

from database.schemas.mongo.common import MongoCollection

__all__ = ["TemporaryStorage"]


class TemporaryStorage(MongoCollection):
    """Collection for lots of random things that don't belong in a full-blown collection"""

    key: str

    @staticmethod
    @overrides
    def collection() -> str:
        return "temporary"
