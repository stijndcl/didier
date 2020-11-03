from data.constants import prefixes
from discord.ext import commands
import os


fallback = os.urandom(32).hex()


def get_prefix(bot: commands.Bot, message):
    content = message.content.lower()
    mention = "<@!{}>".format(bot.user.id)

    # Used @Didier
    if content.startswith(mention):
        if content.startswith(mention + " "):
            return mention + " "
        return mention

    # Used a prefix
    for prefix in prefixes:
        # Find correct prefix
        if content.startswith(prefix):
            # Check if a space has to be added to invoke commands
            if content.startswith(prefix + " "):
                return prefix + " "
            return prefix

    return fallback
