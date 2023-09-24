from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.schemas import MemeTemplate

__all__ = ["add_meme", "get_all_memes", "get_meme_by_name"]


async def add_meme(session: AsyncSession, name: str, template_id: int, field_count: int) -> Optional[MemeTemplate]:
    """Add a new meme into the database"""
    try:
        meme = MemeTemplate(name=name, template_id=template_id, field_count=field_count)
        session.add(meme)
        await session.commit()
        return meme
    except IntegrityError:
        return None


async def get_all_memes(session: AsyncSession) -> list[MemeTemplate]:
    """Get a list of all memes"""
    statement = select(MemeTemplate)
    return list((await session.execute(statement)).scalars().all())


async def get_meme_by_name(session: AsyncSession, query: str) -> Optional[MemeTemplate]:
    """Try to find a meme by its name

    Returns the first match found by PSQL
    """
    statement = select(MemeTemplate).where(MemeTemplate.name.ilike(f"%{query.lower()}%"))
    return (await session.execute(statement)).scalar()
