from discord import app_commands
from discord.ext import commands

from didier import Didier
from didier.data.apis import urban_dictionary
from didier.data.embeds.google import GoogleSearch
from didier.data.scrapers import google


class Other(commands.Cog):
    """Cog for commands that don't really belong anywhere else"""

    client: Didier

    def __init__(self, client: Didier):
        self.client = client

    @commands.hybrid_command(name="define", description="Urban Dictionary", aliases=["Ud", "Urban"], usage="[Term]")
    async def define(self, ctx: commands.Context, *, query: str):
        """Look up the definition of a word on the Urban Dictionary"""
        async with ctx.typing():
            status_code, definitions = await urban_dictionary.lookup(self.client.http_session, query)
            if not definitions:
                return await ctx.reply(f"Something went wrong (status {status_code})")

            await ctx.reply(embed=definitions[0].to_embed(), mention_author=False)

    @commands.hybrid_command(name="google", description="Google search", usage="[Query]")
    @app_commands.describe(query="Search query")
    async def google(self, ctx: commands.Context, *, query: str):
        """Google something"""
        async with ctx.typing():
            results = await google.google_search(self.client.http_session, query)
            embed = GoogleSearch(results).to_embed()
            await ctx.reply(embed=embed, mention_author=False)


async def setup(client: Didier):
    """Load the cog"""
    await client.add_cog(Other(client))
