from typing import Optional

from attr import dataclass, field
from datetime import datetime
from enum import Enum
from functions.timeFormatters import fromString
from functions.scrapers.sporza import getJPLMatches, getJPLTable
from functions.stringFormatters import leadingZero
import re
from requests import get
import tabulate


class Status(Enum):
    AfterToday = "--:--"
    NotStarted = "--:--"
    Postponed = "--:--"
    Over = "Einde"
    HalfTime = "Rust"


@dataclass
class Match:
    """
    Class representing a football match between two teams
    """
    matchDict: dict
    home: str = field(init=False)
    homeScore: int = 0
    away: str = field(init=False)
    awayScore: int = 0
    start: Optional[datetime] = field(init=False)
    date: str = field(init=False)
    weekDay: str = field(init=False)
    status: Status = field(init=False)

    def __attrs_post_init__(self):
        """
        Parse class attributes out of a dictionary returned from an API request
        """
        # The API isn't public, so every single game state is differently formatted
        self.status = self._getStatus(self.matchDict[Navigation.Status.value])
        self.home = self.matchDict[Navigation.HomeTeam.value][Navigation.Name.value]
        self.away = self.matchDict[Navigation.AwayTeam.value][Navigation.Name.value]

        if self._hasStarted():
            self.homeScore = self.matchDict[Navigation.HomeScore.value]
            self.awayScore = self.matchDict[Navigation.AwayScore.value]

        if "startDateTime" in self.matchDict:
            self.start = fromString(self.matchDict["startDateTime"], formatString="%Y-%m-%dT%H:%M:%S.%f%z")
        else:
            self.start = None

        self.date = self.start.strftime("%d/%m") if self.start is not None else "Uitgesteld"
        self.weekDay = self._getWeekday() if self.start is not None else "??"

    def _getStatus(self, status: str):
        """
        Gets the string representation for the status of this match
        """
        # LiveTime only exists if the status is live
        # Avoids KeyErrors
        if status.lower() == "live":
            # Half time
            if Navigation.LiveMatchPhase.value in self.matchDict and \
                    self.matchDict[Navigation.LiveMatchPhase.value] == Navigation.HalfTime.value:
                return Status.HalfTime.value

            # Current time
            return self.matchDict[Navigation.LiveTime.value]

        # If no special status, pull it out of this dict
        statusses: dict = {
            "after_today": Status.AfterToday.value,
            "not_started": Status.NotStarted.value,
            "postponed": Status.Postponed.value,
            "end": Status.Over.value
        }

        return statusses[status.lower()]

    def _getWeekday(self):
        """
        Gets the day of the week this match is played on
        """
        day = self.start.weekday()
        days = ["Ma", "Di", "Wo", "Do", "Vr", "Za", "Zo"]
        return days[day]

    def getInfo(self):
        """
        Returns a list of all the info of this class in order to create a table
        """
        return [self.weekDay, self.date, self.home, self._getScore(), self.away, self.status]

    def _getScore(self):
        """
        Returns a string representing the scoreboard
        """
        if self.start is None:
            return "??"

        # No score to show yet, show time when the match starts
        if not self._hasStarted():
            return "{}:{}".format(leadingZero(str(self.start.hour)), leadingZero(str(self.start.minute)))

        return "{} - {}".format(self.homeScore, self.awayScore)

    def _hasStarted(self):
        return self.status not in [Status.AfterToday.value, Status.NotStarted.value, Status.Postponed.value]


class Navigation(Enum):
    """
    Enum to navigate through the matchdict,
    seeing as the API is private the keys of the dict could change every now and then
    so this makes sure a key only has to be changed once.
    """
    AwayTeam = "awayTeam"
    HomeTeam = "homeTeam"
    AwayScore = "awayScore"
    HomeScore = "homeScore"
    LiveTime = "liveTime"
    LiveMatchPhase = "liveMatchPhase"
    HalfTime = "HALF_TIME"
    Status = "status"
    Name = "name"


def getMatches(matchweek: int):
    """
    Function that constructs the list of matches for a given matchweek
    """
    current_day = getJPLMatches(matchweek)

    # API request failed
    if current_day is None:
        return "Er ging iets fout. Probeer het later opnieuw."

    matches = list(map(Match, current_day))
    matches = list(map(lambda x: x.getInfo(), matches))

    header = "Jupiler Pro League - Speeldag {}".format(matchweek)
    table = tabulate.tabulate(matches, headers=["Dag", "Datum", "Thuis", "Stand", "Uit", "Tijd"])

    return "```{}\n\n{}```".format(header, table)


def getTable():
    """
    Function that constructs the current table of the JPL
    """
    rows = getJPLTable()

    if rows is None:
        return "Er ging iets fout. Probeer het later opnieuw."

    # Format every row to work for Tabulate
    formatted = [_formatRow(row) for row in rows]

    header = "Jupiler Pro League Klassement"
    table = tabulate.tabulate(formatted, headers=["#", "Ploeg", "Punten", "M", "M+", "M-", "M=", "D+", "D-", "D+/-"])

    return "```{}\n\n{}```".format(header, table)


def _formatRow(row):
    """
    Function that formats a row into a list for Tabulate to use
    """
    scoresArray = list([td.renderContents().decode("utf-8") for td in row.find_all("td")])[:9]

    # Insert the team name into the list
    scoresArray.insert(1, row.find_all("a")[0].renderContents().decode("utf-8").split("<!--")[0])

    return scoresArray


def get_jpl_code() -> int:
    editions = get("https://api.sporza.be/web/soccer/competitions/48").json()["editions"]
    newest_edition = editions[0]["_links"]["self"]["href"]
    phase = get(newest_edition).json()["phases"][0]
    phase_url = phase["_links"]["self"]["href"]
    r = re.compile(r"\d+$")
    match = re.search(r, phase_url)

    return int(match[0])
