import re
from typing import Optional

import async_timeout
import feedparser
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from database.crud import ufora_announcements as crud
from didier.data.embeds.ufora.announcements import UforaNotification

__all__ = ["parse_ids", "fetch_ufora_announcements"]


def parse_ids(url: str) -> Optional[tuple[int, int]]:
    """Parse the notification & course id out of a notification url"""
    match = re.search(r"\d+-\d+$", url)

    if not match:
        return None

    spl = match[0].split("-")
    return int(spl[0]), int(spl[1])


async def fetch_ufora_announcements(
    http_session: ClientSession, database_session: AsyncSession
) -> list[UforaNotification]:
    """Fetch all new announcements"""
    notifications: list[UforaNotification] = []

    # No token provided, don't fetch announcements
    if settings.UFORA_RSS_TOKEN is None:
        return notifications

    courses = await crud.get_courses_with_announcements(database_session)

    for course in courses:
        course_announcement_ids = list(map(lambda announcement: announcement.announcement_id, course.announcements))

        course_url = (
            f"https://ufora.ugent.be/d2l/le/news/rss/{course.course_id}/course?token={settings.UFORA_RSS_TOKEN}"
        )

        # Get the updated feed
        with async_timeout.timeout(10):
            async with http_session.get(course_url) as response:
                feed = feedparser.parse(await response.text())

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
                await crud.create_new_announcement(database_session, notification_id, course, notification.published_dt)

    return notifications
