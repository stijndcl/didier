import enum

__all__ = ["TaskType"]


# There is a bug in typeshed that causes an incorrect PyCharm warning
# https://github.com/python/typeshed/issues/8286
# noinspection PyArgumentList
class TaskType(enum.IntEnum):
    """Enum for the different types of tasks"""

    BIRTHDAYS = enum.auto()
    SCHEDULES = enum.auto()
    UFORA_ANNOUNCEMENTS = enum.auto()
