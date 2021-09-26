from discord.ext import commands
from dislash import SlashInteraction, slash_command, Option, OptionType, OptionChoice

from data.embeds.food import Menu, restos
from startup.didier import Didier


class SchoolSlash(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    @slash_command(
        name="eten",
        description="Menu voor een bepaalde resto op een bepaalde dag",
        options=[
            Option(
                "dag",
                description="Dag",
                type=OptionType.STRING
            ),
            Option(
                "resto",
                description="Resto",
                type=OptionType.STRING,
                choices=list(
                    OptionChoice(v, k) for k, v in restos.items()
                )
            )
        ]
    )
    async def _food_slash(self, interaction: SlashInteraction, dag: str = None, resto: str = "sterre"):
        embed = Menu(dag, resto).to_embed()
        await interaction.reply(embed=embed)


def setup(client: Didier):
    client.add_cog(SchoolSlash(client))
