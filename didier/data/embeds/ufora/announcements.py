import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

import discord
from markdownify import markdownify as md

from database.schemas import UforaCourse
from didier.data.embeds.base import EmbedBaseModel
from didier.utils.discord.colours import ghent_university_blue
from didier.utils.types.datetime import LOCAL_TIMEZONE, int_to_weekday
from didier.utils.types.string import leading

__all__ = [
    "UforaNotification",
]


@dataclass
class UforaNotification(EmbedBaseModel):
    """A single notification from Ufora"""

    content: dict
    course: UforaCourse
    notification_id: Optional[int] = None
    course_id: Optional[int] = None

    _view_url: str = field(init=False)
    _title: str = field(init=False)
    _description: str = field(init=False)
    published_dt: datetime = field(init=False)
    _published: str = field(init=False)

    def __post_init__(self):
        self._view_url = self._create_url()
        self._title = self._clean_content(self.content["title"])
        self._description = self._get_description()
        self.published_dt = self._published_datetime()
        self._published = self._get_published()

    def to_embed(self, **kwargs) -> discord.Embed:
        """Turn the notification into an embed"""
        embed = discord.Embed(title=self._title, colour=ghent_university_blue())

        embed.set_author(name=self.course.name)
        embed.title = self._title
        embed.url = self._view_url
        embed.description = self._description
        embed.set_footer(text=self._published)

        return embed

    def get_id(self) -> int:
        """Parse the id out of the notification"""
        return int(self.notification_id) if self.notification_id is not None else self.content["id"]

    def _create_url(self):
        if self.notification_id is None or self.course_id is None:
            return self.content["link"]

        return f"https://ufora.ugent.be/d2l/le/news/{self.course_id}/{self.notification_id}/view?ou={self.course_id}"

    def _get_description(self):
        desc = self._clean_content(self.content["summary"])

        if len(desc) > 4096:
            return desc[:4093] + "..."

        return desc

    def _clean_content(self, text: str):
        # Escape *-characters because they mess up the layout
        # and non-breaking-spaces
        text = text.replace("*", "\\*").replace("\xa0", " ")
        text = md(text)

        # Squash consecutive newlines and ignore spaces inbetween
        subbed = re.sub(r"\n+\s?\n+", "\n\n", text)

        return subbed

    def _published_datetime(self) -> datetime:
        """Get a datetime instance of the publication date"""
        # Datetime is unable to parse the timezone because it's useless
        # We will hereby cut it out and pray the timezone will always be UTC+0
        published = self.content["published"].rsplit(" ", 1)[0]
        time_string = "%a, %d %b %Y %H:%M:%S"
        dt = datetime.strptime(published, time_string).replace(tzinfo=ZoneInfo("GMT")).astimezone(LOCAL_TIMEZONE)
        return dt

    def _get_published(self) -> str:
        """Get a formatted string that represents when this announcement was published"""
        return (
            f"{int_to_weekday(self.published_dt.weekday())} "
            f"{leading('0', str(self.published_dt.day))}"
            "/"
            f"{leading('0', str(self.published_dt.month))}"
            "/"
            f"{self.published_dt.year} "
            f"{leading('0', str(self.published_dt.hour))}"
            ":"
            f"{leading('0', str(self.published_dt.minute))}"
            ":"
            f"{leading('0', str(self.published_dt.second))}"
        )
