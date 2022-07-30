from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.exceptions.not_found import NoResultFoundException
from database.schemas.relational import DadJoke

__all__ = ["add_dad_joke", "get_random_dad_joke"]


async def add_dad_joke(session: AsyncSession, joke: str) -> DadJoke:
    """Add a new dad joke to the database"""
    dad_joke = DadJoke(joke=joke)
    session.add(dad_joke)
    await session.commit()

    return dad_joke


async def get_random_dad_joke(session: AsyncSession) -> DadJoke:  # pragma: no cover # randomness is untestable
    """Return a random database entry"""
    statement = select(DadJoke).order_by(func.random())
    row = (await session.execute(statement)).first()
    if row is None:
        raise NoResultFoundException

    return row[0]
