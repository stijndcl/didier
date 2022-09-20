from typing import Optional

import sqlalchemy.exc
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.exceptions import (
    DuplicateInsertException,
    Forbidden,
    NoResultFoundException,
)
from database.schemas import GitHubLink

__all__ = ["add_github_link", "delete_github_link_by_id", "get_github_links"]


async def add_github_link(session: AsyncSession, user_id: int, url: str) -> GitHubLink:
    """Add a new GitHub link into the database"""
    try:
        gh_link = GitHubLink(user_id=user_id, url=url)
        session.add(gh_link)
        await session.commit()
        await session.refresh(gh_link)
    except sqlalchemy.exc.IntegrityError:
        raise DuplicateInsertException

    return gh_link


async def delete_github_link_by_id(session: AsyncSession, user_id: int, link_id: int):
    """Remove an existing link from the database

    You can only remove links owned by you
    """
    select_statement = select(GitHubLink).where(GitHubLink.github_link_id == link_id)
    gh_link: Optional[GitHubLink] = (await session.execute(select_statement)).scalar_one_or_none()
    if gh_link is None:
        raise NoResultFoundException

    if gh_link.user_id != user_id:
        raise Forbidden

    delete_statement = delete(GitHubLink).where(GitHubLink.github_link_id == gh_link.github_link_id)
    await session.execute(delete_statement)
    await session.commit()


async def get_github_links(session: AsyncSession, user_id: int) -> list[GitHubLink]:
    """Get a user's GitHub links"""
    statement = select(GitHubLink).where(GitHubLink.user_id == user_id)
    return (await session.execute(statement)).scalars().all()
