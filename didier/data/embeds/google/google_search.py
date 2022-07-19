from http import HTTPStatus

import discord
from overrides import overrides

from didier.data.embeds.base import EmbedBaseModel
from didier.data.scrapers.google import SearchData

__all__ = ["GoogleSearch"]


class GoogleSearch(EmbedBaseModel):
    """Embed to display Google search results"""

    data: SearchData

    def __init__(self, data: SearchData):
        self.data = data

    def _error_embed(self) -> discord.Embed:
        """Custom embed for unsuccessful requests"""
        embed = discord.Embed(colour=discord.Colour.red())
        embed.set_author(name="Google Search")

        # Empty embed
        if not self.data.results:
            embed.description = "Geen resultaten gevonden"
            return embed

        # Error embed
        embed.description = f"Status {self.data.status_code}"

        return embed

    @overrides
    def to_embed(self) -> discord.Embed:
        if not self.data.results or self.data.status_code != HTTPStatus.OK:
            return self._error_embed()

        embed = discord.Embed(colour=discord.Colour.blue())
        embed.set_author(name="Google Search")
        embed.set_footer(text=self.data.result_stats or None)

        # Add all results into the description
        results = []
        for index, url in enumerate(self.data.results):
            results.append(f"{index + 1}: {url}")

        embed.description = "\n".join(results)
        return embed