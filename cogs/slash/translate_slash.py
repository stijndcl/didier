from discord.ext import commands
from discord.commands import slash_command, ApplicationContext, Option

from data.embeds.translate import Translation
from startup.didier import Didier


class TranslateSlash(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    @slash_command(name="translate", description="Google Translate")
    async def _translate_slash(self, ctx: ApplicationContext,
                               text: Option(str, description="Tekst om te vertalen"),
                               from_lang: Option(str, description="Taal om van te vertalen (default auto-detect)", default="auto"),
                               to_lang: Option(str, description="Taal om naar te vertalen (default NL)", default="nl")
                               ):
        translation = Translation(text=text, fr=from_lang.lower(), to=to_lang.lower())
        await ctx.respond(embed=translation.to_embed())


def setup(client: Didier):
    client.add_cog(TranslateSlash(client))
