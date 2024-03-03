from discord.ext import commands

from didier import Didier


class Leaderboards(commands.Cog):
    """Cog for various leaderboards"""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @commands.hybrid_group(name="leaderboard", aliases=["lb"], invoke_without_command=True)
    async def leaderboard(self, ctx: commands.Context):
        """List the top X for a given category"""
        # TODO

    @leaderboard.command(name="dinks", aliases=["d"])
    async def dinks(self, ctx: commands.Context):
        """See the users with the most Didier Dinks"""
        # TODO


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Leaderboards(client))
