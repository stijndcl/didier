from typing import Union

from discord import ApplicationContext
from discord.ext.commands import Context

from data import constants


def get_display_name(ctx: Union[ApplicationContext, Context], user_id: int) -> str:
    author = ctx.author if isinstance(ctx, Context) else ctx.user

    # Check if this is a DM, or the user is not in the guild
    if ctx.guild is None or ctx.guild.get_member(user_id) is None:
        # User is the author, no need to fetch their name
        if user_id == author.id:
            return author.display_name

        # Get member instance from CoC
        COC = ctx.bot.get_guild(int(constants.DeZandbak))
        member = COC.get_member(user_id)
        if member is not None:
            return member.display_name

        # Try to fetch the user
        user = ctx.bot.get_user(user_id)
        if user is not None:
            return user.name

        # User couldn't be found
        return f"[? | {user_id}]"

    mem = ctx.guild.get_member(user_id)
    return mem.display_name
