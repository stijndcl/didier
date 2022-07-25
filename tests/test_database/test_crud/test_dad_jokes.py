from sqlalchemy import select

from database.crud import dad_jokes as crud
from database.models import DadJoke


async def test_add_dad_joke(postgres):
    """Test creating a new joke"""
    statement = select(DadJoke)
    result = (await postgres.execute(statement)).scalars().all()
    assert len(result) == 0

    await crud.add_dad_joke(postgres, "joke")
    result = (await postgres.execute(statement)).scalars().all()
    assert len(result) == 1
