from discord.ext import commands
from dislash import SlashInteraction, slash_command, Option, OptionType

from data.embeds.xkcd import XKCDEmbed
from startup.didier import Didier


class FunSlash(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    @slash_command(
        name="xkcd",
        description="Zoek xkcd comics",
        options=[
            Option(
                "num",
                description="Nummer van de comic (default de comic van vandaag).",
                type=OptionType.INTEGER,
                required=False
            )
        ]
    )
    async def _xkcd_slash(self, interaction: SlashInteraction, num: int = None):
        return await interaction.reply(embed=XKCDEmbed(num).create())


def setup(client: Didier):
    client.add_cog(FunSlash(client))
