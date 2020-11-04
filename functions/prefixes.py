from data.constants import prefixes
from discord.ext import commands
import os
import re


fallback = os.urandom(32).hex()


def get_prefix(bot: commands.Bot, message):
    mention = "<@!{}>".format(bot.user.id)
    regex = r"^({})\s*"

    # Check which prefix was used
    for prefix in [*prefixes, mention]:
        r = re.compile(regex.format(prefix), flags=re.I)
        m = r.match(message.content)
        if m:
            # match.group() randomly ignores whitespace for some reason
            # so use string slicing
            return message.content[:m.end()]

    return fallback
