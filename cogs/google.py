import discord
from discord.ext import commands
from decorators import help
from enums.help_categories import Category
from functions.scraping import google_search


class Google(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.command(name="Google", aliases=["Gtfm", "Search"])
    @help.Category(Category.Other)
    async def google(self, ctx, *query):
        results, status = google_search(" ".join(query))

        if results is None:
            return await ctx.send("Er ging iets fout (Response {})".format(status))


def setup(client):
    client.add_cog(Google(client))
