import datetime
from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import checks
import requests
import time


class Release(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    # Gets upcoming game releases
    @commands.group(name="Releases", usage="[Pagina]*", case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Games)
    async def releases(self, ctx, page="1"):
        for char in page:
            if not char.isdigit():
                await ctx.send("Geef een geldige pagina op.")
                return

        dates = self.getDates()
        resp = requests.get("https://api.rawg.io/api/games?dates={},{}&page_size=25&page={}&ordering=released".format(
            dates[0], dates[1], page
        )).json()

        try:
            embed = discord.Embed(colour=discord.Colour.blue())
            embed.set_author(name="Volgende Game Releases | Pagina {}".format(page))

            embed.description = "\n".join(
                ["{} (#{}): {}".format(result["name"], result["id"], self.rewriteDate(result["released"]))
                 for result in resp["results"]])
            embed.set_footer(text="Voor gedetailleerde info: Didier Game Info [id]")
        except KeyError:
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(name="Game Releases")
            embed.add_field(name="Error", value="Er ging iets fout.")

        await ctx.send(embed=embed)

    def getDates(self):
        today = datetime.datetime.fromtimestamp(time.time())
        nextMonth = datetime.datetime.fromtimestamp(time.time() + 2629743)
        return ["-".join([str(today.year), self.leadingZero(str(today.month)), self.leadingZero(str(today.day))]),
                "-".join([str(nextMonth.year),
                          self.leadingZero(str(nextMonth.month)), self.leadingZero(str(nextMonth.day))])]

    def leadingZero(self, num):
        return num if len(num) == 2 else "0" + num

    # Shows more detailed information for a game
    @releases.command(name="Info", aliases=["Details"], usage="[Game Id]")
    async def info(self, ctx, *, game_id):
        game_id = self.create_slug(game_id)
        resp = requests.get("https://api.rawg.io/api/games/{}".format(str(game_id))).json()
        if "redirect" in resp:
            resp = requests.get("https://api.rawg.io/api/games/{}".format(resp["slug"])).json()
        if "Not found." in resp.values():
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_author(name="Game Info")
            embed.description = "Er is geen game gevonden met deze id of naam."
        else:
            embed = discord.Embed(colour=discord.Colour.blue())
            embed.set_author(name="Game Info")
            embed.add_field(name="Naam", value=resp["name"])
            embed.add_field(name="Id", value=resp["id"])
            embed.add_field(name="Datum", value="TBA" if resp["tba"] else self.rewriteDate(resp["released"]))
            embed.add_field(name="Platforms", value=", ".join(self.getPlatforms(resp)))
            embed.add_field(name="Stores", value=", ".join(self.getStores(resp)))
            embed.add_field(name="Genres", value=", ".join(self.getGenres(resp)))
            embed.add_field(name="Tags", value=self.getTags(resp), inline=False)
            embed.add_field(name="Description", value=self.writeDescription(resp["description_raw"]), inline=False)
        await ctx.send(embed=embed)

    # Turns name into a slug
    def create_slug(self, game_id):
        try:
            # Check if it's a number
            game_id = int(game_id)
            return str(game_id)
        except ValueError:
            game_id = game_id.lower().replace(" ", "-").replace(":", "").replace("'", "")
            return game_id

    def rewriteDate(self, date):
        date = date.split("-")
        return "-".join(reversed(date))

    def getGenres(self, release):
        return sorted([genre["name"] for genre in release["genres"]])

    # Returns a list of all platforms this game is available on
    def getPlatforms(self, release):
        return sorted([platform["platform"]["name"] for platform in release["platforms"]])

    # Returns a list of all stores this game is available on
    def getStores(self, release):
        return sorted(store["store"]["name"] for store in release["stores"])

    # Returns a list of all tags associated with this game
    def getTags(self, release):
        if len(release["tags"]) == 0:
            return "N/A"
        li = sorted([tag["name"] for tag in release["tags"]])
        st = li[0]
        for tag in li[1:]:
            if len(st) + 2 + len(tag) > 1024:
                break
            st += ", " + tag
        return st if st else "N/A"

    # Truncates the description if necessary
    def writeDescription(self, description):
        if len(description) > 700:
            return description[:697] + "..."
        return description if description else "N/A"

    @info.error
    async def info_on_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Geef een geldig getal op.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Controleer je argumenten.")
        else:
            raise error


def setup(client):
    client.add_cog(Release(client))
