from datetime import datetime
from discord import Embed, Colour
from functions.stringFormatters import leading_zero as lz
from functions.timeFormatters import intToWeekday
from markdownify import markdownify as md
import pytz


class UforaNotification:
    def __init__(self, content: dict, course, notif_id, course_id):
        self._content: dict = content
        self._course = course
        self._notif_id = notif_id
        self._course_id = course_id
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

        return "https://ufora.ugent.be/d2l/le/news/{0}/{1}/view?ou={0}".format(self._course_id, self._notif_id)

    def _get_description(self):
        desc = self._clean_content(self._content["summary"])

        if len(desc) > 4096:
            return desc[:4093] + "..."

        return desc

    def _clean_content(self, text: str):
        return md(text)

    def _get_published(self):
        # Datetime is unable to parse the timezone because it's useless
        # We will hereby cut it out and pray the timezone will always be UTC+0
        published = self._content["published"].rsplit(" ", 1)[0]
        time_string = "%a, %d %b %Y %H:%M:%S"
        dt = datetime.strptime(published, time_string)\
            .astimezone(pytz.timezone("Europe/Brussels"))

        # Apply timezone offset in a hacky way
        dt = dt + dt.utcoffset()

        return "{} {}/{}/{} om {}:{}:{}".format(
            intToWeekday(dt.weekday()),
            lz(dt.day), lz(dt.month), lz(dt.year),
            lz(dt.hour), lz(dt.minute), lz(dt.second)
        )
