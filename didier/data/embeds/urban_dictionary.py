from datetime import datetime

import discord
from overrides import overrides
from pydantic import field_validator

from didier.data.embeds.base import EmbedPydantic
from didier.utils.discord import colours
from didier.utils.discord.constants import Limits
from didier.utils.types import string as string_utils

__all__ = ["Definition"]


class Definition(EmbedPydantic):
    """A definition from the Urban Dictionary"""

    word: str
    definition: str
    example: str
    permalink: str
    author: str
    thumbs_up: int
    thumbs_down: int
    written_on: datetime

    @property
    def ratio(self) -> float:
        """The up vote/down vote ratio

        This ratio is rounded down to 2 decimal places
        If the amount of down votes is 0, always return 100%
        """
        # No down votes, possibly no up votes either
        # Avoid a 0/0 situation
        if self.thumbs_down == 0:
            return 100

        total_votes = self.thumbs_up + self.thumbs_down
        return round(100 * self.thumbs_up / total_votes, 2)

    @field_validator("definition", "example")
    def modify_long_text(cls, field: str):
        """Remove brackets from fields & cut them off if they are too long"""
        field = field.replace("[", "").replace("]", "")
        return string_utils.abbreviate(field, max_length=Limits.EMBED_FIELD_VALUE_LENGTH)

    @overrides
    def to_embed(self, **kwargs) -> discord.Embed:
        embed = discord.Embed(title="Urban Dictionary", colour=colours.urban_dictionary_green())

        embed.add_field(name="Term", value=self.word, inline=True)
        embed.add_field(name="Author", value=self.author, inline=True)
        embed.add_field(name="Definition", value=self.definition, inline=False)
        embed.add_field(name="Example", value=self.example or "\u200B", inline=False)
        embed.add_field(
            name="Rating", value=f"{self.ratio}% ({self.thumbs_up}/{self.thumbs_up + self.thumbs_down})", inline=True
        )
        embed.add_field(name="Link", value=f"[Urban Dictionary]({self.permalink})", inline=True)

        return embed

    @staticmethod
    def no_result_found_embed() -> discord.Embed:
        """Embed shown when no definitions could be found"""
        embed = discord.Embed(title="Urban Dictionary", colour=colours.error_red())

        embed.description = "No definitions could be found."

        return embed
