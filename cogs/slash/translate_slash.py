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
            Option("from_lang", "Taal om van te vertalen (default auto-detect)", OptionType.STRING),
            Option("to_lang", "Taal om naar te vertalen (default NL)", OptionType.STRING)
        ]
    )
    async def _translate_slash(self, interaction: SlashInteraction, text: str, from_lang: str = "auto", to_lang: str = "nl"):
        translation = Translation(text=text, fr=from_lang.lower(), to=to_lang.lower())
        await interaction.reply(embed=translation.to_embed())


def setup(client: Didier):
    client.add_cog(TranslateSlash(client))
