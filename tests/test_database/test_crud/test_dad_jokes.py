from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import dad_jokes as crud
from database.models import DadJoke


async def test_add_dad_joke(database_session: AsyncSession):
    """Test creating a new joke"""
    statement = select(DadJoke)
    result = (await database_session.execute(statement)).scalars().all()
    assert len(result) == 0

    await crud.add_dad_joke(database_session, "joke")
    result = (await database_session.execute(statement)).scalars().all()
    assert len(result) == 1
