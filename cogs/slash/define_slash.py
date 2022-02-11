from discord.ext import commands
from discord.commands import slash_command, ApplicationContext, Option

from data.embeds.urban_dictionary import Definition
from startup.didier import Didier


class DefineSlash(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    @slash_command(name="define", description="Urban Dictionary")
    async def _define_slash(self, ctx: ApplicationContext, query: Option(str, "Search query", required=True)):
        embed = Definition(query).to_embed()
        await ctx.respond(embed=embed)


def setup(client: Didier):
    client.add_cog(DefineSlash(client))
