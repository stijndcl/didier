import pytest

from database.mongo_types import MongoDatabase


@pytest.mark.mongo
async def test_get_stats_non_existent(mongodb: MongoDatabase, test_user_id: int):
    """Test getting a user's stats when the db is empty"""
