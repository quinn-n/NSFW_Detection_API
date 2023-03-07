from threading import Timer
from typing import Any, Callable, Optional
from functools import update_wrapper

from attr import attrs, attrib


@attrs(frozen=True, kw_only=True, auto_attribs=True, slots=True)
class CacheEntry:
    args: list[Any]
    kwargs: dict[str, Any]
    result: Any

    @classmethod
    def create_entry(
        cls, args: list[Any], kwargs: dict[str, Any], result: Any
    ) -> "CacheEntry":
        """Creates a new `CacheEntry`"""
        return cls(
            args=args,
            kwargs=kwargs,
            result=result,
        )


@attrs(slots=True)
class Cache:
    entries = attrib(default=[], type=list[CacheEntry])

    def add_entry(
        self,
        args: list[Any],
        kwargs: dict[str, Any],
        result: Any,
        time_to_live: Optional[int] = None,
    ) -> None:
        """Adds an entry to the `Cache`'s entry list
        If `time_to_live` is provided, deletes the entry after `time_to_live` seconds"""
        entry = CacheEntry.create_entry(args, kwargs, result)
        self.entries.append(entry)

        if time_to_live is not None:

            def remove_entry():
                self.entries.remove(entry)

            timer = Timer(time_to_live, remove_entry)
            timer.start()

    def get_entry_or_none(
        self, args: list[Any], kwargs: dict[str, Any]
    ) -> Optional[CacheEntry]:
        """Returns a cache entry for given args and kwargs if one exists"""
        for entry in self.entries:
            if entry.args == args and entry.kwargs == kwargs:
                return entry
        return None


def async_cache(time_to_live: Optional[int] = None) -> Callable[[Callable], "Wrapper"]:
    """Adds caching support to an asynchrinous function"""

    def inner(fcn: Callable) -> "Wrapper":
        @attrs(auto_attribs=True, kw_only=True)
        class Wrapper:
            cache: Cache

            async def __call__(self, *args, **kwargs):
                cache_entry = self.cache.get_entry_or_none(args, kwargs)
                if cache_entry is None:
                    result = await fcn(*args, **kwargs)
                    self.cache.add_entry(
                        args, kwargs, result, time_to_live=time_to_live
                    )
                    return result
                else:
                    return cache_entry.result

            @classmethod
            def build(cls) -> "Wrapper":
                return cls(cache=Cache())

        wrapper = Wrapper.build()
        update_wrapper(wrapper, fcn)

        return wrapper

    return inner
