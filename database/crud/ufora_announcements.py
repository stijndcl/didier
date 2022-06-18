from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UforaCourse, UforaAnnouncement


async def get_courses_with_announcements(session: AsyncSession) -> list[UforaCourse]:
    """Get all courses where announcements are enabled"""
    query = select(UforaCourse).where(UforaCourse.log_announcements)
    return (await session.execute(query)).scalars().all()


async def create_new_announcement(session: AsyncSession, announcement_id: int, course: UforaCourse):
    """Add a new announcement to the database"""
    new_announcement = UforaAnnouncement(announcement_id=announcement_id, course=course)
    session.add(new_announcement)
    await session.commit()
