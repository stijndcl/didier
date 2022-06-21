import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import discord
import feedparser
import pytz
from markdownify import markdownify as md
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from database.crud import ufora_announcements as crud
from database.models import UforaCourse
from didier.utils.types.datetime import int_to_weekday
from didier.utils.types.string import leading


@dataclass
class UforaNotification:
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

    def to_embed(self) -> discord.Embed:
        """Turn the notification into an embed"""
        embed = discord.Embed(colour=discord.Colour.from_rgb(30, 100, 200))

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
        text = text.replace("*", "\\*")
        return md(text)

    def _published_datetime(self) -> datetime:
        """Get a datetime instance of the publication date"""
        # Datetime is unable to parse the timezone because it's useless
        # We will hereby cut it out and pray the timezone will always be UTC+0
        published = self.content["published"].rsplit(" ", 1)[0]
        time_string = "%a, %d %b %Y %H:%M:%S"
        dt = datetime.strptime(published, time_string).astimezone(pytz.timezone("Europe/Brussels"))

        # Apply timezone offset in a hacky way
        offset = dt.utcoffset()
        if offset is not None:
            dt += offset

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
            f"om {leading('0', str(self.published_dt.hour))}"
            ":"
            f"{leading('0', str(self.published_dt.minute))}"
            ":"
            f"{leading('0', str(self.published_dt.second))}"
        )


def parse_ids(url: str) -> Optional[tuple[int, int]]:
    """Parse the notification & course id out of a notification url"""
    match = re.search(r"\d+-\d+$", url)

    if not match:
        return None

    spl = match[0].split("-")
    return int(spl[0]), int(spl[1])


async def fetch_ufora_announcements(session: AsyncSession) -> list[UforaNotification]:
    """Fetch all new announcements"""
    notifications: list[UforaNotification] = []

    # No token provided, don't fetch announcements
    if settings.UFORA_RSS_TOKEN is None:
        return notifications

    courses = await crud.get_courses_with_announcements(session)

    for course in courses:
        course_announcement_ids = list(map(lambda announcement: announcement.announcement_id, course.announcements))

        course_url = (
            f"https://ufora.ugent.be/d2l/le/news/rss/{course.course_id}/course?token={settings.UFORA_RSS_TOKEN}"
        )

        # Get the updated feed
        feed = feedparser.parse(course_url)

        # Remove old notifications
        fresh_feed: list[dict] = []
        for entry in feed["entries"]:
            parsed = parse_ids(entry["id"])
            if parsed is None:
                continue

            if parsed[0] not in course_announcement_ids:
                fresh_feed.append(entry)

        if fresh_feed:
            for item in fresh_feed:
                # Parse id's out
                # Technically this can't happen but Mypy angry
                parsed = parse_ids(item["id"])

                if parsed is None:
                    continue

                # Create a new notification
                notification_id, course_id = parsed
                notification = UforaNotification(item, course, notification_id, course_id)
                notifications.append(notification)

                # Create new db entry
                await crud.create_new_announcement(session, notification_id, course, notification.published_dt)

    return notifications