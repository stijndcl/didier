from enum import Enum

from attr import dataclass


class Action(Enum):
    """
    Enum to indicate what action was performed by the user
    """
    Edit = 0
    Remove = 1


@dataclass
class Snipe:
    """
    Dataclass to store Snipe info
    """
    user: int
    channel: int
    guild: int
    action: Action
    old: str
    new: str = None
