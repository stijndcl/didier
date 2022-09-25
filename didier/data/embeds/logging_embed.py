import logging

import discord

from didier.utils.discord.constants import Limits
from didier.utils.types.string import abbreviate

__all__ = ["create_logging_embed"]


def create_logging_embed(level: int, message: str) -> discord.Embed:
    """Create an embed to send to the logging channel"""
    colours = {
        logging.DEBUG: discord.Colour.light_gray,
        logging.ERROR: discord.Colour.red(),
        logging.INFO: discord.Colour.blue(),
        logging.WARNING: discord.Colour.yellow(),
    }

    colour = colours.get(level, discord.Colour.red())
    embed = discord.Embed(colour=colour, title="Logging")
    embed.description = abbreviate(message, Limits.EMBED_DESCRIPTION_LENGTH)

    return embed
