import contextlib
from datetime import date, timedelta
from typing import Optional

from discord.ext.commands import ArgumentParsingError

from didier.utils.types.datetime import (
    forward_to_next_weekday,
    parse_dm_string,
    str_to_weekday,
)

__all__ = ["date_converter"]


def date_converter(argument: Optional[str]) -> date:
    """Converter to turn a string into a date"""
    # Store original argument for error message purposes
    original_argument = argument

    # Default to today
    if not argument:
        return date.today()

    argument = argument.lower()

    # Manual offsets
    if argument in (
        "tomorrow",
        "tmrw",
        "morgen",
    ):
        return date.today() + timedelta(days=1)

    if argument in ("overmorgen",):
        return date.today() + timedelta(days=2)

    # Weekdays passed in words
    with contextlib.suppress(ValueError):
        weekday = str_to_weekday(argument)
        return forward_to_next_weekday(date.today(), weekday, allow_today=False)

    # Date strings
    with contextlib.suppress(ValueError):
        return parse_dm_string(argument)

    # Unparseable
    raise ArgumentParsingError(f"Unable to interpret `{original_argument}` as a date.")
