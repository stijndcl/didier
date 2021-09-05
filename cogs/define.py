from data.embeds.urban_dictionary import Definition
from decorators import help
from discord.ext import commands
from enums.help_categories import Category
from functions import checks


class Define(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.command(name="Define", aliases=["UrbanDictionary", "Ud"], usage="[Woord]")
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Other)
    async def define(self, ctx, *, query):
        """
        Command that looks up the definition of a word in the Urban Dictionary.
        :param ctx: Discord Context
        :param query: Word(s) to look up
        """
        embed = Definition(query).to_embed()
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Define(client))
