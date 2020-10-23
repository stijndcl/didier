from data import constants
from decorators import help
import discord
from discord.ext import commands
from enums.courses import years
from enums.help_categories import Category
from functions import checks, eten, les
import json


class School(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Don't allow any commands to work when locked
    def cog_check(self, ctx):
        return not self.client.locked

    @commands.command(name="Eten", aliases=["Food", "Menu"], usage="[Dag]*")
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.School)
    async def eten(self, ctx, *day):
        day = les.getWeekDay(None if len(day) == 0 else day)[1]

        # Create embed
        menu = eten.etenScript(day)
        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="Menu voor {}".format(day))
        if "gesloten" in menu[0].lower():
            embed.description = "Restaurant gesloten"
        else:
            embed.add_field(name="Soep:", value=menu[0], inline=False)
            embed.add_field(name="Hoofdgerechten:", value=menu[1], inline=False)

            if menu[2]:
                embed.add_field(name="Groenten:", value=menu[2], inline=False)

            embed.set_footer(text="Omwille van de coronamaatregelen is er een beperkter aanbod, en kan je enkel nog eten afhalen. Ter plaatse eten is niet meer mogelijk.")
        await ctx.send(embed=embed)

    @commands.command(name="Les", aliases=["Class", "Classes", "Sched", "Schedule"], usage="[Jaargang]* [Dag]*")
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.School)
    async def les(self, ctx, *day):
        parsed = les.parseArgs(day)

        # Invalid arguments
        if not parsed[0]:
            return await ctx.send(parsed[1])

        day, dayDatetime, semester, year = parsed[1:]

        # Customize the user's schedule
        schedule = self.customizeSchedule(ctx, year, semester)

        # Create the embed
        embed = les.createEmbed(day, dayDatetime, semester, year, schedule)

        await ctx.send(embed=embed)

    # Add all the user's courses
    def customizeSchedule(self, ctx, year, semester):
        schedule = les.getSchedule(semester, year)

        member = self.client.get_guild(int(constants.CallOfCode)).get_member(ctx.author.id)
        for role in member.roles:
            for univYear in years:
                for course in univYear:
                    if course.value["year"] < year and course.value["id"] == role.id and course.value["semester"] == semester:
                        with open("files/schedules/{}{}.json".format(course.value["year"], course.value["semester"]),
                                  "r") as fp:
                            sched2 = json.load(fp)

                        for val in sched2:
                            if val["course"] == course.value["name"]:
                                val["custom"] = course.value["year"]
                                schedule.append(val)
        return schedule


def setup(client):
    client.add_cog(School(client))
