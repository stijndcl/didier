from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import checks, mock, stringFormatters
from functions.database import memes, trump, dadjoke
import json
import os
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
        result = memes.getMeme(name)

        # No meme found
        if not result[0]:
            return await ctx.send(result[1])

        # Convert to list to support item assignment
        fields = list(fields)

        # If there's only one field, the user isn't required to use quotes
        if result[1][2] == 1:
            fields = [" ".join(fields)]

        # Apply mock to mocking spongebob memes
        if result[1][1] == "mocking spongebob":
            fields = list(map(mock.mock, fields))

        # X, X everywhere only takes X as an argument
        if result[1][1] == "x, x everywhere":
            fields[0] = " ".join(fields)
            fields.append(fields[0] + " everywhere")

        # List of fields to send to the API
        boxes = [{"text": ""}, {"text": ""}, {"text": ""}, {"text": ""}]

        # Add all fields required & ignore the excess ones
        for i in range(len(fields)):
            if i > 3:
                break
            boxes[i]["text"] = fields[i]

        # Check server status
        req = requests.get('https://api.imgflip.com/get_memes').json()

        if req["success"]:
            caption = {
                "template_id": result[1][0],
                "username": os.getenv("IMGFLIPNAME"),
                "password": os.getenv("IMGFLIPPASSWORD"),
                "boxes[0][text]": boxes[0]["text"],
                "boxes[1][text]": boxes[1]["text"],
                "boxes[2][text]": boxes[2]["text"],
                "boxes[3][text]": boxes[3]["text"]
            }

            # Send the POST to the API
            memeReply = requests.post('https://api.imgflip.com/caption_image', caption).json()

            if memeReply['success']:
                await ctx.send(str(memeReply['data']['url']))
                await self.utilsCog.removeMessage(ctx.message)
            else:
                await ctx.send(
                    "Error! Controleer of je de juiste syntax hebt gebruikt. Gebruik het commando "
                    "\"memes\" voor een lijst aan geaccepteerde meme-namen.")
        else:
            await ctx.send("Er is een fout opgetreden.")

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
        memeList = [": ".join([stringFormatters.titleCase(meme[1]),
                               str(meme[2])]) for meme in sorted(memeList, key=lambda x: x[1])]

        # Add the fields into the embed
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.add_field(name="Meme: aantal velden", value="\n".join(memeList), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="Pjoke")
    @help.Category(category=Category.Fun)
    async def pjoke(self, ctx):
        """
        Command that sends a random programming joke.
        :param ctx: Discord Context
        """
        r = requests.get("https://official-joke-api.appspot.com/jokes/programming/random").json()
        await ctx.send(r[0]["setup"] + "\n" + r[0]["punchline"])


def setup(client):
    client.add_cog(Fun(client))
