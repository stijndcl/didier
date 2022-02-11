from discord.ext import commands
from discord.commands import slash_command, ApplicationContext, Option, AutocompleteContext

from functions.database import memes
from functions.database.memes import getAllMemes
from data.embeds.xkcd import XKCDEmbed
from data.menus.memes import MemesList
from functions.memes import generate
from functions.stringFormatters import title_case
from startup.didier import Didier


all_memes = getAllMemes()


def autocomplete_memes(ctx: AutocompleteContext) -> list[str]:
    starting = []
    containing = []

    val = ctx.value.lower()

    # First show matches that start with this word, then matches that contain it
    for meme in all_memes:
        if meme[1].startswith(val):
            starting.append(title_case(meme[1]))
        elif val in meme[1]:
            containing.append(title_case(meme[1]))

    return [*starting, *containing]


class FunSlash(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    @slash_command(name="xkcd", description="Zoek xkcd comics")
    async def _xkcd_slash(self, ctx: ApplicationContext,
                          num: Option(int, description="Nummer van de comic (default de comic van vandaag).", required=False, default=None)
                          ):
        return await ctx.respond(embed=XKCDEmbed(num).create())

    @slash_command(name="memes", description="Lijst van memegen-memes")
    async def _memes_slash(self, ctx: ApplicationContext):
        return await MemesList(ctx=ctx).respond()

    @slash_command(name="memegen", description="Genereer memes")
    async def _memegen_slash(self, ctx: ApplicationContext,
                             meme: Option(str, description="Naam van de template", required=True, autocomplete=autocomplete_memes),
                             field1: Option(str, required=True),
                             field2: Option(str, required=False, default=""),
                             field3: Option(str, required=False, default=""),
                             field4: Option(str, required=False, default="")):
        # Get the meme info that corresponds to this name
        result: memes.Meme = memes.getMeme(meme)

        # No meme found
        if result is None:
            return await ctx.respond("Deze meme staat niet in de database.", ephemeral=True)

        await ctx.response.defer()

        fields = (field1, field2, field3, field4)
        generated = generate(result, fields)

        # Send generated meme or error message
        await ctx.send_followup(generated["message"])


def setup(client: Didier):
    client.add_cog(FunSlash(client))
