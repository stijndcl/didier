from datetime import datetime
from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import checks
import pytz
import requests


# Temporarily disabled because of API (setup @ bottom)
class Launch(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.command(name="Launch", aliases=["SpaceX"])
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Other)
    async def launch(self, ctx, *args):
        resp = self.getNextLaunch()
        resp: dict = resp[list(resp.keys())[0]]
        embed = discord.Embed(
            colour=discord.Colour.blue()
        )
        embed.set_author(name="🚀 Volgende SpaceX lancering 🚀")
        embed.add_field(name="Naam:", value=resp["name"], inline=False)
        embed.add_field(name="Tijdstip:", value=resp["time"])
        await ctx.send(embed=embed)

    def getNextLaunch(self):
        resp = requests.get("https://launchlibrary.net/1.3/launch?next=1&name=falcon").json()
        if "status" in resp and (resp["status"] == "fail" or resp["status"] == "error"):
            return {"error": "fail" if resp["status"].lower() == "fail" else "none found"}
        resp = resp["launches"]
        ret = {}
        for launch in resp:
            ret[launch["id"]] = {
                "name": launch["name"],
                "time": self.parseDate(launch["net"][:-4]) if launch["tbdtime"] == 0 else "TBA",
                "TBA": launch["tbdtime"] == "0"
            }
        return ret

    def parseDate(self, timestr):
        d = datetime.strptime(timestr, "%B %d, %Y %H:%M:%S").timestamp()
        return str(
            datetime.fromtimestamp(int(d) + 7200, pytz.timezone("Europe/Brussels")).strftime('%B %d %Y om %H:%M:%S'))


# def setup(client):
#     client.add_cog(Launch(client))
