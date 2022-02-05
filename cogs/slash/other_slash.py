from discord.ext import commands
from discord.commands import slash_command, ApplicationContext
from requests import get

from startup.didier import Didier


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


def setup(client: Didier):
    client.add_cog(OtherSlash(client))
