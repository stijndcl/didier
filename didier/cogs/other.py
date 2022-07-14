from discord.ext import commands

from didier import Didier
from didier.data.apis import urban_dictionary


class Other(commands.Cog):
    """Cog for commands that don't really belong anywhere else"""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @commands.hybrid_command(name="define", description="Urban Dictionary", aliases=["Ud", "Urban"], usage="[Woord]")
    async def define(self, ctx: commands.Context, *, query: str):
        """Look up the definition of a word on the Urban Dictionary"""
        definitions = await urban_dictionary.lookup(self.client.http_session, query)
        await ctx.reply(embed=definitions[0].to_embed(), mention_author=False)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Other(client))
