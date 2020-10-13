from data import paginatedLeaderboard
import datetime
from decorators import help
import discord
from discord.ext import commands, menus
from enums.help_categories import Category
from functions import checks
import requests


class Train(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.command(name="Train", aliases=["Trein"], usage="[Vertrek]* [Bestemming]")
    @help.Category(category=Category.School)
    async def train(self, ctx, *args):
        if not args or len(args) > 2:
            await ctx.send("Controleer je argumenten.")
            return
        destination = args[-1]
        departure = args[0] if len(args) > 1 else "Gent Sint-Pieters"

        req = requests.get(
            "http://api.irail.be/connections/?from={}&to={}&alerts=true&lang=nl&format=json".format(departure,
                                                                                                    destination)).json()
        if "error" in req:
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(name="Treinen van {} naar {}".format(
                self.formatCity(departure), self.formatCity(destination)))
            embed.add_field(name="Error", value="Er ging iets fout, probeer het later opnieuw.", inline=False)
            await self.sendEmbed(ctx, embed)
            return

        pages = paginatedLeaderboard.Pages(source=TrainPagination(self.formatConnections(req["connection"]),
                                                                  self.formatCity(departure),
                                                                  self.formatCity(destination)),
                                           clear_reactions_after=True)
        await pages.start(ctx)

    def formatConnections(self, connections):
        response = []
        for connection in sorted(connections, key=lambda con: con["departure"]["time"]):
            conn = {}
            if connection["departure"]["canceled"] != "0" or connection["arrival"]["canceled"] != "0":
                conn = {"Canceled": "Afgeschaft"}
            dep = connection["departure"]
            arr = connection["arrival"]
            conn["depStation"] = self.formatCity(dep["station"])
            conn["depTime"] = self.formatTime(dep["time"])
            conn["delay"] = self.formatDelay(dep["delay"])
            conn["track"] = dep["platform"]
            conn["arrStation"] = self.formatCity(arr["station"])
            conn["direction"] = self.formatCity(dep["direction"]["name"])
            conn["arrTime"] = self.formatTime(arr["time"])
            conn["duration"] = self.formatTime(connection["duration"])
            response.append(conn)
        return response

    def formatTime(self, timestamp):
        if int(timestamp) <= 86400:
            minutes = int(timestamp) // 60
            if minutes < 60:
                return str(minutes) + "m"
            return "{}h{:02}m".format(minutes // 60, minutes % 60)
        else:
            return datetime.datetime.fromtimestamp(int(timestamp)).strftime("%H:%M")

    def formatDelay(self, seconds):
        seconds = int(seconds)
        return self.sign(seconds) + self.formatTime(abs(seconds)) if seconds != 0 else ""

    def sign(self, number):
        return "-" if int(number) < 0 else "+"

    def formatCity(self, city):
        city = city[0].upper() + city[1:]
        arr = []
        for i, letter in enumerate(city):
            if (i > 0 and (city[i - 1] == " " or city[i - 1] == "-")) or i == 0:
                arr.append(letter.upper())
            else:
                arr.append(letter.lower())
        return "".join(arr)

    async def sendEmbed(self, ctx, embed):
        if checks.allowedChannels(ctx):
            await ctx.send(embed=embed)
        else:
            await ctx.author.send(embed=embed)


class TrainPagination(menus.ListPageSource):
    def __init__(self, data, departure, destination):
        super().__init__(data, per_page=3)
        self.departure = departure
        self.destination = destination

    async def format_page(self, menu: menus.MenuPages, entries):
        offset = menu.current_page * self.per_page
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="Treinen van {} naar {}".format(self.departure, self.destination))
        embed.set_footer(text="{}/{}".format(menu.current_page + 1, self.get_max_pages()))

        for i, connection in enumerate(entries, start=offset):
            afgeschaft = "Canceled" in connection
            embed.add_field(name="Van", value=str(connection["depStation"]), inline=True)
            embed.add_field(name="Om", value=str(connection["depTime"]), inline=True)
            embed.add_field(name="Spoor", value=str(connection["track"]), inline=True)
            embed.add_field(name="Richting", value=str(connection["direction"]), inline=True)
            embed.add_field(name="Aankomst", value=(str(connection["arrTime"])
                                                    if not afgeschaft else "**AFGESCHAFT**"), inline=True)
            embed.add_field(name="Vertraging", value=str(connection["delay"]) if connection["delay"] != "" else "0",
                            inline=True)

            # White space
            if i - offset < 2:
                embed.add_field(name="\u200b", value="\u200b", inline=False)
        return embed


def setup(client):
    client.add_cog(Train(client))
