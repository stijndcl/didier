from discord.ext import commands
from discord.commands import slash_command, ApplicationContext, Option

from data.embeds.xkcd import XKCDEmbed
from startup.didier import Didier


class FunSlash(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    @slash_command(name="xkcd", description="Zoek xkcd comics")
    async def _xkcd_slash(self, ctx: ApplicationContext,
                          num: Option(int, description="Nummer van de comic (default de comic van vandaag).", required=False, default=None)
                          ):
        return await ctx.respond(embed=XKCDEmbed(num).create())


def setup(client: Didier):
    client.add_cog(FunSlash(client))
