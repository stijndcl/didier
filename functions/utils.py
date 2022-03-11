from typing import Union, Optional

import discord
from discord import ApplicationContext
from discord.ext.commands import Context

import settings


def get_member_or_user(ctx: Union[ApplicationContext, Context], user_id: int) -> Optional[Union[discord.Member, discord.User]]:
    """Get a COC Member instance of a user if they are in the server,
    otherwise the regular User instance
    """
    author = ctx.author if isinstance(ctx, Context) else ctx.user

    # Check if this is a DM, or the user is not in the guild
    if ctx.guild is None or ctx.guild.get_member(user_id) is None:
        # User is the author, no need to fetch their name
        if user_id == author.id:
            return author

        # Get member instance from CoC
        COC = ctx.bot.get_guild(settings.COC_ID)
        member = COC.get_member(user_id)
        if member is not None:
            return member

        # Try to fetch the user
        user = ctx.bot.get_user(user_id)
        return user

    # Guild exists, use that instead
    mem = ctx.guild.get_member(user_id)
    return mem


def get_display_name(ctx: Union[ApplicationContext, Context], user_id: int) -> str:
    member = get_member_or_user(ctx, user_id)

    # Nothing found
    if member is None:
        return f"[? | {user_id}]"

    if isinstance(member, discord.Member):
        return member.display_name

    return member.name


def get_mention(ctx: Union[ApplicationContext, Context], user_id: int) -> str:
    member = get_member_or_user(ctx, user_id)

    # Nothing found
    if member is None:
        return f"[? | {user_id}]"

    return member.mention


async def reply_to_reference(ctx: Context, content: Optional[str] = None, embed: Optional[discord.Embed] = None, always_mention=False):
    """Reply to a message
    In case the message is a reply to another message, try to reply to that one instead and ping the author
    otherwise, reply to the message that invoked the command & only mention the author if necessary
    """
    # Message is a reply
    if ctx.message.reference is not None:
        cached = ctx.message.reference.cached_message

        # Reference is not cached anymore: fetch it
        if cached is None:
            # Message is in the same channel, otherwise no way to reply to it
            cached = await ctx.channel.fetch_message(ctx.message.reference.message_id)

        return await cached.reply(content, embed=embed, mention_author=cached.author != ctx.author)

    return await ctx.reply(content, embed=embed, mention_author=always_mention)
