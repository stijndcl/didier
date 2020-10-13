from data import constants
from discord.ext import commands


# Cog that handles failure of checks
# Has to be a Cog to have access to the Client
class FailedChecks(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.utilsCog = self.client.get_cog("Utils")

    # User posted in #FreeGames without being allowed to do so
    async def freeGames(self, ctx):
        content = ctx.content
        errorChannel = self.client.get_channel(int(constants.ErrorLogs))

        await self.utilsCog.removeMessage(ctx)
        await self.utilsCog.sendDm(ctx.author.id,
                                   "Je bericht \n`{}`\n werd verwijderd uit #FreeGames omdat het geen link "
                                   "bevatte.\nPost AUB enkel links in dit kanaal.\n*Als je bericht onterecht "
                                   "verwijderd werd, stuur dan een DM naar DJ STIJN.*".format(content))
        await errorChannel.send("`{}`\nDoor **{}** werd verwijderd uit #FreeGames.".format(content,
                                                                                           ctx.author.display_name))


def setup(client):
    client.add_cog(FailedChecks(client))
