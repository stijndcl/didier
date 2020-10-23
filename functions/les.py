import datetime
import discord
from functions import config, timeFormatters, stringFormatters
from functions.numbers import clamp
import json

def createCourseString(courses):
    courseString = ""
    for course in sorted(courses, key=lambda item: item["slot"]["time"][1]):
        # Add a ":" to the hour + add a leading "0" if needed
        start = timeFormatters.timeFromInt(course["slot"]["time"][1])
        end = timeFormatters.timeFromInt(course["slot"]["time"][2])
        courseString += "{} - {}: {} {}\n".format(start, end,
                                                  str(course["course"]), getLocation(course["slot"]))
    return courseString


def createEmbed(day, dayDatetime, semester, year, schedule):
    # Create a date object to check the current week
    startDate = 1600041600
    currentTime = dayDatetime.timestamp()
    week = clamp(timeFormatters.timeIn(currentTime - startDate, "weeks")[0], 1, 13)

    title, week = getTitle(day, dayDatetime, week)

    # Add all courses & their corresponding times + locations of today
    courses, extras, prev, online = getCourses(schedule, day, week)

    embed = discord.Embed(colour=discord.Colour.blue(), title=title)
    embed.set_author(name="Lessenrooster voor {}{} Bachelor".format(year, "ste" if year == 1 else "de"))

    if len(courses) == 0:
        embed.add_field(name="Geen Les", value="Geen Les", inline=False)
    else:
        courseString = createCourseString(courses)
        courseString += "\nGroep {} heeft vandaag online les.".format(1 if week % 2 == 0 else 2)
        embed.description = courseString

        if prev:
            embed.add_field(name="Vakken uit vorige jaren", value=createCourseString(prev), inline=False)

        if extras:
            embed.add_field(name="Extra", value="\n".join(getExtras(extra) for extra in extras), inline=False)

        # Add online links
        if online:
            embed.add_field(name="Online Links", value="\n".join(getLink(onlineClass) for onlineClass in online))

        embed.set_footer(text="Semester  {} | Lesweek {}".format(semester, round(week)))
    return embed


def findDate(targetWeekday):
    now = timeFormatters.dateTimeNow()
    while now.weekday() != targetWeekday:
        now = now + datetime.timedelta(days=1)
    return now


def getCourses(schedule, day, week):
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


def getExtras(extra):
    start = timeFormatters.timeFromInt(extra["slot"]["time"][1])
    end = timeFormatters.timeFromInt(extra["slot"]["time"][2])

    location = getLocation(extra["slot"])

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


def getLink(onlineClass):
    return "{}: **[{}]({})**".format(onlineClass["course"], onlineClass["online"], onlineClass["link"])


def getLocation(slot):
    if "canceled" in slot:
        return None

    if "online" in slot:
        return "online @ **[{}]({})**".format(slot["online"], slot["zoom"] if slot["online"] == "ZOOM" else slot["bongo"])

    # Check for courses in multiple locations
    if "locations" in slot:
        # Language - 'en' for the last one
        return ", ".join(getLocation(location) for location in slot["locations"][:-1]) \
               + " en " + getLocation(slot["locations"][-1])
    return "in {} {} {}".format(slot["campus"], slot["building"], slot["room"])


def getSchedule(semester, year):
    with open("files/schedules/{}{}.json".format(year, semester), "r") as fp:
        schedule = json.load(fp)

    return schedule


def getTitle(day, dayDT, week):
    # now = timeFormatters.dateTimeNow()
    # if timeFormatters.weekdayToInt(day) < now.weekday():
    #     week += 1

    day = day[0].upper() + day[1:].lower()

    titleString = "{} {}/{}/{}".format(day, stringFormatters.leadingZero(dayDT.day),
                                           stringFormatters.leadingZero(dayDT.month), dayDT.year)
    return titleString, week


# Returns the day of the week, while keeping track of weekends
def getWeekDay(day=None):
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


def parseArgs(day):
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
                    return [False, "Dit is geen geldige jaargang."]
            # elif: calling a weekday is automatically handled below,
            # so checking is obsolete
        else:
            # Both were passed
            if day[0].isdigit():
                if 0 < int(day[0]) < years_counter + 1:
                    year = int(day[0])
                    day = []
                else:
                    return [False, "Dit is geen geldige jaargang."]
            # Cut the schedule from the string
            day = day[1:]

    day = getWeekDay(None if len(day) == 0 else day)[1]
    dayDatetime = findDate(timeFormatters.weekdayToInt(day))

    return [True, day, dayDatetime, semester, year]
