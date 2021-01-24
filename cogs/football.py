from bs4 import BeautifulSoup
from decorators import help
from discord.ext import commands
from enums.help_categories import Category
from functions import checks, config
from functions.football import getMatches
import requests
import tabulate


class Football(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return checks.isMe(ctx) and not self.client.locked

    @commands.group(name="Jpl", case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(Category.Sports)
    async def jpl(self, ctx, *args):
        pass

    @jpl.command(name="Matches", aliases=["M"], usage="[Week]*")
    async def matches(self, ctx, *args):
        args = list(args)

        # Default is current day
        if not args:
            args = [str(config.get("jpl_day"))]

        if all(letter.isdigit() for letter in args[0]):
            await ctx.send(getMatches(int(args[0])))
        else:
            return await ctx.send("Dit is geen geldige speeldag.")

    # TODO check back when there's active games & add the timestamp instead of EINDE
    def format_match(self, match):
        return [match["day"], match["date"], match["home"], match["score"], match["away"], "Einde"]

    def get_weekday(self, day: int):
        days = ["Ma", "Di", "Wo", "Do", "Vr", "Za", "Zo"]
        return days[day]

    @jpl.command(name="Table", aliases=["Ranking", "Rankings", "Ranks", "T"])
    async def table(self, ctx, *args):
        page_html = requests.get("https://sporza.be/nl/categorie/voetbal/jupiler-pro-league/").text
        bs_parsed = BeautifulSoup(page_html, "html.parser")
        rows = bs_parsed.find(summary="algemeen klassement").find_all("tr")[1:]
        rowsFormatted = []
        for row in rows:
            rowsFormatted.append(self.createRowList(row))
        await ctx.send("```Jupiler Pro League Klassement\n\n{}```".format(tabulate.tabulate(rowsFormatted, headers=["#", "Ploeg", "Punten", "M", "M+", "M-", "M="])))

    # Formats the row into an list that can be passed to Tabulate
    def createRowList(self, row):
        scoresArray = list([td.renderContents().decode("utf-8") for td in row.find_all("td")])[:6]
        # Insert the team name into the list
        scoresArray.insert(1, row.find_all("a")[0].renderContents().decode("utf-8").split("<!--")[0])
        return scoresArray


def setup(client):
    client.add_cog(Football(client))
