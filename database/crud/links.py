from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.exceptions import NoResultFoundException
from database.schemas import Link

__all__ = ["add_link", "edit_link", "get_all_links", "get_link_by_name"]


async def get_all_links(session: AsyncSession) -> list[Link]:
    """Get a list of all links"""
    statement = select(Link)
    return (await session.execute(statement)).scalars().all()


async def add_link(session: AsyncSession, name: str, url: str) -> Link:
    """Add a new link into the database"""
    if name.islower():
        name = name.capitalize()

    instance = Link(name=name, url=url)
    session.add(instance)
    await session.commit()

    return instance


async def get_link_by_name(session: AsyncSession, name: str) -> Optional[Link]:
    """Get a link by its name"""
    statement = select(Link).where(func.lower(Link.name) == name.lower())
    return (await session.execute(statement)).scalar_one_or_none()


async def edit_link(session: AsyncSession, name: str, new_url: str):
    """Edit an existing link"""
    link: Optional[Link] = await get_link_by_name(session, name)

    if link is None:
        raise NoResultFoundException

    link.url = new_url
    session.add(link)
    await session.commit()
