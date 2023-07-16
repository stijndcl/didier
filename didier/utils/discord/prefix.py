import re
from typing import Optional

from discord import Message
from discord.ext import commands

from didier.data import constants

__all__ = ["get_prefix", "match_prefix"]


def match_prefix(client: commands.Bot, message: Message) -> Optional[str]:
    """Try to match a prefix against a message, returning None instead of a default value

    This is done dynamically through regexes to allow case-insensitivity
    and variable amounts of whitespace among other things.
    """
    mention = f"<@!?{client.user.id}>" if client.user else None
    regex = r"^({})\s*"

    # Check which prefix was used
    for prefix in [*constants.PREFIXES, mention]:
        if prefix is None:
            continue

        match = re.match(regex.format(prefix), message.content, flags=re.I)

        if match is not None:
            # Get the part of the message that was matched
            # .group() is inconsistent with whitespace, so that can't be used
            return message.content[: match.end()]

    return None


def get_prefix(client: commands.Bot, message: Message) -> str:
    """Match a prefix against a message, with a fallback

    This is the main prefix function that is used by the bot
    """
    # If nothing was matched, return "didier" as a fallback
    return match_prefix(client, message) or "didier"
