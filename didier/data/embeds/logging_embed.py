import logging

import discord

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
    embed.description = message

    return embed
