from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import DBSession
from database.schemas import UforaCourse, UforaCourseAlias

__all__ = ["main"]


async def main():
    """Add the Image Processing course"""
    session: AsyncSession
    async with DBSession() as session:
        image_proc = UforaCourse(
            code="E010310", name="Image Processing", year=6, compulsory=False, role_id=1155595071228498134
        )

        session.add(image_proc)
        await session.commit()

        image_proc_alias = UforaCourseAlias(course_id=image_proc.course_id, alias="Beeldverwerking")
        session.add(image_proc_alias)
        await session.commit()
