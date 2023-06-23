from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import DBSession
from database.schemas import UforaCourse

__all__ = ["main"]


async def main():
    """Add the Bachelor and Master infosites, and log announcements"""
    session: AsyncSession
    async with DBSession() as session:
        bsc = UforaCourse(
            course_id=77068,
            code="INFOSITE-BSC",
            name="INFOSITE Bachelor of Science in de Informatica",
            year=6,
            compulsory=True,
            role_id=None,
            log_announcements=True,
        )

        msc = UforaCourse(
            course_id=77206,
            code="INFOSITE-MSC",
            name="INFOSITE Master of Science in de Informatica",
            year=6,
            compulsory=True,
            role_id=None,
            log_announcements=True,
        )

        session.add_all([bsc, msc])
        await session.commit()
