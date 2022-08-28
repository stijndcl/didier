from datetime import datetime
from enum import Enum
from typing import Optional, cast

import discord
from overrides import overrides
from pydantic import BaseModel

from didier.data.embeds.base import EmbedPydantic
from didier.utils.discord.colours import ghent_university_blue, ghent_university_yellow
from didier.utils.types.datetime import int_to_weekday
from didier.utils.types.string import leading

__all__ = ["Menu", "no_menu_found"]


class _MealKind(str, Enum):
    FISH = "fish"
    MEAT = "meat"
    SOUP = "soup"
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"


class _MealType(str, Enum):
    COLD = "cold"
    MAIN = "main"
    SIDE = "side"


class _Meal(BaseModel):
    """Model for an item on the menu"""

    kind: _MealKind
    name: str
    price: str
    type: _MealType


class Menu(EmbedPydantic):
    """Embed that shows the menu in Ghent University restaurants"""

    meals: list[_Meal] = []
    open: bool
    vegetables: list[str] = []
    message: Optional[str] = None

    def _get_dutch_meal_prefix(self, meal: _Meal) -> str:
        if meal.kind == _MealKind.MEAT:
            prefix = "Vlees"
        elif meal.kind == _MealKind.FISH:
            prefix = "Vis"
        elif meal.kind == _MealKind.VEGETARIAN:
            prefix = "Vegetarisch"
        else:
            prefix = "Vegan"

        return prefix

    def _get_soups(self) -> str:
        acc = ""

        for meal in self.meals:
            if meal.kind == _MealKind.SOUP:
                acc += f"{meal.name} ({meal.price})\n"

        return acc.strip()

    def _get_main_courses(self) -> str:
        acc = ""

        for meal in self.meals:
            if meal.type != _MealType.MAIN:
                continue

            prefix = self._get_dutch_meal_prefix(meal)

            acc += f"* {prefix}: {meal.name} ({meal.price})\n"

        return acc.strip()

    def _get_cold_meals(self) -> str:
        acc = ""

        for meal in self.meals:
            if meal.type == _MealType.COLD:
                acc += f"* {self._get_dutch_meal_prefix(meal)}: {meal.name} ({meal.price})\n"

        return acc.strip()

    def _closed_embed(self, embed: discord.Embed) -> discord.Embed:
        embed.colour = ghent_university_yellow()
        embed.description = "The restaurants are closed today."
        return embed

    def _regular_embed(self, embed: discord.Embed) -> discord.Embed:
        embed.add_field(name="🥣 Soep", value=self._get_soups(), inline=False)
        embed.add_field(name="🍴 Hoofdgerechten", value=self._get_main_courses(), inline=False)
        embed.add_field(name="❄️Koud", value=self._get_cold_meals(), inline=False)

        vegetables = "\n".join(list(sorted(self.vegetables)))
        embed.add_field(name="🥦 Groenten", value=vegetables, inline=False)

        return embed

    @overrides
    def to_embed(self, **kwargs) -> discord.Embed:
        day_dt: datetime = cast(datetime, kwargs.get("day_dt"))
        weekday = int_to_weekday(day_dt.weekday())
        formatted_date = f"{leading('0', str(day_dt.day))}/{leading('0', str(day_dt.month))}/{day_dt.year}"

        embed = discord.Embed(title=f"Menu - {weekday} {formatted_date}", colour=ghent_university_blue())

        embed = self._regular_embed(embed) if self.open else self._closed_embed(embed)

        if self.message:
            embed.add_field(name="📣 Extra Mededeling", value=self.message, inline=False)

        return embed


def no_menu_found(day_dt: datetime) -> discord.Embed:
    """Return a different embed if no menu could be found"""
    embed = discord.Embed(title="Menu", colour=discord.Colour.red())
    embed.description = f"Unable to retrieve menu for {day_dt.strftime('%d/%m/%Y')}."
    return embed
