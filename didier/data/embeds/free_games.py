import html
from typing import Optional

import discord
from aiohttp import ClientSession
from overrides import overrides
from pydantic import field_validator

from didier.data.embeds.base import EmbedPydantic
from didier.data.scrapers.common import GameStorePage
from didier.data.scrapers.steam import get_steam_webpage_info
from didier.utils.discord import colours
from didier.utils.discord.constants import Limits
from didier.utils.types.string import abbreviate

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
    title: str

    name: Optional[str] = None
    store: Optional[str] = None

    store_page: Optional[GameStorePage] = None

    @field_validator("title")
    def _clean_title(cls, value: str) -> str:
        return html.unescape(value)

    async def update(self, http_session: ClientSession):
        """Scrape the store page to fetch some information"""
        self.name, self.store = self.title.split(SEPARATOR)

        store = (self.store or "").lower()

        if "steam" in store:
            self.store_page = await get_steam_webpage_info(http_session, self.link)
        elif "epic" in store:
            self.link = "https://store.epicgames.com/free-games"

        if self.store_page is not None and self.store_page.url is not None:
            self.link = self.store_page.url

    @overrides
    def to_embed(self, **kwargs) -> discord.Embed:
        embed = discord.Embed()
        embed.set_author(name=self.store)

        store_image, store_colour = _get_store_info(self.store or "")
        if store_image is not None:
            embed.set_thumbnail(url=store_image)

        # Populate with scraped info
        if self.store_page is not None:
            embed.title = self.store_page.title
            embed.set_image(url=self.store_page.image)
            embed.description = abbreviate(self.store_page.description, Limits.EMBED_DESCRIPTION_LENGTH)

            if self.store_page.original_price is not None and self.store_page.discounted_price is not None:
                if self.store_page.discount_percentage is not None:
                    discount_pct_str = f" ({self.store_page.discount_percentage})"
                else:
                    discount_pct_str = ""

                embed.add_field(
                    name="Price",
                    value=f"~~{self.store_page.original_price}~~ **{self.store_page.discounted_price}** "
                    f"{discount_pct_str}",
                    inline=False,
                )

            embed.add_field(name="Open in browser", value=f"[{self.link}]({self.link})")

            if self.store_page.xdg_open_url is not None:
                embed.add_field(
                    name="Open in app", value=f"[{self.store_page.xdg_open_url}]({self.store_page.xdg_open_url})"
                )
        else:
            embed.title = self.name
            embed.add_field(name="Open in browser", value=f"[{self.link}]({self.link})")

        embed.url = self.link

        embed.colour = store_colour

        return embed
