from discord.ext import commands
from decorators import help
from enums.help_categories import Category
from functions.scrapers.google import google_search, create_google_embed


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

        result = google_search(" ".join(query))

        if not result.results:
            return await ctx.send("Er ging iets fout (Response {})".format(result.status_code))

        embed = create_google_embed(result)
        await ctx.reply(embed=embed, mention_author=False)


def setup(client):
    client.add_cog(Google(client))
