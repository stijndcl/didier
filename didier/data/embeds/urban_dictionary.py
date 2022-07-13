from datetime import datetime

import discord
from overrides import overrides

from didier.data.embeds.base import EmbedPydantic

__all__ = ["Definition"]


class Definition(EmbedPydantic):
    """A definition from the Urban Dictionary"""

    word: str
    definition: str
    permalink: str
    author: str
    thumbs_up: int
    thumbs_down: int
    written_on: datetime

    @overrides
    def to_embed(self) -> discord.Embed:
        embed = discord.Embed()
