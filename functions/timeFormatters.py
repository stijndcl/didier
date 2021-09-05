import datetime
from typing import List

import dateutil.relativedelta
import pytz
import time

from functions import stringFormatters


def epochToDate(epochTimeStamp, strFormat="%d/%m/%Y om %H:%M:%S"):
    now = dateTimeNow()
    updateTime = datetime.datetime.fromtimestamp(int(epochTimeStamp), pytz.timezone("Europe/Brussels"))
    diff = now - updateTime
    updateFormatted = str(updateTime.strftime(strFormat))
    timeAgo = str(time.strftime('%H:%M:%S', time.gmtime(diff.total_seconds())))
    return {"date": updateFormatted, "dateDT": updateTime, "timeAgo": timeAgo}


def dateTimeNow():
    return datetime.datetime.now(pytz.timezone("Europe/Brussels"))


def leadingZero(hourMinutes):
    return ("0" if len(hourMinutes) == 3 else "") + hourMinutes


def delimiter(hourMinutes, delim=":"):
    return hourMinutes[:2] + delim + hourMinutes[2:]


def timeFromInt(value):
    return delimiter(leadingZero(str(value)))


# Returns age in YMWD
def age(seconds):
    # Amount of years
    years, seconds = timeIn(seconds, "years")
    months, seconds = timeIn(seconds, "months")
    weeks, seconds = timeIn(seconds, "weeks")
    days, seconds = timeIn(seconds, "days")

    return {"years": years, "months": months, "weeks": weeks, "days": days}


# Returns amount of [unit] in [seconds] + the remaining seconds
def timeIn(seconds, unit):
    timeDic = {"years": 31556926, "months": 2629743, "weeks": 604800, "days": 86400}
    timeUnit = timeDic[unit]
    return seconds // timeUnit, seconds - ((seconds // timeUnit) * timeUnit)


# Creates a string representation based on Days/Hours/Minutes/Seconds
def diffDayBasisString(timestamp):
    if isinstance(timestamp, int):
        timestamp = epochToDate(timestamp)["dateDT"]
    now = dateTimeNow()
    diff = dateutil.relativedelta.relativedelta(now, timestamp)

    timeList = []

    # Don't add obsolete info such as "0 days", ...
    if diff.days != 0:
        timeList.append("{} {}".format(diff.days, getPlural(diff.days, "days")))

    if diff.hours != 0:
        timeList.append("{} uur".format(diff.hours))

    if diff.minutes != 0:
        timeList.append("{} {}".format(diff.minutes, getPlural(diff.minutes, "minutes")))

    if diff.seconds != 0:
        timeList.append("{} {}".format(diff.seconds, getPlural(diff.seconds, "seconds")))

    timeString = ", ".join(timeList[:-1])
    if len(timeString) > 0:
        timeString += " en "
    timeString += timeList[-1]
    return timeString


def diffYearBasisString(timestamp):
    if isinstance(timestamp, int):
        timestamp = epochToDate(timestamp)["dateDT"]
    now = dateTimeNow()
    diff = dateutil.relativedelta.relativedelta(now, timestamp)
    timeList = []

    # Don't add obsolete info such as "0 days", ...
    if diff.years != 0:
        timeList.append("{} jaar".format(diff.years))

    if diff.months != 0:
        timeList.append("{} {}".format(diff.months, getPlural(diff.months, "months")))

    if diff.weeks != 0:
        timeList.append("{} {}".format(diff.weeks, getPlural(diff.weeks, "weeks")))

    if diff.days != 0:
        timeList.append("{} {}".format(diff.days, getPlural(diff.days, "days")))

    timeString = ""

    if not timeList:
        return "Minder dan een dag"

    if len(timeList) > 1:
        timeString = ", ".join(timeList[:-1])
    if len(timeString) > 0:
        timeString += " en "

    timeString += timeList[-1]

    return timeString


# Returns the full day based on an abbreviation or full name
def getFormat(term):
    terms = ["days", "weeks", "months", "years"]
    for word in terms:
        if word.startswith(term.lower()):
            return word
    return None


# Gets the plural of a unit if necessary
def getPlural(amount, unit):
    dic = {
        "seconds": {"s": "seconde", "p": "seconden"},
        "minutes": {"s": "minuut", "p": "minuten"},
        "hours": {"s": "uur", "p": "uur"},
        "days": {"s": "dag", "p": "dagen"},
        "weeks": {"s": "week", "p": "weken"},
        "months": {"s": "maand", "p": "maanden"},
        "years": {"s": "jaar", "p": "jaar"}
    }
    return dic[unit.lower()]["s" if amount == 1 else "p"]


def weekdayToInt(day: str) -> int:
    days = {"maandag": 0, "dinsdag": 1, "woensdag": 2, "donderdag": 3, "vrijdag": 4, "zaterdag": 5, "zondag": 6}

    # Allow abbreviations
    for d, i in days.items():
        if d.startswith(day):
            return i

    return -1


def intToWeekday(day):
    return ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"][day]


def fromString(timeString: str, formatString="%d/%m/%Y", tzinfo=pytz.timezone("Europe/Brussels")):
    """
    Constructs a datetime object from an input string
    """
    return datetime.datetime.strptime(timeString, formatString).replace(tzinfo=tzinfo)


def fromArray(data: List[int]) -> datetime:
    day = stringFormatters.leading_zero(str(data[0]))
    month = stringFormatters.leading_zero(str(data[1]))
    year = str(data[2])

    if len(data) == 6:
        hour = stringFormatters.leading_zero(str(data[3]))
        minute = stringFormatters.leading_zero(str(data[4]))
        second = stringFormatters.leading_zero(str(data[5]))

        return fromString(f"{day}/{month}/{year} {hour}:{minute}:{second}", formatString="%d/%m/%Y %H:%M:%S")

    return fromString(f"{day}/{month}/{year}")


def skip_weekends(day: datetime) -> datetime:
    """
    Increment the current date if it's not a weekday
    """
    weekday = day.weekday()

    # Friday is weekday 4
    if weekday > 4:
        return day + datetime.timedelta(days=(7 - weekday))

    return day


def forward_to_weekday(day: datetime, weekday: int) -> datetime:
    """
    Increment a date until the weekday is the same as the one provided
    Finds the "next" [weekday]
    """
    current = day.weekday()

    # This avoids negative numbers below, and shows
    # next week in case the days are the same
    if weekday <= current:
        weekday += 7

    return day + datetime.timedelta(days=(weekday - current))
