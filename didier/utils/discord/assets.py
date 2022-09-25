from typing import Union

import discord
from discord.ext import commands

__all__ = ["get_author_avatar", "get_user_avatar"]


def get_user_avatar(user: Union[discord.User, discord.Member]) -> discord.Asset:
    """Get a user's avatar asset"""
    if isinstance(user, discord.Member):
        return user.display_avatar or user.default_avatar

    return user.avatar or user.default_avatar


def get_author_avatar(ctx: Union[commands.Context, discord.Interaction]) -> discord.Asset:
    """Get the avatar asset of a command author"""
    author = ctx.author if isinstance(ctx, commands.Context) else ctx.user
    return get_user_avatar(author)
