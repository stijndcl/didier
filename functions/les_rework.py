from datetime import datetime, timedelta
from timeFormatters import dateTimeNow, weekdayToInt
from typing import Optional


def find_target_date(arg: Optional[str]) -> datetime:
    """
    Find the requested date out of the user's arguments
    """
    # Start at current date
    day: datetime = dateTimeNow()

    # If no offset was provided, check the time
    # otherwise the argument overrides it
    if arg is None:
        # When the command is used after 6 pm, show schedule
        # for the next day instead
        if day.hour > 18:
            day += timedelta(days=1)
    elif 0 <= (weekday := weekdayToInt(arg)) <= 4:  # Weekday provided
        day = forward_to_weekday(day, weekday)
    elif arg.lower() == "morgen":  # Tomorrow's schedule
        day += timedelta(days=1)
    elif arg.lower() == "overmorgen":  # Day after tomorrow's schedule
        day += timedelta(days=2)

    # Don't land on a weekend
    day = skip_weekends(day)

    return day


def skip_weekends(day: datetime) -> datetime:
    """
    Increment the current date if it's not a weekday
    """
    weekday = day.weekday()

    # Friday is weekday 4
    if weekday > 4:
        return day + timedelta(days=(7 - weekday))

    return day


def forward_to_weekday(day: datetime, weekday: int) -> datetime:
    """
    Increment a date until the weekday is the same as the one provided
    Finds the "next" [weekday]
    """
    current = day.weekday()

    # This avoids negative numbers below, and shows
    # next week in case the days are the same
    if weekday >= current:
        weekday += 7

    return day + timedelta(days=(weekday - current))
