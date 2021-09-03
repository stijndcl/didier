from discord.ext import commands
from dislash import SlashInteraction, slash_command, Option, OptionType

from data.embeds.translate import Translation
from startup.didier import Didier


class TranslateSlash(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    @slash_command(
        name="translate",
        description="Google Translate",
        options=[
            Option("text", "Tekst om te vertalen", OptionType.STRING, required=True),
            Option("to", "Taal om naar te vertalen (default NL)", OptionType.STRING)
        ]
    )
    async def _translate_slash(self, interaction: SlashInteraction, text: str, to: str = "nl"):
        translation = Translation(text=text, to=to.lower())
        await interaction.reply(embed=translation.to_embed())


def setup(client: Didier):
    client.add_cog(TranslateSlash(client))
