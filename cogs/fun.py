from data.embeds.xkcd import XKCDEmbed
from data.menus import paginatedLeaderboard
from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import checks, stringFormatters
from functions.database import memes, trump, dadjoke
from functions.memes import generate
import json
import random
import requests


class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.utilsCog = self.client.get_cog("Utils")

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.command(name="Dadjoke", aliases=["Dj", "Dad"])
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Fun)
    async def dadjoke(self, ctx):
        """
        Command that sends a random dad joke.
        :param ctx: Discord Context
        """
        await ctx.send(dadjoke.getRandomJoke())

    @commands.command(name="Stalin", aliases=["Ss", "StalinMotivation", "Motivate"])
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Quotes)
    async def stalin(self, ctx):
        """
        Command that sends a random Stalin quote.
        :param ctx: Discord Context
        """
        with open("files/StalinMotivation.json", "r") as fp:
            file = json.load(fp)
            await ctx.send(file[random.randint(1, len(file))])

    @commands.command(name="Satan", aliases=["S8n", "SatanQuote"])
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Quotes)
    async def satan(self, ctx):
        """
        Command that sends a random Satan quote.
        :param ctx: Discord Context
        """
        with open("files/SatanQuotes.json", "r") as fp:
            file = json.load(fp)
            await ctx.send(file[random.randint(1, len(file))])

    @commands.command(name="Trump")
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Quotes)
    async def trump(self, ctx):
        """
        Command that sends a random Trump quote.
        :param ctx: Discord Context
        """
        quote = trump.getRandomQuote()
        await ctx.send("**\"{}**\"\n{} - {}".format(quote[1], quote[2], quote[3]))

    @commands.command(name="8-Ball", aliases=["8b", "8Ball"], ignore_extra=True)
    @help.Category(category=Category.Quotes)
    async def eightball(self, ctx):
        """
        Command that sends a random 8-ball response.
        :param ctx: Discord Context
        """
        with open("files/eightball.json", "r") as fp:
            file = json.load(fp)
            await ctx.send(file[random.randint(0, len(file) - 1)])

    @commands.command(name="Memegen", usage="[Meme] [Velden]")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @help.Category(category=Category.Fun)
    async def memegen(self, ctx, name="", *fields):
        """
        Command that generates memes.
        :param ctx: Discord Context
        :param name: the name of the meme
        :param fields: the fields to add to the meme
        """
        if len(fields) == 0:
            return await ctx.send("Controleer je argumenten.")

        # Get the meme info that corresponds to this name
        result: memes.Meme = memes.getMeme(name)

        # No meme found
        if result is None:
            return await ctx.send("Deze meme staat niet in de database.")

        # Convert to list to support item assignment
        fields = list(fields)

        generated = generate(result, fields)

        # If the request was successful, remove the message calling it
        if generated["success"]:
            await self.utilsCog.removeMessage(ctx.message)

        # Send the meme's url or the error message
        await ctx.send(generated["message"])

    @commands.command(name="Memes")
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Fun)
    async def memes(self, ctx):
        """
        Command that shows a list of memes in the database.
        :param ctx: Discord Context
        """
        memeList = memes.getAllMemes()

        # Turn the list into a list of [Name: fields]
        memeList = [": ".join([stringFormatters.title_case(meme[1]),
                               str(meme[2])]) for meme in sorted(memeList, key=lambda x: x[1])]

        pages = paginatedLeaderboard.Pages(source=paginatedLeaderboard.Source(memeList, "Memes", discord.Colour.blue()),
                                           clear_reactions_after=True)
        await pages.start(ctx)

    @commands.command(name="Pjoke")
    @help.Category(category=Category.Fun)
    async def pjoke(self, ctx):
        """
        Command that sends a random programming joke.
        :param ctx: Discord Context
        """
        r = requests.get("https://official-joke-api.appspot.com/jokes/programming/random").json()
        await ctx.send(r[0]["setup"] + "\n" + r[0]["punchline"])

    @commands.command(name="xkcd")
    @help.Category(category=Category.Fun)
    async def xkcd(self, ctx, n: int = None):
        """
        Send an xkcd comic
        """
        return await ctx.reply(embed=XKCDEmbed(n).create())


def setup(client):
    client.add_cog(Fun(client))
