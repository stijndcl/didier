from data import constants
import datetime
from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import checks, clap, mock, sunrise, timeFormatters
import pytz
import time
import urllib.parse


# Random things that are usually oneliners & don't belong in any other categories
class Oneliners(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.utilsCog = self.client.get_cog('Utils')

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.command(name="Age", usage="[Formaat]*")
    @help.Category(category=Category.Didier)
    async def age(self, ctx, specification=None):
        allowedSpecifications = ["d", "days", "m", "months", "w", "weeks", "y", "years"]

        if specification is not None and specification.lower() not in allowedSpecifications:
            await ctx.send("**{}** is geen geldig formaat.".format(specification))
            return

        if specification is None:
            timeString = timeFormatters.diffYearBasisString(constants.creationDate)
        else:
            ageSeconds = round(time.time()) - constants.creationDate
            timeFormat = timeFormatters.getFormat(specification)
            timeString = str(timeFormatters.timeIn(ageSeconds, timeFormat)[0])
            timeString += " " + timeFormatters.getPlural(int(timeString), timeFormat)
        await ctx.send("Didier is **{}** oud.".format(timeString))

    @commands.command(name="Clap", usage="[Tekst]")
    @help.Category(category=Category.Other)
    async def clap(self, ctx, *args):
        await ctx.send(clap.clap("".join(args)))
        await self.utilsCog.removeMessage(ctx.message)

    @commands.command(name="Reverse", aliases=["Rev"], usage="[Tekst]")
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Other)
    async def reverse(self, ctx, *args):
        await ctx.send(" ".join(args)[::-1])

    @commands.command(name="Government", aliases=["Gov", "Regering"])
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Other)
    async def government(self, ctx):
        now = timeFormatters.dateTimeNow()
        newGov = datetime.datetime.fromtimestamp(1601539200, tz=pytz.timezone("Europe/Brussels"))
        delta = now - newGov
        zin = "Na **494** dagen is er weer een regering, **47** dagen te vroeg om het record te breken. Very sad times.\nMAAR hoelang denk je dat de nieuwe regering het gaat volhouden? Place your bets! Momenteel zitten we aan **{}** dag{}.".format(
            delta.days, "en" if delta.days != 1 else ""
        )
        # now = int(time.time())
        # valVorige = 1545350400
        # verkiezingen = 1558828800
        # valDiff = now - valVorige
        # verkiezingenDiff = now - verkiezingen
        # zin = (
        #         "We zitten al **%d** dagen zonder regering, en proberen al **%d** dagen een nieuwe te vormen.\nHet "
        #         "huidige wereldrecord is "
        #         "**541** dagen, dus nog **%d** dagen tot we het gebroken hebben." %
        #         (valDiff // 86400, verkiezingenDiff // 86400, 541 - int(verkiezingenDiff // 86400)))
        await ctx.send(zin)

    @commands.command()
    async def inject(self, ctx):
        await ctx.send("**{}** heeft wat code geïnjecteerd.".format(ctx.author.display_name))

    @commands.command(name="Mock", usage="[Tekst]")
    @help.Category(category=Category.Other)
    async def mock(self, ctx, *text):
        await ctx.channel.send("{} - **{}**".format(mock.mock(" ".join(text)), ctx.author.display_name))
        await self.utilsCog.removeMessage(ctx.message)

    @commands.command(name="Molest", usage="[@Persoon]")
    async def molest(self, ctx):
        if constants.didierId in ctx.message.content:
            await ctx.send("Nee.")
        elif str(ctx.author.id) in ctx.message.content or ctx.message.content == "molest me":
            await ctx.send("I didn't know you swing that way, " + ctx.author.display_name)
        elif "171671190631481345" in ctx.message.content:
            await ctx.send("Nee")
        else:
            await ctx.send("https://imgur.com/a/bwA6Exn")

    @commands.command(name="Changelog", aliases=["Cl", "Change", "Changes"])
    @help.Category(category=Category.Didier)
    async def changelog(self, ctx, *args):
        await ctx.send("V2.0: <https://docs.google.com/document/d/1oa-9oc9yFnZ0X5sLJTWfdahtaL0vF8acLl-xMXA3a40/edit#>\n"
                       "V2.1: https://docs.google.com/document/d/1ezdJBTnKWoog4q9yJrgwfF4iGOn-PZMoBZgSNVYPtqg/edit#")

    @commands.command(name="Todo", aliases=["List", "Td"])
    @help.Category(category=Category.Didier)
    async def todo(self, ctx, *args):
        await ctx.send("https://trello.com/b/PdtsAJea/didier-to-do-list")

    @commands.command(name="LMGTFY", aliases=["Dsfr", "Gtfm", "Google"], usage="[Query]")
    @help.Category(category=Category.Other)
    async def lmgtfy(self, ctx, *, query=None):
        if query:
            await ctx.send("https://lmgtfy.com/?q={}&iie=1".format(urllib.parse.quote(query)))

    @commands.command(name="Neck", aliases=["Necc"], usage="[Lengte]*")
    @help.Category(category=Category.Fun)
    async def neck(self, ctx, size=None):
        if not size:
            size = 1
        try:
            size = int(size)
            if not 0 < size < 16:
                raise ValueError
        except ValueError:
            return await ctx.send("Geef een geldig getal op.")

        await ctx.send("<:WhatDidYou:744476950654877756>" + ("<:DoTo:744476965951504414>" * size) + "<:MyDrink:744476979939508275>")

    @commands.command()
    async def open(self, ctx):
        # await ctx.send(file=discord.File("files/images/open_source_bad.jpg"))
        await ctx.send("Shut, it already is.")

    @commands.command()
    async def sc(self, ctx, *args):
        await ctx.send("http://take-a-screenshot.org/")

    @commands.command(aliases=["src", "os", "sauce"])
    async def source(self, ctx):
        # await ctx.send("<https://bit.ly/31z3BuH>")
        await ctx.send("https://github.com/stijndcl/didier")

    @commands.command(aliases=["sunrise", "sunshine"])
    async def sun(self, ctx):
        s = sunrise.Sun()
        await ctx.send(":sunny:: **{}**\n:crescent_moon:: **{}**".format(s.sunrise(), s.sunset()))

    @commands.command(name="Tias", aliases=["TryIt"])
    async def tias(self, ctx, *args):
        await ctx.send("***Try it and see***")


def setup(client):
    client.add_cog(Oneliners(client))
