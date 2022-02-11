from discord.ext import commands
from discord.commands import slash_command, ApplicationContext, AutocompleteContext, Option
from requests import get

from data.links import load_all_links, get_link_for
from startup.didier import Didier

links = load_all_links()


def link_autocomplete(ctx: AutocompleteContext) -> list[str]:
    return [link for link in links if link.lower().startswith(ctx.value.lower())]


class OtherSlash(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    @slash_command(name="inspire", description="Genereer quotes via Inspirobot.")
    async def _inspire_slash(self, ctx: ApplicationContext):
        image = get("https://inspirobot.me/api?generate=true")

        if image.status_code == 200:
            await ctx.respond(image.text)
        else:
            await ctx.respond("Uh oh API down.")

    @slash_command(name="link", description="Shortcut voor nuttige links.")
    async def _link_slash(self, ctx: ApplicationContext,
                          name: Option(str, description="Naam van de link.", required=True,
                                       autocomplete=link_autocomplete)):
        match = get_link_for(name)

        if match is None:
            return await ctx.respond(f"Geen match gevonden voor \"{name}\".")

        return await ctx.respond(match)


def setup(client: Didier):
    client.add_cog(OtherSlash(client))
