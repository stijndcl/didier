from discord.ext import commands
from dislash import slash_command, SlashInteraction, Option, OptionType
from functions.scrapers.google import google_search, create_google_embed
from startup.didier import Didier


class GoogleSlash(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    @slash_command(name="google",
                   description="Google search",
                   options=[
                     Option("query", "Search query", OptionType.STRING, required=True)
                   ],
                   guild_ids=[728361030404538488, 880175869841277008]
                   )
    async def _google_slash(self, interaction: SlashInteraction, query: str):
        result = google_search(query)

        if not result.results:
            return await interaction.reply("Er ging iets fout (Response {})".format(result.status_code))

        embed = create_google_embed(result)
        await interaction.reply(embed=embed)


def setup(client: Didier):
    client.add_cog(GoogleSlash(client))
