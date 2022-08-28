import datetime
import re
import zoneinfo
from typing import TypeVar, Union

__all__ = [
    "LOCAL_TIMEZONE",
    "forward_to_next_weekday",
    "int_to_weekday",
    "parse_dm_string",
    "str_to_date",
    "str_to_month",
    "str_to_weekday",
    "tz_aware_now",
]

DateType = TypeVar("DateType", datetime.date, datetime.datetime)

LOCAL_TIMEZONE = zoneinfo.ZoneInfo("Europe/Brussels")


def forward_to_next_weekday(day_dt: DateType, target_weekday: int, *, allow_today: bool = False) -> DateType:
    """Forward a date to the next occurence of a weekday"""
    if not 0 <= target_weekday <= 6:
        raise ValueError

    # Skip at least one day
    if not allow_today:
        day_dt += datetime.timedelta(days=1)

    while day_dt.weekday() != target_weekday:
        day_dt += datetime.timedelta(days=1)

    return day_dt


def int_to_weekday(number: int) -> str:  # pragma: no cover # it's useless to write a test for this
    """Get the Dutch name of a weekday from the number"""
    return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][number]


def parse_dm_string(argument: str) -> datetime.date:
    """Parse a string to [day]/[month]

    The year is set to the current year by default, as this can be changed easily.

    This supports:
    - DD/MM
    - DD (month defaults to current)
    - DD [Dutch Month, possibly abbreviated]
    - DD [English Month, possibly abbreviated]
    - [Dutch Month, possibly abbreviated] DD
    - [English Month, possibly abbreviated] DD
    """
    argument = argument.lower()
    today = datetime.date.today()

    # DD/MM
    if "/" in argument:
        spl = argument.split("/")
        if len(spl) != 2:
            raise ValueError

        return datetime.date(day=int(spl[0]), month=int(spl[1]), year=today.year)

    # Try to interpret text
    spl = argument.split(" ")
    if len(spl) != 2:
        raise ValueError

    # Day Month
    match = re.search(r"\d+", spl[0])
    if match is not None:
        day = int(match.group())
        month = str_to_month(spl[1])
        return datetime.date(day=day, month=month, year=today.year)

    # Month Day
    match = re.search(r"\d+", spl[0])
    if match is not None:
        day = int(match.group())
        month = str_to_month(spl[0])
        return datetime.date(day=day, month=month, year=today.year)

    # Unparseable
    raise ValueError


def str_to_date(date_str: str, formats: Union[list[str], str] = "%d/%m/%Y") -> datetime.date:
    """Turn a string into a DD/MM/YYYY date"""
    # Allow passing multiple formats in a list
    if isinstance(formats, str):
        formats = [formats]

    for format_str in formats:
        try:
            return datetime.datetime.strptime(date_str, format_str).date()
        except ValueError:
            continue

    raise ValueError


def str_to_month(argument: str) -> int:
    """Turn a string int oa month, bilingual"""
    argument = argument.lower()

    month_dict = {
        # English
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        # August is a prefix of Augustus so it is skipped
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
        # Dutch
        "januari": 1,
        "februari": 2,
        "maart": 3,
        # April is the same in English so it is skipped
        "mei": 5,
        "juni": 6,
        "juli": 7,
        "augustus": 8,
        # September is the same in English so it is skipped
        "oktober": 10,
        # November is the same in English so it is skipped
        # December is the same in English so it is skipped
    }

    for key, value in month_dict.items():
        if key.startswith(argument):
            return value

    raise ValueError


def str_to_weekday(argument: str) -> int:
    """Turn a string into a weekday, bilingual"""
    argument = argument.lower()

    weekday_dict = {
        # English
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
        # Dutch
        "maandag": 0,
        "dinsdag": 1,
        "woensdag": 2,
        "donderdag": 3,
        "vrijdag": 4,
        "zaterdag": 5,
        "zondag": 6,
    }

    for key, value in weekday_dict.items():
        if key.startswith(argument):
            return value

    raise ValueError


def tz_aware_now() -> datetime.datetime:
    """Get the current date & time, but timezone-aware"""
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).astimezone(LOCAL_TIMEZONE)
