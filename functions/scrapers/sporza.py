from bs4 import BeautifulSoup
import re
from requests import get


def getMatchweek():
    """
    Parses the current JPL matchweek out of Sporza's site
    """
    resp = get("https://sporza.be/nl/categorie/voetbal/jupiler-pro-league/")

    if resp.status_code != 200:
        return None

    bs = BeautifulSoup(resp.text, "html.parser")
    matchdays = bs.find_all("section", attrs={"class": "sc-matchdays"})

    if len(matchdays) == 0:
        return None

    # Table header
    header = matchdays[0]

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

    # Something went wrong
    if page_html.status_code != 200:
        return None

    bs_parsed = BeautifulSoup(page_html.text, "html.parser")
    rows = bs_parsed.find(summary="algemeen klassement").find_all("tr")[1:]
    return rows
