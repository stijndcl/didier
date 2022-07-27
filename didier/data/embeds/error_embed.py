import traceback

import discord
from discord.ext import commands

from didier.utils.discord.constants import Limits
from didier.utils.types.string import abbreviate

__all__ = ["create_error_embed"]


def _get_traceback(exception: Exception) -> str:
    """Get a proper representation of the exception"""
    tb = traceback.format_exception(type(exception), exception, exception.__traceback__)
    error_string = ""
    for line in tb:
        # Don't add endless tracebacks
        if line.strip().startswith("The above exception was the direct cause of"):
            break

        # Escape Discord markdown formatting
        error_string += line.replace(r"*", r"\*").replace(r"_", r"\_")
        if line.strip():
            error_string += "\n"

    return abbreviate(error_string, Limits.EMBED_FIELD_VALUE_LENGTH)


def create_error_embed(ctx: commands.Context, exception: Exception) -> discord.Embed:
    """Create an embed for the traceback of an exception"""
    description = _get_traceback(exception)

    if ctx.guild is None:
        origin = "DM"
    else:
        origin = f"{ctx.channel.mention} ({ctx.guild.name})"

    invocation = f"{ctx.author.display_name} in {origin}"

    embed = discord.Embed(colour=discord.Colour.red())
    embed.set_author(name="Error")
    embed.add_field(name="Command", value=f"{ctx.message.content}", inline=True)
    embed.add_field(name="Context", value=invocation, inline=True)
    embed.add_field(name="Exception", value=abbreviate(str(exception), Limits.EMBED_FIELD_VALUE_LENGTH), inline=False)
    embed.add_field(name="Traceback", value=description, inline=False)

    return embed