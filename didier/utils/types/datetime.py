import datetime
import zoneinfo

__all__ = ["LOCAL_TIMEZONE", "int_to_weekday", "str_to_date", "tz_aware_now"]

from typing import Union

LOCAL_TIMEZONE = zoneinfo.ZoneInfo("Europe/Brussels")


def int_to_weekday(number: int) -> str:  # pragma: no cover # it's useless to write a test for this
    """Get the Dutch name of a weekday from the number"""
    return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][number]


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


def tz_aware_now() -> datetime.datetime:
    """Get the current date & time, but timezone-aware"""
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).astimezone(LOCAL_TIMEZONE)
