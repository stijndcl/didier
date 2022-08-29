import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.schemas import UforaAnnouncement, UforaCourse

__all__ = ["create_new_announcement", "get_courses_with_announcements", "remove_old_announcements"]


async def get_courses_with_announcements(session: AsyncSession) -> list[UforaCourse]:
    """Get all courses where announcements are enabled"""
    statement = select(UforaCourse).where(UforaCourse.log_announcements)
    return (await session.execute(statement)).scalars().all()


async def create_new_announcement(
    session: AsyncSession, announcement_id: int, course: UforaCourse, publication_date: datetime.datetime
) -> UforaAnnouncement:
    """Add a new announcement to the database"""
    new_announcement = UforaAnnouncement(
        announcement_id=announcement_id, course=course, publication_date=publication_date
    )
    session.add(new_announcement)
    await session.commit()
    return new_announcement


async def remove_old_announcements(session: AsyncSession):
    """Delete all announcements that are > 8 days old

    The RSS feed only goes back 7 days, so all of these old announcements never have to
    be checked again when checking if an announcement is fresh or not.
    """
    limit = datetime.datetime.utcnow() - datetime.timedelta(days=8)
    statement = delete(UforaAnnouncement).where(UforaAnnouncement.publication_date < limit)
    await session.execute(statement)
    await session.commit()
