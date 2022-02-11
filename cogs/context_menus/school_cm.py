import discord
from discord import ApplicationContext
from discord.ext import commands
from discord.commands import message_command

from startup.didier import Didier


class SchoolCM(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    @message_command(name="Pin")
    async def _pin_cm(self, ctx: ApplicationContext, message: discord.Message):
        # In case people abuse, check if they're blacklisted
        blacklist = []

        if ctx.user.id in blacklist:
            return await ctx.respond(":angry:", ephemeral=True)

        if message.is_system():
            return await ctx.respond("Dus jij wil system messages pinnen?\nMag niet.", ephemeral=True)

        await message.pin(reason=f"Didier Pin door {ctx.user.display_name}")
        await ctx.respond("📌", ephemeral=True)


def setup(client: Didier):
    # client.add_cog(SchoolCM(client))
    # TODO wait for bug to be fixed in lib then uncomment this
    #   when used in dm, tries to create a DM with the bot?
    pass
