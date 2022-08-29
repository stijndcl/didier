from discord.ext import commands
from overrides import overrides

from didier import Didier


class TestCog(commands.Cog):
    """Testing cog for dev purposes"""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @overrides
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await self.client.is_owner(ctx.author)

    @commands.command()
    async def test(self, ctx: commands.Context):
        """Debugging command"""


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(TestCog(client))
