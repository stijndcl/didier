from database.models import UforaCourse
from database.utils.caches import UforaCourseCache


async def test_ufora_course_cache_refresh_empty(postgres, ufora_course_with_alias: UforaCourse):
    """Test loading the data for the Ufora Course cache when it's empty"""
    cache = UforaCourseCache()
    await cache.refresh(postgres)

    assert len(cache.data) == 1
    assert cache.data == ["test"]
    assert cache.aliases == {"alias": "test"}


async def test_ufora_course_cache_refresh_not_empty(postgres, ufora_course_with_alias: UforaCourse):
    """Test loading the data for the Ufora Course cache when it's not empty anymore"""
    cache = UforaCourseCache()
    cache.data = ["Something"]
    cache.data_transformed = ["something"]

    await cache.refresh(postgres)

    assert len(cache.data) == 1
    assert cache.data == ["test"]
    assert cache.aliases == {"alias": "test"}
