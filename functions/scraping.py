import re

from requests import get
from urllib.parse import urlencode
from bs4 import BeautifulSoup

# TODO add Football requests in here as well


def google_search(query):
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
        return None, resp.status_code

    bs = BeautifulSoup(resp.text, "html.parser")

    def getContent(element):
        """
        Function to find links & titles in the HTML of a <div> element
        """
        link = element.find("a", href=True)
        title = element.find("h3")

        if link is None or title is None:
            return None

        sp = title.find("span")

        if sp is None:
            return None

        return link["href"], sp.text

    divs = bs.find_all("div", attrs={"class": "g"})

    return list(getContent(d) for d in divs), 200


def getMatchweek():
    """
    Parses the current JPL matchweek out of Sporza's site
    """
    resp = get("https://sporza.be/nl/categorie/voetbal/jupiler-pro-league/")

    if resp.status_code != 200:
        return None

    bs = BeautifulSoup(resp.text, "html.parser")
    matchdays = bs.find_all("section", attrs={"class": "sc-matchdays"})

    if len(matchdays) < 2:
        return None

    # Table header
    header = matchdays[1]

    # Regex to find current matchday
    r = re.compile(r"speeldag\s*\d+", flags=re.I)

    match = r.search(str(header))

    # Something went wrong, just ignore
    if match is None:
        return None

    # "Speeldag DD" -> split on space & take second
    return match[0].split(" ")[1]


def getJPLMatches(week: int):
    """
    JPL matches for a given matchweek
    """
    current_day = get("https://api.sporza.be/web/soccer/matchdays/161733/{}".format(week))

    # Something went wrong
    if current_day.status_code != 200:
        return None

    return current_day.json()["groupedMatches"][0]["matches"]


def getJPLTable():
    """
    JPL table
    """
    page_html = get("https://sporza.be/nl/categorie/voetbal/jupiler-pro-league/")

    if page_html.status_code != 200:
        return None

    bs_parsed = BeautifulSoup(page_html.text, "html.parser")
    rows = bs_parsed.find(summary="algemeen klassement").find_all("tr")[1:]
    return rows
