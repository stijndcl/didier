import re

from discord import Message
from discord.ext import commands

from didier.data import constants


def get_prefix(client: commands.Bot, message: Message) -> str:
    """Match a prefix against a message
    This is done dynamically to allow variable amounts of whitespace,
    and through regexes to allow case-insensitivity among other things.
    """
    mention = f"<@!?{client.user.id}>"
    regex = r"^({})\s*"

    # Check which prefix was used
    for prefix in [*constants.PREFIXES, mention]:
        match = re.match(regex.format(prefix), message.content, flags=re.I)

        if match is not None:
            # Get the part of the message that was matched
            # .group() is inconsistent with whitespace, so that can't be used
            return message.content[: match.end()]

    # Matched nothing
    return "didier"
