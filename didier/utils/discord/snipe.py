import discord

from didier.utils.regexes import STEAM_CODE

__all__ = ["should_snipe"]


def should_snipe(message: discord.Message) -> bool:
    """Check if a message should be sniped or not"""
    # Don't snipe DM's
    if message.guild is None:
        return False

    # Don't snipe bots
    if message.author.bot:
        return False

    return not STEAM_CODE.is_in(message.content)
