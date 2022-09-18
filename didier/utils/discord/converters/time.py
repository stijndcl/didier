import contextlib
import datetime
from datetime import date, timedelta
from typing import Optional, Union

import discord
from discord import app_commands
from discord.ext import commands
from overrides import overrides

from didier.utils.discord.autocompletion.time import autocomplete_day
from didier.utils.types.datetime import (
    forward_to_next_weekday,
    parse_dm_string,
    str_to_weekday,
)

__all__ = ["date_converter", "DateTransformer"]


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
    raise commands.ArgumentParsingError(f"Unable to interpret `{original_argument}` as a date.")


class DateTransformer(commands.Converter, app_commands.Transformer):
    """Application commands transformer for dates"""

    @overrides
    async def autocomplete(
        self, interaction: discord.Interaction, value: Union[int, float, str]
    ) -> list[app_commands.Choice[Union[int, float, str]]]:
        return autocomplete_day(str(value))

    @overrides
    async def convert(self, ctx: commands.Context, argument: str) -> datetime.date:
        return date_converter(argument)

    @overrides
    async def transform(self, interaction: discord.Interaction, value: str) -> datetime.date:
        return date_converter(value)
