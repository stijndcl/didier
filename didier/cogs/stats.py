from typing import Optional

import discord
from discord.ext import commands

from database.crud.cf_stats import get_cf_stats
from didier import Didier


class Stats(commands.Cog):
    """Cog for various stats that Didier tracks"""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @commands.hybrid_group(name="stats", invoke_without_command=True)
    async def stats(self, ctx: commands.Context):
        """See stats about yourself or another user"""

    @stats.command(name="cf", aliases=["coinflip"])
    async def _cf_stats(self, ctx: commands.Context, user: Optional[discord.User] = None):
        """See a user's `Didier CF` stats"""
        async with ctx.typing(), self.client.postgres_session as session:
            user = user or ctx.author
            cf_stats = await get_cf_stats(session, user.id)

        embed = discord.Embed(title="Didier CF Stats", colour=discord.Colour.blue())
        embed.set_author(name=user.display_name)

        if user.avatar is not None:
            embed.set_thumbnail(url=user.avatar.url)

        played = cf_stats.games_won + cf_stats.games_lost

        if played == 0:
            return await ctx.reply("This user hasn't played any games yet.", mention_author=False)

        embed.add_field(name="Games played", value=played)
        embed.add_field(
            name="Winrate", value=f"{round(100 * cf_stats.games_won / played, 2)}% ({cf_stats.games_won}/{played})"
        )

        embed.add_field(name="Dinks won", value=cf_stats.dinks_won)
        embed.add_field(name="Dinks lost", value=cf_stats.dinks_lost)
        embed.add_field(name="Profit", value=cf_stats.dinks_won - cf_stats.dinks_lost)

        await ctx.reply(embed=embed, mention_author=False)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Stats(client))
