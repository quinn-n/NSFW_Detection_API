import asyncio
from threading import Timer
from typing import (
    Any,
    Callable,
    Optional,
    Hashable,
)
from functools import update_wrapper

from attr import attrs, attrib


Results = Any
_CacheEntries = dict[Hashable, Results]


@attrs(slots=True)
class Cache:
    entries = attrib(factory=lambda: {}, type=_CacheEntries)  # type: _CacheEntries

    def create_entry(
        self,
        key: Hashable,
        result: Any,
        time_to_live: Optional[int] = None,
    ) -> None:
        """Adds an entry to the `Cache`'s entry list
        If `time_to_live` is provided, deletes the entry after `time_to_live` seconds"""
        self.entries[key] = result

        if time_to_live is not None:
            self._set_timer(key, time_to_live)

    def get_entry_or_none(self, key: Hashable) -> Optional[Results]:
        """Returns a cache entry for given args and kwargs if one exists"""
        return self.entries.get(key, None)

    def remove_entry(self, key: Hashable) -> None:
        """Manually remove an entry from the cache"""
        self.entries.pop(key)

    def _set_timer(self, key: Hashable, time_to_live: int) -> None:
        """Creates a timer to delete an entry"""
        Timer(time_to_live, lambda: self.remove_entry(key)).start()


def async_cache(time_to_live: Optional[int] = None) -> Callable[[Callable], "Wrapper"]:
    """Adds caching support to an asynchrinous function"""

    def inner(fcn: Callable) -> "Wrapper":
        @attrs(kw_only=True)
        class Wrapper:
            cache = attrib(factory=lambda: Cache(), type=Cache)  # type: Cache
            running_cache = attrib(factory=lambda: Cache(), type=Cache)  # type: Cache

            async def __call__(self, *args, **kwargs):
                key = (args, tuple(kwargs.items()))
                cache_entry = self.cache.get_entry_or_none(key)
                if cache_entry is None:
                    running_entry = self.running_cache.get_entry_or_none(key)

                    # Cache of currently running items
                    if running_entry is not None:
                        return await running_entry
                    # New args, run function
                    else:

                        async def update_future_with_result() -> Results:
                            result = await fcn(*args, **kwargs)
                            future.set_result(result)
                            self.cache.create_entry(
                                key, result, time_to_live=time_to_live
                            )
                            return result

                        loop = asyncio.get_event_loop()
                        future = loop.create_future()

                        self.running_cache.create_entry(key, future)

                        await update_future_with_result()
                        result = await future
                        self.running_cache.remove_entry(key)
                        return result
                # Identical function call in cache, return cached result
                else:
                    return cache_entry

            @classmethod
            def build(cls) -> "Wrapper":
                return cls()

        wrapper = Wrapper.build()
        update_wrapper(wrapper, fcn)

        return wrapper

    return inner
