from typing import Optional

import sqlalchemy.exc
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud.users import get_or_add_user
from database.exceptions import DuplicateInsertException, ForbiddenNameException
from database.schemas import Bookmark

__all__ = ["create_bookmark", "get_bookmarks", "get_bookmark_by_name"]


async def create_bookmark(session: AsyncSession, user_id: int, label: str, jump_url: str) -> Bookmark:
    """Create a new bookmark to a message"""
    # Don't allow bookmarks with names of subcommands
    if label.lower() in ["create", "ls", "list", "search"]:
        raise ForbiddenNameException

    await get_or_add_user(session, user_id)

    try:
        bookmark = Bookmark(label=label, jump_url=jump_url, user_id=user_id)
        session.add(bookmark)
        await session.commit()
        await session.refresh(bookmark)
    except sqlalchemy.exc.IntegrityError as e:
        raise DuplicateInsertException from e

    return bookmark


async def get_bookmarks(session: AsyncSession, user_id: int, *, query: Optional[str] = None) -> list[Bookmark]:
    """Get all a user's bookmarks"""
    statement = select(Bookmark).where(Bookmark.user_id == user_id)

    if query is not None:
        statement = statement.where(Bookmark.label.ilike(f"%{query.lower()}%"))

    return (await session.execute(statement)).scalars().all()


async def get_bookmark_by_name(session: AsyncSession, user_id: int, query: str) -> Optional[Bookmark]:
    """Try to find a bookmark by its name"""
    statement = select(Bookmark).where(Bookmark.user_id == user_id).where(func.lower(Bookmark.label) == query.lower())
    return (await session.execute(statement)).scalar_one_or_none()
