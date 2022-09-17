from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import DBSession
from database.schemas import UforaCourse

__all__ = ["main"]


async def main():
    """Example script: add a Ufora course"""
    session: AsyncSession
    async with DBSession() as session:
        modsim = UforaCourse(
            course_id=439235,
            code="C003786",
            name="Modelleren en Simuleren",
            year=3,
            compulsory=False,
            role_id=785577582561067028,
        )

        session.add_all([modsim])
        await session.commit()
