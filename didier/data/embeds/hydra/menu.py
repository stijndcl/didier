from datetime import datetime
from typing import Literal, Optional, cast

import discord
from overrides import overrides
from pydantic import BaseModel

from didier.data.embeds.base import EmbedPydantic
from didier.utils.discord.colours import ghent_university_blue
from didier.utils.types.datetime import int_to_weekday
from didier.utils.types.string import leading

__all__ = ["Menu", "no_menu_found"]


class _Meal(BaseModel):
    """Model for an item on the menu"""

    kind: Literal["meat", "fish", "soup", "vegetarian", "vegan"]
    name: str
    price: str
    type: Literal["cold", "main", "side"]


class Menu(EmbedPydantic):
    """Embed that shows the menu in Ghent University restaurants"""

    meals: list[_Meal] = []
    open: bool
    vegetables: list[str] = []
    message: Optional[str] = None

    @overrides
    def to_embed(self, **kwargs) -> discord.Embed:
        day_dt: datetime = cast(datetime, kwargs.get("day_dt"))
        weekday = int_to_weekday(day_dt.weekday())
        formatted_date = f"{leading('0', str(day_dt.day))}/{leading('0', str(day_dt.month))}/{day_dt.year}"

        embed = discord.Embed(title=f"Menu - {weekday} {formatted_date}", colour=ghent_university_blue())

        return embed


def no_menu_found(day_dt: datetime) -> discord.Embed:
    """Return a different embed if no menu could be found"""
    embed = discord.Embed(title="Menu", colour=discord.Colour.red())
    embed.description = f"Unable to retrieve menu for {day_dt.strftime('%d/%m/%Y')}."
    return embed
