from discord.ext import commands
from dislash import SlashInteraction, slash_command, Option, OptionType

from data.embeds.urban_dictionary import Definition
from startup.didier import Didier


class DefineSlash(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    @slash_command(name="define",
                   description="Urban Dictionary",
                   options=[
                     Option("query", "Search query", OptionType.STRING, required=True)
                   ],
                   guild_ids=[728361030404538488, 880175869841277008]
                   )
    async def _define_slash(self, interaction: SlashInteraction, query):
        embed = Definition(query).to_embed()
        await interaction.reply(embed=embed)


def setup(client: Didier):
    client.add_cog(DefineSlash(client))
