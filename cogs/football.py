from bs4 import BeautifulSoup
import datetime
from decorators import help
from discord.ext import commands
from enums.help_categories import Category
from functions import checks, config
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
        if not args:
            args = [str(config.get("jpl_day"))]
        if all(letter.isdigit() for letter in args[0]):
            current_day = requests.get("https://api.sporza.be/web/soccer/matchdays/161733/{}".format(args[0])).json()
            current_day = current_day["groupedMatches"][0]["matches"]

            # Create dictionaries for every match
            matches_formatted = {}
            for i, match in enumerate(current_day):
                matchDic = {"home": match["homeTeam"]["name"], "away": match["awayTeam"]["name"]}

                # Add date
                matchDate = datetime.datetime.strptime(match["startDateTime"].split("+")[0], "%Y-%m-%dT%H:%M:%S.%f")
                matchDic["date"] = matchDate.strftime("%d/%m")
                matchDic["day"] = self.get_weekday(matchDate.weekday())

                # TODO check back when there's active games (to find the key in the dict) & add the current time if not over
                # Add scores
                if match["status"] == "END":  # Status != [not_yet_started] whatever it is
                    matchDic["score"] = "{} - {}".format(match["homeScore"], match["awayScore"])
                else:
                    # If there's no score, show when the match starts
                    matchDic["score"] = "{}:{}".format(
                        ("" if len(str(matchDate.hour)) == 2 else "0") + str(matchDate.hour),  # Leading Zero
                        ("" if len(str(matchDate.minute)) == 2 else "0") + str(matchDate.minute))  # Leading Zero

                matches_formatted[i] = matchDic

            # Put every formatted version of the matches in a list
            matchList = list([self.format_match(matches_formatted[match]) for match in matches_formatted])
            await ctx.send("```Jupiler Pro League - Speeldag {}\n\n{}```".format(args[0], tabulate.tabulate(matchList, headers=["Dag", "Datum", "Thuis", "Stand", "Uit", "Tijd"])))
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
