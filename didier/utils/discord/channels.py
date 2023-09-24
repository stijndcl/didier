import discord

__all__ = ["NON_MESSAGEABLE_CHANNEL_TYPES"]

NON_MESSAGEABLE_CHANNEL_TYPES = (discord.ForumChannel, discord.CategoryChannel, discord.abc.PrivateChannel)
