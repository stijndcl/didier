from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import colours
import random
import requests
import json


class Random(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    # Creates an alias
    @commands.command(name="Choice", aliases=["Choose"], usage="[Argumenten]")
    async def choose(self, ctx, *options):
        await self.choice(ctx, *options)

    @commands.command(name="Shuffle", usage="[Argumenten]")
    async def _shuffle(self, ctx, *options):
        await self.shuffle(ctx, *options)

    @commands.group(name="Random", aliases=["R", "Rand", "RNG"], case_insensitive=True, invoke_without_command=True)
    @help.Category(category=Category.Random, unpack=True)
    async def random(self, ctx):
        pass

    @random.command(name="Choice", usage="[Argumenten]")
    async def choice(self, ctx, *options):
        if not options or not options[0]:
            return await ctx.send("Geef een geldige reeks op.")

        await ctx.send(random.choice(options))

    @random.command(name="Number", aliases=["Int"], usage="[Van]* [Tot]*")
    async def number(self, ctx, to=100, start=1):
        # This allows number(to) to work, as well as number(start, to)
        if start > to:
            start, to = to, start

        await ctx.send(random.randint(start, to))

    @number.error
    async def on_number_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.BadArgument):
            await ctx.send("Dit is geen geldig getal.")
        else:
            raise error

    @random.command(name="Name")
    async def name(self, ctx):
        try:
            name = requests.get("https://randomuser.me/api/").json()
        except json.decoder.JSONDecodeError:
            await ctx.send("Er ging iets mis. Probeer het opnieuw.")
            return

        name = name["results"][0]["name"]
        await ctx.send("{} {} {}".format(name["title"], name["first"], name["last"]))

    @random.command(name="Identity", aliases=["Id"])
    async def identity(self, ctx):
        try:
            identity = requests.get("https://randomuser.me/api/").json()
        except json.decoder.JSONDecodeError:
            return await ctx.send("Er ging iets mis. Probeer het opnieuw.")

        identity = identity["results"][0]
        name = identity["name"]
        name = "{} {} {}".format(name["title"], name["first"], name["last"])

        gender = identity["gender"]
        street = "{} {}".format(identity["location"]["street"]["number"], identity["location"]["street"]["name"])
        location = "{}, {}, {}, {}".format(street, identity["location"]["city"],
                                           identity["location"]["state"], identity["location"]["country"])
        age = identity["dob"]["age"]

        await ctx.send("{}\n{}, {}\n{}".format(name, age, gender, location))

    @random.command(name="Shuffle", aliases=["Order"], usage="[Argumenten]")
    async def shuffle(self, ctx, *args):
        if not args:
            return await ctx.send("Geef een geldige reeks op.")

        args = list(args)

        random.shuffle(args)

        await ctx.send(" - ".join(args))

    @random.command(name="Colour", aliases=["Color"])
    async def colour(self, ctx):
        r, g, b = colours.randomRGB()

        embed = discord.Embed(colour=discord.Colour.from_rgb(r, g, b))
        embed.set_author(name="Random Colour")
        embed.add_field(name="RGB", value="{}, {}, {}".format(r, g, b), inline=False)
        embed.add_field(name="HEX", value=colours.RGBToHEX(r, g, b), inline=False)
        embed.add_field(name="HSL", value="{}°, {}%, {}%".format(*colours.RGBToHSL(r, g, b)), inline=False)
        embed.add_field(name="HSV", value="{}°, {}%, {}%".format(*colours.RGBToHSV(r, g, b)), inline=False)
        await ctx.send(embed=embed)

    @random.command(name="Timestamp", aliases=["Time", "Ts"])
    async def timestamp(self, ctx):
        hour = str(random.randint(0, 23))
        hour = ("0" if len(hour) == 1 else "") + hour
        minutes = str(random.randint(0, 23))
        minutes = ("0" if len(minutes) == 1 else "") + minutes
        await ctx.send("{}:{}".format(hour, minutes))

    @random.command(name="Fact", aliases=["Knowledge"])
    async def fact(self, ctx):
        randomFact = requests.get("https://uselessfacts.jsph.pl/random.json?language=en").json()
        await ctx.send(randomFact["text"])

    @commands.command(name="Yes/No", aliases=["Yn"])
    @help.Category(Category.Random)
    async def yesno(self, ctx):
        await ctx.send(random.choice(["Ja.", "Nee."]))


def setup(client):
    client.add_cog(Random(client))
