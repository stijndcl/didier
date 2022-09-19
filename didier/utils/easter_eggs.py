import random
from typing import Optional

import discord
from discord.ext import commands

from database.utils.caches import EasterEggCache
from didier.utils.discord.prefix import match_prefix

__all__ = ["detect_easter_egg"]


def _roll_easter_egg(response: str) -> Optional[str]:
    """Roll a random chance for an easter egg to be responded with

    The chance for an easter egg to be used is 33%
    """
    rolled = random.randint(0, 100) < 33
    return response if rolled else None


async def detect_easter_egg(client: commands.Bot, message: discord.Message, cache: EasterEggCache) -> Optional[str]:
    """Try to detect an easter egg in a message"""
    prefix = match_prefix(client, message)

    content = message.content.strip().lower()

    # Message calls Didier
    if prefix is not None:
        prefix = prefix.strip().lower()

        # Message is only "Didier"
        if content == prefix:
            return "Hmm?"
        else:
            # Message invokes a command: do nothing
            return None

    for easter_egg in cache.easter_eggs:
        # Exact matches
        if easter_egg.exact and easter_egg.match == content:
            return _roll_easter_egg(easter_egg.response)

        # Matches that start with a certain term
        if easter_egg.startswith and content.startswith(easter_egg.match):
            return _roll_easter_egg(easter_egg.response)

    return None
