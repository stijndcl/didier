import random
import re
from typing import Optional

import discord
from discord.ext import commands

import settings
from database.utils.caches import EasterEggCache
from didier.utils.discord.prefix import match_prefix

__all__ = ["detect_easter_egg"]


def _roll_easter_egg(response: str) -> Optional[str]:
    """Roll a random chance for an easter egg to be responded with"""
    rolled = random.randint(0, 100) < settings.EASTER_EGG_CHANCE
    return response if rolled else None


async def detect_easter_egg(client: commands.Bot, message: discord.Message, cache: EasterEggCache) -> Optional[str]:
    """Try to detect an easter egg in a message"""
    prefix = match_prefix(client, message)

    # Remove markdown and whitespace for better matches
    content = message.content.strip().strip("_* \t\n").lower()

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
        pattern = easter_egg.match

        # Use regular expressions to easily allow slight variations
        if easter_egg.exact:
            pattern = rf"^{pattern}$"
        elif easter_egg.startswith:
            pattern = rf"^{pattern}"

        matched = re.search(pattern, content)

        if matched is not None:
            return _roll_easter_egg(easter_egg.response)

    return None
