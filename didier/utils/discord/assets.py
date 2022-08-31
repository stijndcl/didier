from typing import Union

import discord
from discord.ext import commands

__all__ = ["get_author_avatar"]


def get_author_avatar(ctx: Union[commands.Context, discord.Interaction]) -> discord.Asset:
    """Get a user's avatar asset"""
    author = ctx.author if isinstance(ctx, commands.Context) else ctx.user
    return author.avatar or author.default_avatar
