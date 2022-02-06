from discord.ext import commands

from data.embeds.snipe import EditSnipe, DeleteSnipe
from data.menus import custom_commands
from data.snipe import Action, Snipe
from decorators import help
from enums.help_categories import Category
from startup.didier import Didier


class Other(commands.Cog):
    def __init__(self, client: Didier):
        self.client: Didier = client

    # Don't allow any commands to work when locked
    def cog_check(self, _):
        return not self.client.locked

    @commands.command(name="Custom")
    @help.Category(category=Category.Didier)
    async def list_custom(self, ctx):
        """
        Get a list of all custom commands
        """
        await custom_commands.CommandsList(ctx).send()

    @commands.command(name="Snipe")
    @help.Category(category=Category.Other)
    async def snipe(self, ctx):
        """
        Shame people for editing & removing messages.
        The dict is stored in memory so it will be cleared whenever the bot restarts.
        """
        if ctx.guild is None:
            return

        if ctx.channel.id not in self.client.snipe:
            return await ctx.send("Er is hier niemand om uit te lachen.")

        s: Snipe = self.client.snipe[ctx.channel.id]

        embed_class = (EditSnipe(s) if s.action == Action.Edit else DeleteSnipe(s))

        return await ctx.send(embed=embed_class.to_embed(self.client))


def setup(client):
    client.add_cog(Other(client))
