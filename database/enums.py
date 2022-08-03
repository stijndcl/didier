import enum

__all__ = ["TaskType", "TempStorageKey"]


# There is a bug in typeshed that causes an incorrect PyCharm warning
# https://github.com/python/typeshed/issues/8286
# noinspection PyArgumentList
class TaskType(enum.IntEnum):
    """Enum for the different types of tasks"""

    BIRTHDAYS = enum.auto()
    UFORA_ANNOUNCEMENTS = enum.auto()


@enum.unique
class TempStorageKey(str, enum.Enum):
    """Enum for keys to distinguish the TemporaryStorage rows"""

    WORDLE_WORD = "wordle_word"
