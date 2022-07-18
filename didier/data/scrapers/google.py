import http
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import unquote_plus, urlencode

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from bs4.element import Tag

__all__ = ["google_search", "SearchData"]


@dataclass
class SearchData:
    """Dataclass to store some data about a search query"""

    query: str
    status_code: int
    results: list[str] = field(default_factory=list)
    result_stats: str = ""

    def __post_init__(self):
        self.query = unquote_plus(self.query)


def get_result_stats(bs: BeautifulSoup) -> Optional[str]:
    """Parse the result stats

    Example result: "About 16.570.000 results (0,84 seconds)"
    """
    stats = bs.find("div", id="result-stats").text
    return stats and stats.removesuffix("\xa0")


def parse_result(element: Tag) -> Optional[str]:
    """Parse 1 wrapper into a link"""
    a_tag = element.find("a", href=True)
    url = a_tag["href"]
    title = a_tag.find("h3")

    if (
        url is None
        or not url.startswith(
            (
                "http://",
                "https://",
            )
        )
        or title is None
    ):
        return None

    text = unquote_plus(title.text)
    return f"[{text}]({url})"


def get_search_results(bs: BeautifulSoup) -> list[str]:
    """Parse the search results"""
    result_wrappers = bs.find_all("div", class_="g")
    results = filter(lambda x: x is not None, map(parse_result, result_wrappers))

    # Remove duplicates
    # (sets don't preserve the order!)
    return list(dict.fromkeys(results))


async def google_search(http_client: ClientSession, query: str):
    """Get the first 10 Google search results"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
    }

    query = urlencode({"q": query})

    # Request 20 results in case of duplicates, bad matches, ...
    async with http_client.get(f"https://www.google.com/search?{query}&num=20&hl=en", headers=headers) as response:
        # Something went wrong
        if response.status != http.HTTPStatus.OK:
            return SearchData(query, response.status)

        bs = BeautifulSoup(await response.text(), "html.parser")
        result_stats = get_result_stats(bs)
        results = get_search_results(bs)

        return SearchData(query, 200, results[:10], result_stats)
