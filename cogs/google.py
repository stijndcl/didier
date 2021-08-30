import discord
from discord.ext import commands
from dislash import slash_command, SlashInteraction, Option, OptionType
from decorators import help
from enums.help_categories import Category
from functions.scrapers.google import google_search, SearchResult


def _create_google_embed(result: SearchResult) -> discord.Embed:
    embed = discord.Embed(colour=discord.Colour.blue())
    embed.set_author(name="Google Search")

    # Empty list of results
    if len(result.results) == 0:
        embed.colour = discord.Colour.red()
        embed.description = "Geen resultaten gevonden."
        return embed

    # Add results into a field
    links = []

    for index, link in enumerate(result.results):
        links.append(f"{index + 1}: {link}")

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
        result = google_search(query)

        if not result.results:
            return await interaction.reply("Er ging iets fout (Response {})".format(result.status_code))

        embed = _create_google_embed(result)
        await interaction.reply(embed=embed)

    @commands.command(name="Google", aliases=["Gtfm", "Search"], usage="[Query]", case_insensitive=True)
    @help.Category(Category.Other)
    async def google(self, ctx, *query):
        if not query:
            return await ctx.reply("Je hebt geen query opgegeven.", mention_author=True)

        result = google_search(" ".join(query))

        if not result.results:
            return await ctx.send("Er ging iets fout (Response {})".format(result.status_code))

        embed = _create_google_embed(result)
        await ctx.reply(embed=embed, mention_author=False)


def setup(client):
    client.add_cog(Google(client))
