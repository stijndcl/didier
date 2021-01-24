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

    @commands.command(name="Google", aliases=["Gtfm", "Search"], usage="[Query]", case_insensitive=True)
    @help.Category(Category.Other)
    async def google(self, ctx, *query):
        if not query:
            return await ctx.reply("Je hebt geen query opgegeven.", mention_author=True)

        results, status = google_search(" ".join(query))

        if results is None:
            return await ctx.send("Er ging iets fout (Response {})".format(status))

        elements = list(filter(lambda x: x is not None, results))

        if len(elements) > 10:
            elements = elements[:10]

        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="Google Search")

        # Empty list of results
        if len(elements) == 0:
            embed.description = "Geen resultaten gevonden."
            return await ctx.reply(embed=embed, mention_author=False)

        links = []

        for index, (link, title) in enumerate(elements):
            links.append("{}: [{}]({})".format(index + 1, title, link))

        embed.description = "\n".join(links)

        await ctx.reply(embed=embed, mention_author=False)


def setup(client):
    client.add_cog(Google(client))
