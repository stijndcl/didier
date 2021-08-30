from typing import Optional, List

from bs4 import BeautifulSoup
from dataclasses import dataclass
from requests import get
from urllib.parse import urlencode


@dataclass
class SearchResult:
    status_code: int
    results: List[str]


def google_search(query) -> SearchResult:
    """
    Function to get Google search results
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    }

    query = urlencode({"q": query})

    # Get 20 results in case some of them are None
    resp = get("https://www.google.com/search?{}&num=20&hl=en".format(query), headers=headers)

    if resp.status_code != 200:
        return SearchResult(resp.status_code, [])

    bs = BeautifulSoup(resp.text, "html.parser")

    def getContent(element):
        """
        Function to find links & titles in the HTML of a <div> element
        """
        link = element.find("a", href=True)
        title = element.find("h3")

        if link is None or not link["href"].startswith(("http://", "https://",)) or title is None:
            return None

        return link["href"], title.text

    divs = bs.find_all("div", attrs={"class": "g"})

    results = list(getContent(d) for d in divs)

    # Filter out Nones
    results = list(filter(lambda x: x is not None, results))

    # Map to urls
    links = []
    for (link, title) in results:
        links.append(f"[{title}]({link})")

    return SearchResult(200, links[:10])
