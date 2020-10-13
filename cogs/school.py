from data import constants
import datetime
from decorators import help
import discord
from discord.ext import commands
from enums.courses import years
from enums.help_categories import Category
from functions import checks, eten, timeFormatters, config, stringFormatters
from functions.numbers import clamp
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
        day = self.getWeekDay(None if len(day) == 0 else day)[1]

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

    @commands.command(name="Les", aliases=["Sched", "Schedule", "Class"], usage="[Jaargang]* [Dag]*")
    @commands.check(checks.allowedChannels)
    @help.Category(category=Category.School)
    async def les(self, ctx, *day):
        semester = int(config.get("semester"))
        year = int(config.get("year"))
        years_counter = int(config.get("years"))
        # Check if a schedule or a day was called
        if len(day) == 0:
            day = []
        else:
            # Only either of them was passed
            if len(day) == 1:
                # Called a schedule
                if day[0].isdigit():
                    if 0 < int(day[0]) < years_counter + 1:
                        year = int(day[0])
                        day = []
                    else:
                        return await ctx.send("Dit is geen geldige jaargang.")
                # elif: calling a weekday is automatically handled below,
                # so checking is obsolete
            else:
                # Both were passed
                if day[0].isdigit():
                    if 0 < int(day[0]) < years_counter + 1:
                        year = int(day[0])
                        day = []
                    else:
                        return await ctx.send("Dit is geen geldige jaargang.")
                # Cut the schedule from the string
                day = day[1:]

        day = self.getWeekDay(None if len(day) == 0 else day)[1]
        dayDatetime = self.findDate(timeFormatters.weekdayToInt(day))

        schedule = self.customizeSchedule(ctx, year, semester)

        # Create a date object to check the current week
        startDate = 1600041600
        currentTime = dayDatetime.timestamp()
        week = clamp(timeFormatters.timeIn(currentTime - startDate, "weeks")[0], 1, 13)

        title, week = self.getTitle(day, dayDatetime, week)

        # Add all courses & their corresponding times + locations of today
        courses, extras, prev, online = self.getCourses(schedule, day, week)

        embed = discord.Embed(colour=discord.Colour.blue(), title=title)
        embed.set_author(name="Lessenrooster voor {}{} Bachelor".format(year, "ste" if year == 1 else "de"))

        if len(courses) == 0:
            embed.add_field(name="Geen Les", value="Geen Les", inline=False)
        else:
            courseString = self.createCourseString(courses)
            courseString += "\nGroep {} heeft vandaag online les.".format(1 if week % 2 == 0 else 2)
            embed.description = courseString

            if prev:
                embed.add_field(name="Vakken uit vorige jaren", value=self.createCourseString(prev), inline=False)

            if extras:
                embed.add_field(name="Extra", value="\n".join(self.getExtras(extra) for extra in extras), inline=False)

            # Add online links if not commnet
            if online:
                embed.add_field(name="Online Links", value="\n".join(self.getLink(onlineClass) for onlineClass in online))

            embed.set_footer(text="Semester  {} | Lesweek {}".format(semester, round(week)))
        await ctx.send(embed=embed)

    def getLink(self, onlineClass):
        return "{}: **[{}]({})**".format(onlineClass["course"], onlineClass["online"], onlineClass["link"])

    def createCourseString(self, courses):
        courseString = ""
        for course in sorted(courses, key=lambda item: item["slot"]["time"][1]):
            # Add a ":" to the hour + add a leading "0" if needed
            start = timeFormatters.timeFromInt(course["slot"]["time"][1])
            end = timeFormatters.timeFromInt(course["slot"]["time"][2])
            courseString += "{} - {}: {} {}\n".format(start, end,
                                                         str(course["course"]), self.getLocation(course["slot"]))
        return courseString

    # Returns the day of the week, while keeping track of weekends
    def getWeekDay(self, day=None):
        weekDays = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag"]

        # Get current day of the week
        dayNumber = datetime.datetime.today().weekday()
        # If a day or a modifier was passed, show that day instead
        if day is not None:
            if day[0] == "morgen":
                dayNumber += 1
            elif day[0] == "overmorgen":
                dayNumber += 2
            else:
                for i in range(5):
                    if weekDays[i].startswith(day):
                        dayNumber = i
        # Weekends should be skipped
        dayNumber = dayNumber % 7
        if dayNumber > 4:
            dayNumber = 0

        # Get daystring
        return dayNumber, weekDays[dayNumber]

    def getLocation(self, slot):
        if "canceled" in slot:
            return None

        if "online" in slot:
            return "online @ **[{}]({})**".format(slot["online"], slot["zoom"] if slot["online"] == "ZOOM" else slot["bongo"])

        # Check for courses in multiple locations
        if "locations" in slot:
            # Language - 'en' for the last one
            return ", ".join(self.getLocation(location) for location in slot["locations"][:-1]) \
                   + " en " + self.getLocation(slot["locations"][-1])
        return "in {} {} {}".format(slot["campus"], slot["building"], slot["room"])

    def getCourses(self, schedule, day, week):
        # Add all courses & their corresponding times + locations of today
        courses = []

        extras = []

        prev = []

        onlineLinks = []

        for course in schedule:
            for slot in course["slots"]:
                if day in slot["time"]:
                    classDic = {"course": course["course"], "slot": slot}

                    # Class was canceled
                    if "canceled" in slot and "weeks" in slot and week in slot["weeks"]:
                        extras.append(classDic)
                        continue

                    # Add online links for those at home
                    if not any(el["course"] == course["course"] for el in onlineLinks):
                        if "bongo" in course:
                            onlineDic = {"course": course["course"], "online": "Bongo Virtual Classroom", "link": course["bongo"]}
                            onlineLinks.append(onlineDic)
                        elif "zoom" in course:
                            onlineDic = {"course": course["course"], "online": "Zoom", "link": course["zoom"]}
                            onlineLinks.append(onlineDic)

                    # Add this class' bongo & zoom links
                    if "bongo" in course:
                        classDic["slot"]["bongo"] = course["bongo"]

                    if "zoom" in course:
                        classDic["slot"]["zoom"] = course["zoom"]

                    if "custom" in course:
                        prev.append(classDic)

                    # Check for special classes
                    if "weeks" in slot and "online" not in slot:
                        if week in slot["weeks"]:
                            if "custom" not in course:
                                courses.append(classDic)
                            extras.append(classDic)
                    elif "weeks" in slot and "online" in slot and "group" not in slot:
                        if week in slot["weeks"]:
                            if "custom" not in course:
                                courses.append(classDic)
                            extras.append(classDic)

                    else:
                        if "custom" not in course:
                            courses.append(classDic)

        # Filter out normal courses that are replaced with special courses
        for extra in extras:
            for course in courses:
                if course["slot"]["time"] == extra["slot"]["time"] and course != extra:
                    courses.remove(course)
                    break

        # Sort online links alphabetically
        onlineLinks.sort(key=lambda x: x["course"])

        # Remove links of canceled classes
        for element in onlineLinks:
            if not any(c["course"] == element["course"] for c in courses):
                onlineLinks.remove(element)

        return courses, extras, prev, onlineLinks

    def getTitle(self, day, dayDT, week):
        # now = timeFormatters.dateTimeNow()
        # if timeFormatters.weekdayToInt(day) < now.weekday():
        #     week += 1

        day = day[0].upper() + day[1:].lower()

        titleString = "{} {}/{}/{}".format(day, stringFormatters.leadingZero(dayDT.day),
                                           stringFormatters.leadingZero(dayDT.month), dayDT.year)
        return titleString, week

    def getExtras(self, extra):
        start = timeFormatters.timeFromInt(extra["slot"]["time"][1])
        end = timeFormatters.timeFromInt(extra["slot"]["time"][2])

        location = self.getLocation(extra["slot"])

        if "canceled" in extra["slot"]:
            return "De les **{}** van **{}** tot **{}** gaat vandaag uitzonderlijk **niet** door.".format(
                extra["course"], start, end
            )

        if "group" in extra["slot"]:
            return "**Groep {}** heeft vandaag uitzonderlijk **{}** **{}** van **{} tot {}**.".format(
                extra["slot"]["group"], extra["course"], location,
                start, end
            )
        elif "online" in extra["slot"]:
            return "**{}** gaat vandaag uitzonderlijk online door {} van **{} tot {}**.".format(
                extra["course"], location[7:],
                start, end
            )
        else:
            return "**{}** vindt vandaag uitzonderlijk plaats **{}** van **{} tot {}**.".format(
                extra["course"], location,
                start, end
            )

    def findDate(self, targetWeekday):
        now = timeFormatters.dateTimeNow()
        while now.weekday() != targetWeekday:
            now = now + datetime.timedelta(days=1)
        return now

    # Add all the user's courses
    def customizeSchedule(self, ctx, year, semester):
        with open("files/schedules/{}{}.json".format(year, semester), "r") as fp:
            schedule = json.load(fp)
        return schedule
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
