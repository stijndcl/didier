import datetime
import discord
from functions import config, timeFormatters, stringFormatters
from functions.numbers import clamp
import json


# TODO use constants & enums instead of hardcoding platform names
#   also make the naming in the jsons more consistent

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
        # TODO uncomment this when covid rules slow down
        # courseString += "\nGroep {} heeft vandaag online les.".format(1 if week % 2 == 0 else 2)
        embed.description = courseString

        if prev:
            embed.add_field(name="Vakken uit vorige jaren", value=createCourseString(prev), inline=False)

        if extras:
            embed.add_field(name="Extra", value="\n".join(getExtras(extra) for extra in extras), inline=False)

        # TODO uncomment this when covid rules slow down
        # Add online links - temporarily removed because everything is online right now
        # if online:
        #     uniqueLinks: dict = getUniqueLinks(online)
        #     embed.add_field(name="Online Links", value="\n".join(
        #         sorted(getLinks(onlineClass, links) for onlineClass, links in uniqueLinks.items())))

        embed.set_footer(text="Semester  {} | Lesweek {}".format(semester, round(week)))
    return embed


def findDate(targetWeekday):
    """
    Function that finds the datetime object that corresponds to
    the next occurence of [targetWeekday].
    :param targetWeekday: The weekday to find
    """
    now = timeFormatters.dateTimeNow()
    while now.weekday() != targetWeekday:
        now = now + datetime.timedelta(days=1)
    return now


def getCourses(schedule, day, week):
    """
    Function that creates a list of all courses of this day,
    a list of all online links, and extra information for these courses.
    :param schedule: A user's (customized) schedule
    :param day: The current weekday
    :param week: The current week
    """
    # Add all courses & their corresponding times + locations of today
    courses = []
    extras = []
    prev = []
    onlineLinks = []

    for course in schedule:
        for slot in course["slots"]:
            if day in slot["time"]:
                # Basic dict containing the course name & the class' time slot
                classDic = {"course": course["course"], "slot": slot}

                # Class was canceled
                if "canceled" in slot and "weeks" in slot and week in slot["weeks"]:
                    extras.append(classDic)
                    continue

                # Add online links for those at home
                # Check if link hasn't been added yet
                if "online" in slot and not any(el["course"] == course["course"] and
                                                # Avoid KeyErrors: if either of these don't have an online link yet,
                                                # add it as well
                                                ("online" not in el or el["online"] == slot["online"])
                                                for el in onlineLinks):
                    # Some courses have multiple links on the same day,
                    # add all of them
                    if "bongo" in slot["online"].lower():
                        onlineDic = {"course": course["course"], "online": "Bongo Virtual Classroom",
                                     "link": course["bongo"]}
                        onlineLinks.append(onlineDic)

                    if "zoom" in slot["online"].lower():
                        onlineDic = {"course": course["course"], "online": "ZOOM", "link": course["zoom"]}
                        onlineLinks.append(onlineDic)

                    if "teams" in slot["online"].lower():
                        onlineDic = {"course": course["course"], "online": "MS Teams", "link": course["msteams"]}
                        onlineLinks.append(onlineDic)

                # Add this class' bongo, msteams & zoom links
                if "bongo" in course:
                    classDic["slot"]["bongo"] = course["bongo"]

                if "msteams" in course:
                    classDic["slot"]["msteams"] = course["msteams"]

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
                    # This class is only online for this week
                    if week in slot["weeks"]:
                        if "custom" not in course:
                            courses.append(classDic)
                        extras.append(classDic)
                else:
                    # Nothing special happening, just add it to the list of courses
                    # in case this is a course for everyone in this year
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
    """
    Function that returns a formatted string giving clear info
    when a course is happening somewhere else (or canceled).
    """
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
        return "**{}** gaat vandaag uitzonderlijk **online** door {} van **{} tot {}**.".format(
            extra["course"], location[7:],
            start, end
        )
    else:
        return "**{}** vindt vandaag uitzonderlijk plaats **{}** van **{} tot {}**.".format(
            extra["course"], location,
            start, end
        )


def getUniqueLinks(onlineClasses):
    """
    Function that returns a dict of all online unique online links for every class
    in case some classes have multiple links on the same day.
    """
    # Create a list of all unique course names
    courseNames = list(set(oc["course"] for oc in onlineClasses))
    uniqueLinks: dict = {}

    # Add every link of every class into the dict
    for name in courseNames:
        uniqueLinks[name] = {}
        for oc in onlineClasses:
            if oc["course"] == name:
                # Add the link for this platform
                uniqueLinks[name][oc["online"]] = oc["link"]

    return uniqueLinks


def getLinks(onlineClass, links):
    """
    Function that returns a formatted string giving a hyperlink
    to every online link for this class today.
    """
    return "{}: {}".format(onlineClass,
                           " | ".join(
                               ["**[{}]({})**".format(platform, url) for platform, url in
                                links.items()])
                           )


def getLocation(slot):
    """
    Function that returns a formatted string indicating where this course
    is happening.
    """
    if "canceled" in slot:
        return None

    # TODO fix this because it's ugly
    if "online" in slot:
        return "online @ **[{}]({})**".format(slot["online"],
                                              slot["zoom"] if slot["online"] == "ZOOM" else slot["msteams"] if slot[
                                                                                                                   "online"] == "MS Teams" else
                                              slot["bongo"])

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
            # TODO check other direction (di 1) in else
            # Both were passed
            if day[0].isdigit():
                if 0 < int(day[0]) < years_counter + 1:
                    year = int(day[0])
                    # day = []
                else:
                    return [False, "Dit is geen geldige jaargang."]
            # Cut the schedule from the string
            day = day[1:]
    day = getWeekDay(None if len(day) == 0 else day)[1]
    dayDatetime = findDate(timeFormatters.weekdayToInt(day))

    return [True, day, dayDatetime, semester, year]
