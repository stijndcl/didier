from discord.ext import commands
from overrides import overrides

from didier import Didier


class DebugCog(commands.Cog):
    """Testing cog for dev purposes"""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @overrides
    async def cog_check(self, ctx: commands.Context) -> bool:  # type:ignore[override]
        return await self.client.is_owner(ctx.author)

    @commands.command(aliases=["Dev"])
    async def debug(self, ctx: commands.Context):
        """Debugging command"""


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(DebugCog(client))
