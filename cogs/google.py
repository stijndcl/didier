import discord
from discord.ext import commands
from dislash import slash_command, SlashInteraction, Option, OptionType
from decorators import help
from enums.help_categories import Category
from functions.scrapers.google import google_search


def _create_google_embed(results) -> discord.Embed:
    # Filter out all Nones
    elements = list(filter(lambda x: x is not None, results))

    embed = discord.Embed(colour=discord.Colour.blue())
    embed.set_author(name="Google Search")

    # Empty list of results
    if len(elements) == 0:
        embed.description = "Geen resultaten gevonden."
        return embed

    # Cut excess results out
    if len(elements) > 10:
        elements = elements[:10]

    links = []

    for index, (link, title) in enumerate(elements):
        links.append("{}: [{}]({})".format(index + 1, title, link))

    embed.description = "\n".join(links)

    return embed


class Google(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @slash_command(name="google",
                   description="Google search",
                   options=[
                     Option("query", "Search query", OptionType.STRING, required=True)
                   ],
                   guild_ids=[880175869841277008]
                   )
    async def _google_slash(self, interaction: SlashInteraction, query: str):
        results, status = google_search(query)

        if results is None:
            return await interaction.reply("Er ging iets fout (Response {})".format(status))

        embed = _create_google_embed(results)
        await interaction.reply(embed=embed)

    @slash_command(name="test", description="Test")
    async def test(self, interaction):
        await interaction.reply(":eyes:")

    @commands.command(name="Google", aliases=["Gtfm", "Search"], usage="[Query]", case_insensitive=True)
    @help.Category(Category.Other)
    async def google(self, ctx, *query):
        if not query:
            return await ctx.reply("Je hebt geen query opgegeven.", mention_author=True)

        results, status = google_search(" ".join(query))

        if results is None:
            return await ctx.send("Er ging iets fout (Response {})".format(status))

        embed = _create_google_embed(results)
        await ctx.reply(embed=embed, mention_author=False)


def setup(client):
    client.add_cog(Google(client))
