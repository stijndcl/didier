from dataclasses import dataclass
from typing import Optional, cast

from bs4 import BeautifulSoup, Tag

__all__ = ["GameStorePage", "parse_open_graph_tags"]


@dataclass
class GameStorePage:
    """Dataclass for information on a game's store page"""

    description: str
    image: str
    title: str
    xdg_open_url: Optional[str] = None
    url: Optional[str] = None
    discount_expiry: Optional[int] = None  # TODO
    discounted_price: Optional[str] = None
    original_price: Optional[str] = None
    discount_percentage: Optional[str] = None


def parse_open_graph_tags(soup: BeautifulSoup) -> Optional[GameStorePage]:
    """Parse Open Graph Protocol tags out of a webpage

    If any of the required tags were not found, this returns None
    """
    head = soup.find("head")

    if head is None:
        return None

    head = cast(Tag, head)

    title_tag = head.find("meta", property="og:title")
    if title_tag is None:
        return None

    description_tag = head.find("meta", property="og:description")
    if description_tag is None:
        return None

    image_tag = head.find("meta", property="og:image")
    if image_tag is None:
        return None

    url_tag = head.find("meta", property="og:url")
    if url_tag is None:
        url = None
    else:
        url = str(url_tag["content"])  # type: ignore

    description = str(description_tag["content"])  # type: ignore
    image = str(image_tag["content"])  # type: ignore
    title = str(title_tag["content"])  # type: ignore

    return GameStorePage(title=title, description=description, url=url, image=image)
