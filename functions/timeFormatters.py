import datetime
import time

import dateutil.relativedelta
import pytz


def epochToDate(epochTimeStamp, strFormat="%m/%d/%Y om %H:%M:%S"):
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


def weekdayToInt(day):
    days = {"maandag": 0, "dinsdag": 1, "woensdag": 2, "donderdag": 3, "vrijdag": 4, "zaterdag": 5, "zondag": 6}
    return days[day.lower()]


def intToWeekday(day):
    return ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"][day]
