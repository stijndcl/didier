from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.exceptions.not_found import NoResultFoundException
from database.models import DadJoke

__all__ = ["add_dad_joke", "edit_dad_joke", "get_random_dad_joke"]


async def add_dad_joke(session: AsyncSession, joke: str) -> DadJoke:
    """Add a new dad joke to the database"""
    dad_joke = DadJoke(joke=joke)
    session.add(dad_joke)
    await session.commit()

    return dad_joke


async def edit_dad_joke(session: AsyncSession, joke_id: int, new_joke: str) -> DadJoke:
    """Edit an existing dad joke"""
    statement = select(DadJoke).where(DadJoke.dad_joke_id == joke_id)
    dad_joke: Optional[DadJoke] = (await session.execute(statement)).scalar_one_or_none()
    if dad_joke is None:
        raise NoResultFoundException

    dad_joke.joke = new_joke
    session.add(dad_joke)
    await session.commit()

    return dad_joke


async def get_random_dad_joke(session: AsyncSession) -> DadJoke:
    """Return a random database entry"""
    statement = select(DadJoke).order_by(func.random())
    row = (await session.execute(statement)).first()
    if row is None:
        raise NoResultFoundException

    return row[0]
