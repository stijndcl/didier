from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import DBSession
from database.schemas import UforaCourse

__all__ = ["main"]


async def main():
    """Add debug Ufora courses"""
    session: AsyncSession
    async with DBSession() as session:
        modsim = UforaCourse(course_id=439235, code="C003786", name="Modelleren en Simuleren", year=3, compulsory=False)

        session.add_all([modsim])
        await session.commit()
