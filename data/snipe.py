from attr import dataclass
from data import regexes
import discord
from enum import Enum


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


def should_snipe(message: discord.Message) -> bool:
    """
    Check if a message should be sniped or not
    This could be a oneliner but that makes it unreadable
    """
    if message.guild is None:
        return False

    if message.author.bot:
        return False

    return not regexes.contains(message.content, regexes.STEAM_CODE)
