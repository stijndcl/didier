from typing import Literal, Optional

import discord
from overrides import overrides
from pydantic import BaseModel

from didier.data.embeds.base import EmbedPydantic
from didier.utils.discord.colours import ghent_university_blue

__all__ = ["Menu"]


class _Meal(BaseModel):
    """Model for an item on the menu"""

    kind: Literal["meat", "fish", "soup", "vegetarian", "vegan"]
    name: str
    price: str
    type: Literal["main", "side"]


class Menu(EmbedPydantic):
    """Embed that shows the menu in Ghent University restaurants"""

    meals: list[_Meal] = []
    open: bool
    vegetables: list[str] = []
    message: Optional[str] = None

    @overrides
    def to_embed(self, **kwargs: dict) -> discord.Embed:
        embed = discord.Embed(title="Menu", colour=ghent_university_blue())

        return embed
