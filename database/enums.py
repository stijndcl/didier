import enum

__all__ = ["ReminderCategory", "TaskType"]


class ReminderCategory(enum.IntEnum):
    """Enum for reminder categories"""

    LES = enum.auto()


class TaskType(enum.IntEnum):
    """Enum for the different types of tasks"""

    BIRTHDAYS = enum.auto()
    SCHEDULES = enum.auto()
    UFORA_ANNOUNCEMENTS = enum.auto()
