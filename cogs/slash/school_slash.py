from discord.ext import commands
from dislash import SlashInteraction, slash_command, Option, OptionType

from data.embeds.food import Menu
from startup.didier import Didier


class SchoolSlash(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    @slash_command(
        name="eten",
        description="Menu in de UGENT resto's op een bepaalde dag",
        options=[
            Option(
                "dag",
                description="Dag",
                type=OptionType.STRING
            )
        ]
    )
    async def _food_slash(self, interaction: SlashInteraction, dag: str = None):
        embed = Menu(dag).to_embed()
        await interaction.reply(embed=embed)


def setup(client: Didier):
    client.add_cog(SchoolSlash(client))
