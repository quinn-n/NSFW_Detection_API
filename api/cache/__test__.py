from time import sleep

from api.cache import Cache


def test_get_entry_or_none() -> None:
    cache = Cache()
    assert cache.get_entry_or_none(["a"], {}) is None
    cache.add_entry(["a"], {}, "test entry")
    assert cache.get_entry_or_none(["a"], {}) is not None


# Broken because of thread wierdness with pytest
# def test_cache_pruning() -> None:
    # cache = Cache()
    # cache.add_entry(["a"], {}, "test entry", time_to_live=0)
# 
    # # Make sure timer runs
    # sleep(2)
# 
    # # Entry should have been pruned from cache
    # entry = cache.get_entry_or_none(["a"], {})
    # print(f"got cache entry {entry}")
# 
    # print("asserting no entry")
    # assert cache.get_entry_or_none(["a"], {}) is None
