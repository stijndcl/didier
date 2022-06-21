from typing import Optional

import discord
from discord.ext import commands

from didier import Didier


class Owner(commands.Cog):
    """Cog for owner-only commands"""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @commands.command(name="Sync")
    @commands.is_owner()
    async def sync(self, ctx: commands.Context, guild: Optional[discord.Guild] = None):
        """Sync all application-commands in Discord"""
        await self.client.tree.sync(guild=guild)
        await ctx.message.add_reaction("🔄")


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Owner(client))
