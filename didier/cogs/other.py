from discord.ext import commands

from didier import Didier
from didier.data.apis import urban_dictionary


class Other(commands.Cog):
    """Cog for commands that don't really belong anywhere else"""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @commands.command(name="Define", aliases=["Ud", "Urban"], usage="[Woord]")
    async def define(self, ctx: commands.Context, *, query: str):
        """Look up the definition of a word on the Urban Dictionary"""
        definitions = urban_dictionary.lookup(self.client.http_session, query)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Other(client))
