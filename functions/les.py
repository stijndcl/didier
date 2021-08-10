from datetime import datetime, timedelta
from functions.timeFormatters import dateTimeNow, weekdayToInt, forward_to_weekday
from typing import Optional


def find_target_date(arg: Optional[str] = None) -> datetime:
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

    return day
