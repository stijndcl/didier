import html
from typing import Optional

import discord
from overrides import overrides
from pydantic import validator

from didier.data.embeds.base import EmbedPydantic
from didier.utils.discord import colours

__all__ = ["SEPARATOR", "FreeGameEmbed"]

SEPARATOR = " • Free • "


def _get_store_info(store: str) -> tuple[Optional[str], discord.Colour]:
    """Get the image url for a given store"""
    store = store.lower()

    if "epic" in store:
        return (
            "https://cdn2.unrealengine.com/"
            "Unreal+Engine%2Feg-logo-filled-1255x1272-0eb9d144a0f981d1cbaaa1eb957de7a3207b31bb.png",
            colours.epic_games_white(),
        )

    if "gog" in store:
        return (
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/GOG.com_logo.svg/1679px-GOG.com_logo.svg.png",
            colours.gog_purple(),
        )

    if "steam" in store:
        return (
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/"
            "Steam_icon_logo.svg/2048px-Steam_icon_logo.svg.png",
            colours.steam_blue(),
        )

    return None, discord.Colour.random()


class FreeGameEmbed(EmbedPydantic):
    """Embed for free games"""

    dc_identifier: int
    link: str
    summary: str = ""
    title: str

    @validator("title")
    def _clean_title(cls, value: str) -> str:
        return html.unescape(value)

    @overrides
    def to_embed(self, **kwargs) -> discord.Embed:
        name, store = self.title.split(SEPARATOR)
        embed = discord.Embed(title=name, url=self.link, description=self.summary or None)
        embed.set_author(name=store)

        image, colour = _get_store_info(store)
        if image is not None:
            embed.set_thumbnail(url=image)

        embed.colour = colour

        return embed
