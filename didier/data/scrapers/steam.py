import re
from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional, cast

from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag

from didier.data.scrapers.common import GameStorePage, parse_open_graph_tags

__all__ = ["get_steam_webpage_info"]


@dataclass
class _PriceInfo:
    # These are strings because they aren't used as floats,
    # and this avoids possible rounding errors
    original_price: str
    discounted_price: str
    discount_percentage: Optional[str]

    def __post_init__(self):
        """Fix the price formats"""
        self.original_price = "€" + self.original_price.replace(",--", ",00").removesuffix("€")
        self.discounted_price = "€" + self.discounted_price.replace(",--", ",00").removesuffix("€")
        if self.discounted_price == "€0,00":
            self.discounted_price = "Free"


def _shorten_url(url: str) -> str:
    match = re.search(r"https://store.steampowered.com/app/(\d+)/", url)
    if match is None or not match.groups():
        return url

    return f"https://s.team/a/{match.groups()[0]}"


def _parse_xdg_open_url(url: str) -> Optional[str]:
    match = re.search(r"/app/(\d+)/", url)
    if match is None or not match.groups():
        return None

    return f"steam://store/{match.groups()[0]}"


def _get_steam_discounts(soup: BeautifulSoup) -> Optional[_PriceInfo]:
    discount_wrapper_tag = soup.find("div", class_="discount_block")
    if discount_wrapper_tag is None:
        return None

    discount_wrapper_tag = cast(Tag, discount_wrapper_tag)

    # Parsing the original (non-discounted) price
    original_price_tag = discount_wrapper_tag.find("div", class_="discount_original_price")
    if original_price_tag is None:
        return None

    original_price_tag = cast(Tag, original_price_tag)
    original_price = original_price_tag.text
    if original_price is None:
        return None

    # Parsing the discounted price
    discounted_price_tag = discount_wrapper_tag.find("div", class_="discount_final_price")
    if discounted_price_tag is None:
        return None

    discounted_price_tag = cast(Tag, discounted_price_tag)
    discounted_price = discounted_price_tag.text
    if discounted_price is None:
        return None

    percentage_tag = discount_wrapper_tag.find("div", class_="discount_pct")
    if percentage_tag is None:
        percentage = None
    else:
        percentage = percentage_tag.text

    return _PriceInfo(original_price=original_price, discounted_price=discounted_price, discount_percentage=percentage)


def _clean_title(title: str) -> str:
    match = re.search(r"Save [\d,]+% on (.*) on Steam", title)
    if match is None or not match.groups():
        return title

    return match.groups()[0]


async def get_steam_webpage_info(http_session: ClientSession, url: str) -> Optional[GameStorePage]:
    """Scrape a Steam page"""
    # If not currently on a Steam page, follow a redirect chain until you are
    if not url.startswith("https://store.steampowered.com/"):
        async with http_session.head(url, allow_redirects=True) as response:
            url = str(response.url)

    async with http_session.get(url) as response:
        if response.status != HTTPStatus.OK:
            return None

        page = await response.text()

    soup = BeautifulSoup(page, "html.parser")

    page_tags = parse_open_graph_tags(soup)
    if page_tags is None:
        return None

    if page_tags.url is None:
        page_tags.url = url

    page_tags.title = _clean_title(page_tags.title)
    page_tags.xdg_open_url = _parse_xdg_open_url(page_tags.url)
    page_tags.url = _shorten_url(page_tags.url)

    price_info = _get_steam_discounts(soup)

    if price_info is not None:
        page_tags.original_price = price_info.original_price
        page_tags.discounted_price = price_info.discounted_price
        page_tags.discount_percentage = price_info.discount_percentage

    return page_tags
