from datetime import datetime, timedelta
from discord import Embed, Colour
from functions.timeFormatters import intToWeekday
import pytz
import re


class UforaNotification:
    def __init__(self, content: dict, course):
        self._content: dict = content
        self._course = course
        self._notif_id, self._course_id = self._find_ids(self._content["id"])
        self._view_url = self._create_url()
        self._title = self._clean_content(self._content["title"])
        self._description = self._get_description()
        self._published = self._get_published()

    def to_embed(self):
        embed = Embed(colour=Colour.from_rgb(30, 100, 200))

        embed.set_author(name=self._course)
        embed.title = self._title
        embed.url = self._view_url
        embed.description = self._description
        embed.set_footer(text=self._published)

        return embed

    def get_id(self):
        return int(self._notif_id) if self._notif_id is not None else self._content["id"]

    def _create_url(self):
        if self._notif_id is None or self._course_id is None:
            return self._content["link"]

        return "https://ufora.ugent.be/d2l/le/news/{0}/{1}/view?ou={0}".format(self._notif_id, self._course_id)

    def _find_ids(self, url: str):
        match = re.search(r"[0-9]+-[0-9]+$", url)

        if not match:
            return None, None

        spl = match[0].split("-")

        return spl[0], spl[1]

    def _get_description(self):
        desc = self._clean_content(self._content["summary"])

        if len(desc) > 500:
            return desc[:500]

        return desc

    def _clean_content(self, text: str):
        html_table = {
            # CHARACTERS:
            "&amp;": '&',
            "&quot;": '"',
            "apos;": "'",
            "&gt;": ">",
            "&lt;": "<",
            # MARKDOWN SUPPORT:
            "<b>": "**",
            "</b>": "**",
            "<strong>": "**",
            "</strong>": "**",
            "<i>": "*",
            "</i>": "*",
            "<em>": "*",
            "</em>": "*",
            "<del>": "~~",
            "</del>": "~~",
            "<ins>": "__",
            "</ins>": "__",
            # Represent paragraphs with newlines
            "</p>": "\n"
        }

        # Unescape HTML
        for key, value in html_table.items():
            text = text.replace(key, value)

        # Remove HTML tags
        return re.sub(r"<[^>]*>", "", text)

    def _get_published(self):
        time_string = "%a, %d %b %Y %H:%M:%S %Z"
        dt = datetime.strptime(self._content["published"], time_string)\
            .astimezone(pytz.timezone("Europe/Brussels"))

        # Apply timezone offset
        dt = dt + timedelta(hours=dt.utcoffset().seconds//3600)

        return "{} {}/{}/{} om {}:{}:{}".format(
            intToWeekday(dt.weekday()),
            dt.day, dt.month, dt.year,
            dt.hour, dt.minute, dt.second
        )
