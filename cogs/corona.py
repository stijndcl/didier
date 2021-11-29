from decorators import help
import discord
from discord.ext import commands
from enums.help_categories import Category
from functions import checks, timeFormatters
import requests


class Corona(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    # Gets the information & calls other functions if necessary
    @commands.group(name="Corona", usage="[Land]*", case_insensitive=True, invoke_without_command=True)
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Other)
    async def corona(self, ctx, country: str = "Belgium"):
        """
        Command that shows the corona stats for a certain country.
        :param ctx: Discord Context
        :param country: the country to show the stats for
        """
        dic = await self.getCountryStats(country)
        if dic is None:
            # Country was not found
            await self.sendError(ctx)
            return

        # Vaccination stats
        try:
            vaccine = self.getVaccineData(country, dic["today"]["population"], dic["yesterday"]["population"])
        except KeyError:
            vaccine = None

        await self.sendEmbed(ctx, dic, vaccine)

    @corona.command(name="Vaccinations", aliases=["V", "Vacc", "Vax", "Vaxx"])
    async def vaccinations(self, ctx):
        population = 11632326

        res = requests.get("https://covid-vaccinatie.be/api/v1/administered.json")
        updated = requests.get("https://covid-vaccinatie.be/api/v1/last-updated.json")

        if res.status_code != 200:
            return

        res = res.json()
        administered = res["result"]["administered"]

        first_dose = 0
        second_dose = 0

        # Get dose counts
        for entry in administered:
            first_dose += entry["first_dose"]
            second_dose += entry["second_dose"]

        new_info = self.get_new_vaccinations(administered)

        # % of population that has received their vaccine
        first_dose_perc = round(first_dose * 100 / population, 2)
        second_dose_perc = round(second_dose * 100 / population, 2)

        # % of population that has received their vaccine TODAY
        first_today_perc = round(new_info["today"]["first_dose"] * 100 / population, 2)
        second_today_perc = round(new_info["today"]["second_dose"] * 100 / population, 2)

        # Difference compared to the day before
        first_trend = self.trend(new_info, "first_dose")
        second_trend = self.trend(new_info, "second_dose")

        embed = discord.Embed(colour=discord.Colour.red(), title="Vaccinatiecijfers")

        embed.add_field(name="Eerste Dosis", value="{:,} ({}%)".format(first_dose, first_dose_perc))
        embed.add_field(name="Eerste Dosis (Vandaag)",
                        value="{:,} ({}%)".format(new_info["today"]["first_dose"], first_today_perc))
        embed.add_field(name="Eerste Dosis (Verschil)", value=first_trend)
        embed.add_field(name="Tweede Dosis", value="{:,} ({}%)".format(second_dose, second_dose_perc))
        embed.add_field(name="Tweede Dosis (Vandaag)",
                        value="{:,} ({}%)".format(new_info["today"]["second_dose"], second_today_perc))
        embed.add_field(name="Tweede Dosis (Verschil)", value=second_trend)

        # Only add updated timestamp if the request succeeded
        # this isn't really a big deal so the command doesn't fail
        # if it didn't
        if updated.status_code == 200:
            embed.set_footer(text="Laatste update: {}".format(updated.json()["result"]["last_updated"]["updated"]))

        return await ctx.send(embed=embed)

    def get_new_vaccinations(self, data):
        """
        Finds the amount of new doses administered today & the day before
        """
        reversed_data = list(reversed(data))

        # Find the most recent date that was added
        # (not necessarily today)
        latest_date = reversed_data[0]["date"]
        date_before = ""

        info = {
            "today": {
                "first_dose": 0,
                "second_dose": 0
            },
            "yesterday": {
                "first_dose": 0,
                "second_dose": 0
            }
        }

        # Find first date doses
        for entry in reversed_data:
            if entry["date"] == latest_date:
                info["today"]["first_dose"] += entry["first_dose"]
                info["today"]["second_dose"] += entry["second_dose"]
            else:
                # Find the date before the most recent one
                # to calculate differences
                date_before = entry["date"]
                break

        # Find second date doses
        for entry in reversed_data:
            # Info on first date was added above
            if entry["date"] == latest_date:
                continue
            elif entry["date"] == date_before:
                info["yesterday"]["first_dose"] += entry["first_dose"]
                info["yesterday"]["second_dose"] += entry["second_dose"]
            else:
                break

        return info

    @corona.command(aliases=["lb", "leaderboards"], hidden=True)
    async def leaderboard(self, ctx):
        """
        Command that shows the Corona Leaderboard.
        Alias for Lb Corona.
        :param ctx: Discord Context
        :return: y
        """
        await self.client.get_cog("Leaderboards").callLeaderboard("corona", ctx)

    async def sendEmbed(self, ctx, dic, vaccines):
        """
        Function that sends a Corona embed from a dictionary.
        :param ctx: Discord Context
        :param dic: the dictionary corresponding to this country
        """
        embed = discord.Embed(colour=discord.Colour.red(), title="Coronatracker {}".format(dic["today"]["country"]))
        embed.set_thumbnail(url="https://i.imgur.com/aWnDuBt.png")

        # Total
        embed.add_field(name="Totale Gevallen (Vandaag):",
                        value=self.createEmbedString(
                            dic["today"]["cases"],
                            dic["today"]["todayCases"],
                            self.trendIndicator(dic, "todayCases")
                        ),
                        inline=False)

        # Active
        embed.add_field(name="Actieve Gevallen (Vandaag):",
                        value=self.createEmbedString(
                            dic["today"]["activeCases"],
                            dic["today"]["activeCases"] - dic["yesterday"]["activeCases"],
                            self.activeTrendIndicator(dic)
                        ),
                        inline=False)

        # Deaths
        embed.add_field(name="Sterfgevallen (Vandaag):",
                        value=self.createEmbedString(
                            dic["today"]["deaths"],
                            dic["today"]["todayDeaths"],
                            self.trendIndicator(dic, "todayDeaths")
                        ),
                        inline=False)

        # Recovered
        embed.add_field(name="Hersteld (Vandaag):",
                        value=self.createEmbedString(
                            dic["today"]["recovered"],
                            dic["today"]["todayRecovered"],
                            self.trendIndicator(dic, "todayRecovered")
                        ),
                        inline=False)

        # Test Cases
        embed.add_field(name="Aantal uitgevoerde tests:",
                        value=self.createEmbedString(
                            dic["today"]["tests"],
                            dic["today"]["todayTests"]
                        ),
                        inline=False)

        # Vaccines
        if vaccines is not None:
            # embed.add_field(name="Aantal toegediende vaccins:",
            #                 value=self.createEmbedString(
            #                     vaccines["today"]["vaccines"],
            #                     vaccines["today"]["todayVaccines"],
            #                     self.trendIndicator(vaccines, "todayVaccines")
            #                 ))
            embed.add_field(name="Aantal toegediende vaccins:",
                            value="{:,}".format(vaccines["today"]["vaccines"]),
                            inline=False)
        else:
            # Vaccine data is missing
            embed.add_field(name="Aantal toegediende vaccins:",
                            value="?",
                            inline=False)

        # Timestamp of last update
        timeFormatted = timeFormatters.epochToDate(int(dic["today"]["updated"]) / 1000)
        embed.set_footer(text="Laatst geüpdatet op {} ({} geleden)".format(
            timeFormatted["date"], timeFormatted["timeAgo"]))
        await ctx.send(embed=embed)

    def createEmbedString(self, total, today, indicator="", isPercentage=False):
        """
        Function that formats a string to add covid data into the embed,
        separate function to make code more readable
        """
        # + or - symbol | minus is included in the number so no need
        symbol = "+" if today >= 0 else ""
        perc = "%" if isPercentage else ""

        return "{:,}{} **({}{:,}{})** {}".format(
            total, perc, symbol, today, perc, indicator
        )

    @commands.command(name="Trends", aliases=["Ct"], usage="[Land]*")
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.Other)
    async def trends(self, ctx, country: str = "Belgium"):
        """
        Command that gives more precise stats & changes.
        :param ctx: Discord Context
        :param country: the country to get the stats for
        """
        dic = await self.getCountryStats(country)
        if dic is None:
            await self.sendError(ctx)
            return

        # Get the distribution for this country
        distribution = self.distribution(dic)

        embed = discord.Embed(colour=discord.Colour.red(), title="Coronatrends {}".format(dic["today"]["country"]))
        embed.set_thumbnail(url="https://i.imgur.com/aWnDuBt.png")

        # Calculate the trends & add them into the fields
        embed.add_field(name="Totale Gevallen\n({:,})".format(dic["today"]["cases"]),
                        value=self.trend(dic, "cases"),
                        inline=True)

        embed.add_field(name="Sterfgevallen\n({:,})".format(dic["today"]["deaths"]),
                        value=self.trend(dic, "deaths"),
                        inline=True)

        embed.add_field(name="Hersteld\n({:,})".format(dic["today"]["recovered"]),
                        value=self.trend(dic, "recovered"))

        embed.add_field(name="Totale Gevallen\nVandaag ({:,})".format(dic["today"]["todayCases"]),
                        value=self.trend(dic, "todayCases"),
                        inline=True)

        embed.add_field(name="Sterfgevallen\nVandaag ({:,})".format(dic["today"]["todayDeaths"]),
                        value=self.trend(dic, "todayDeaths"),
                        inline=True)

        embed.add_field(name="Hersteld\nVandaag ({:,})".format(dic["today"]["todayRecovered"]),
                        value=self.trend(dic, "todayRecovered"))

        embed.add_field(name="Verdeling", value="Actief: {} | Overleden: {} | Hersteld: {}".format(
            distribution[0], distribution[1], distribution[2]), inline=False)

        # Timestamp of last update
        timeFormatted = timeFormatters.epochToDate(int(dic["today"]["updated"]) / 1000)
        embed.set_footer(text="Laatst geüpdatet op {} ({} geleden)".format(
            timeFormatted["date"], timeFormatted["timeAgo"]))
        await ctx.send(embed=embed)

    async def getCountryStats(self, country):
        """
        Function that gets the stats for a specific country.
        :param country: the country to get the stats for
        :return: a dictionary containing the info for today & yesterday
        """
        # Check if Global or a country was passed
        if country.lower() == "global":
            country = "all?"
        else:
            country = "countries/{}?strict=false&".format(country)

        today = requests.get("https://disease.sh/v3/covid-19/{}yesterday=false&allowNull=false".format(country)).json()

        # Send error message
        if "message" in today:
            return None

        yesterday = requests.get("https://disease.sh/v3/covid-19/{}yesterday=true&allowNull=false".format(country)) \
            .json()

        # Divide into today & yesterday to be able to calculate the changes
        dic = {
            "today": {
                "country": today["country"] if country != "all?" else "Global",
                "cases": today["cases"],
                "activeCases": today["active"],
                "todayCases": today["todayCases"],
                "deaths": today["deaths"],
                "todayDeaths": today["todayDeaths"],
                "recovered": today["recovered"],
                "todayRecovered": today["todayRecovered"],
                "tests": today["tests"],
                "todayTests": today["tests"] - yesterday["tests"],
                "updated": today["updated"],
                "population": today["population"]
            },
            "yesterday": {
                "cases": yesterday["cases"],
                "activeCases": yesterday["active"],
                "todayCases": yesterday["todayCases"],
                "deaths": yesterday["deaths"],
                "todayDeaths": yesterday["todayDeaths"],
                "recovered": yesterday["recovered"],
                "todayRecovered": yesterday["todayRecovered"],
                "tests": yesterday["tests"],
                "updated": yesterday["updated"],
                "population": yesterday["population"]
            }
        }

        return dic

    def getVaccineData(self, country: str, todayPopulation: int, yesterdayPopulation: int):
        """
        Function that gets vaccination stats for a specicic country.
        This information is later added to the embed.
        """
        if todayPopulation == 0:
            todayPopulation = 1

        if yesterdayPopulation == 0:
            yesterdayPopulation = 1

        # "all" has a different endpoint
        if country == "global":
            vaccine: dict = requests.get("https://disease.sh/v3/covid-19/vaccine/coverage?lastdays=3").json()
        else:
            vaccine: dict = requests.get("https://disease.sh/v3/covid-19/vaccine/coverage/countries/{}?lastdays=3"
                                         .format(country)).json()

        # Country-specific is structured differently
        if "timeline" in vaccine:
            vaccine = vaccine["timeline"]

        # Error message returned or not enough data yet
        if "message" in vaccine or len(vaccine.keys()) != 3:
            return None

        timeFormat = "%m/%d/%y"

        def getDt(dt):
            """
            Function that calls fromString with an argument
            so it can be used in map
            """
            return timeFormatters.fromString(dt, timeFormat)

        def toString(dt):
            """
            Function to cast datetime back to string
            """
            st: str = dt.strftime(timeFormat)

            # Api doesn't add leading zeroes so the keys don't match anymore ---'
            if st.startswith("0"):
                st = st[1:]

            if st[2] == "0":
                st = st[:2] + st[3:]

            return st

        # Order dates
        ordered = sorted(map(getDt, vaccine.keys()))
        # Datetime objects are only required for sorting, turn back into strings
        ordered = list(map(toString, ordered))

        info = {"today": {}, "yesterday": {}}

        # Total vaccines
        info["today"]["vaccines"] = vaccine[ordered[2]]
        # New vaccines today
        info["today"]["todayVaccines"] = vaccine[ordered[2]] - vaccine[ordered[1]]
        # % of total population
        info["today"]["perc"] = round(100 * vaccine[ordered[2]] / todayPopulation, 2)
        info["yesterday"]["vaccines"] = vaccine[ordered[1]]
        info["yesterday"]["todayVaccines"] = vaccine[ordered[1]] - vaccine[ordered[0]]

        return info

    def distribution(self, dic):
        """
        Calculates the percentage distribution for every key & shows an indicator.
        :param dic: the today/yesterday dictionary for this country
        :return: a list containing the distribution + indicator for active, recovered & deaths
        """
        totalToday = dic["today"]["cases"] if dic["today"]["cases"] != 0 else 1
        totalYesterday = dic["yesterday"]["cases"] if dic["yesterday"]["cases"] != 0 else 1

        tap = round(100 * dic["today"]["activeCases"] / totalToday, 2)  # Today Active Percentage
        trp = round(100 * dic["today"]["recovered"] / totalToday, 2)  # Today Recovered Percentage
        tdp = round(100 * dic["today"]["deaths"] / totalToday, 2)  # Today Deaths Percentage
        yap = round(100 * dic["yesterday"]["activeCases"] / totalYesterday, 2)  # Yesterday Active Percentage
        yrp = round(100 * dic["yesterday"]["recovered"] / totalYesterday, 2)  # Yesterday Recovered Percentage
        ydp = round(100 * dic["yesterday"]["deaths"] / totalYesterday, 2)  # Yesterday Deaths Percentage

        return ["{}% {}".format(tap, self.indicator(tap, yap)),
                "{}% {}".format(tdp, self.indicator(tdp, ydp)),
                "{}% {}".format(trp, self.indicator(trp, yrp))]

    async def sendError(self, ctx):
        """
        Function that sends an error embed when an invalid country was passed.
        :param ctx: Discord Context
        """
        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="Error", value="Dit land staat niet in de database.", inline=False)
        await ctx.send(embed=embed)

    # Returns a number and a percentage of rise/decline
    def trend(self, dic, key):
        """
        Function that creates a string representing a number & percentage of
        rise & decline for a certain key of the dict.
        :param dic: the today/yesterday dictionary for this country
        :param key: the key to compare
        :return: a string showing the increase in numbers & percentages
        """
        # Difference vs yesterday
        change = dic["today"][key] - dic["yesterday"][key]

        # Don't divide by 0
        yesterday = dic["yesterday"][key] if dic["yesterday"][key] != 0 else 1

        # Percentage
        perc = round(100 * change / yesterday, 2)

        # Sign to add to the number
        sign = "+" if change >= 0 else ""

        return "{}{:,} ({}{:,}%)".format(sign, change, sign, perc)

    # Requires a bit of math so this is a separate function
    def activeTrendIndicator(self, dic):
        """
        Function that returns a rise/decline indicator for the active cases of the day.
        This is a separate function as it requires some math to get right.
        New cases have to take into account the deaths & recovered cases being
        subtracted as well.
        :param dic: the today/yesterday dictionary for this country
        :return: a triangle emoji or empty string
        """
        todayNew = dic["today"]["todayCases"] - dic["today"]["todayDeaths"] - dic["today"]["todayRecovered"]
        yesterdayNew = dic["yesterday"]["todayCases"] - dic["yesterday"]["todayDeaths"] - dic["yesterday"][
            "todayRecovered"]

        return ":small_red_triangle:" if todayNew > yesterdayNew else \
            (":small_red_triangle_down:" if todayNew < yesterdayNew else "")

    # Returns an arrow indicating rise or decline
    def trendIndicator(self, dic, key):
        """
        Function that returns a rise/decline indicator for the target key.
        :param dic: the today/yesterday dictionary for this country
        :param key: the key to get the indicator for
        :return: a triangle emoji or empty string
        """
        return ":small_red_triangle:" if dic["today"][key] > dic["yesterday"][key] else \
            (":small_red_triangle_down:" if dic["today"][key] < dic["yesterday"][key] else "")

    # Also returns an indicator, but compares instead of pulling it out of the dic (for custom numbers)
    def indicator(self, today, yesterday):
        """
        Function that also returns an indicator but for two numbers
        instead of comparing values out of the dictionary.
        :param today: the number representing today
        :param yesterday: the number representing yesterday
        :return: a triangle emoji or empty string
        """
        return ":small_red_triangle:" if today > yesterday else \
            (":small_red_triangle_down:" if yesterday > today else "")


def setup(client):
    client.add_cog(Corona(client))
