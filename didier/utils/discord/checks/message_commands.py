from discord.ext import commands


async def is_owner(ctx: commands.Context) -> bool:
    """Check that a command is being invoked by the owner of the bot"""
    return await ctx.bot.is_owner(ctx.author)
