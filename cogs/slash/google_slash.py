from discord.ext import commands
from discord.commands import slash_command, ApplicationContext, Option
from functions.scrapers.google import google_search, create_google_embed
from startup.didier import Didier


class GoogleSlash(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    @slash_command(name="google", description="Google search")
    async def _google_slash(self, ctx: ApplicationContext, query: Option(str, "Search query")):
        result = google_search(query)

        if not result.results:
            return await ctx.respond("Er ging iets fout (Response {})".format(result.status_code))

        embed = create_google_embed(result)
        await ctx.respond(embed=embed)


def setup(client: Didier):
    client.add_cog(GoogleSlash(client))
