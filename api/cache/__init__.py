import asyncio
from threading import Timer
from typing import AsyncGenerator, Any, Callable, Optional, Union, Iterable, Awaitable
from functools import update_wrapper

import click
from attr import attrs, attrib


Args = list[Any]
KWArgs = tuple[str, Any]
Results = Any


@attrs(frozen=True, kw_only=True, auto_attribs=True, slots=True)
class CacheEntry:
    args: tuple
    kwargs: dict[str, Any]
    result: Any

    @classmethod
    def create_entry(
        cls, args: tuple, kwargs: dict[str, Any], result: Any
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

    def create_entry(
        self,
        args: tuple,
        kwargs: dict[str, Any],
        result: Any,
        time_to_live: Optional[int] = None,
    ) -> CacheEntry:
        """Adds an entry to the `Cache`'s entry list
        If `time_to_live` is provided, deletes the entry after `time_to_live` seconds"""
        entry = CacheEntry.create_entry(args, kwargs, result)
        self.entries.append(entry)

        if time_to_live is not None:
            self._set_timer(entry, time_to_live)

        return entry

    def add_entry(self, entry: CacheEntry, time_to_live: Optional[int] = None) -> None:
        """Manually add a `CacheEntry`"""
        self.entries.append(entry)
        if time_to_live is not None:
            self._set_timer(entry, time_to_live)

    def get_entry_or_none(
        self, args: tuple, kwargs: dict[str, Any]
    ) -> Optional[CacheEntry]:
        """Returns a cache entry for given args and kwargs if one exists"""
        for entry in self.entries:
            if entry.args == args and entry.kwargs == kwargs:
                return entry
        return None

    def remove_entry(self, entry: CacheEntry) -> None:
        """Manually remove an entry from the cache"""
        self.entries.remove(entry)

    def _set_timer(self, entry: CacheEntry, time_to_live: int) -> None:
        """Creates a timer to delete an entry"""
        Timer(time_to_live, lambda: self.remove_entry(entry)).start()


RunningArgs = dict[tuple[Args, KWArgs], asyncio.Future[Results]]


def async_cache(time_to_live: Optional[int] = None) -> Callable[[Callable], "Wrapper"]:
    """Adds caching support to an asynchrinous function"""

    def inner(fcn: Callable) -> "Wrapper":
        @attrs(kw_only=True)
        class Wrapper:
            cache = attrib(type=Cache)  # type: Cache
            running_cache = attrib(default=Cache(), type=Cache)  # type: Cache

            async def __call__(self, *args, **kwargs):
                cache_entry = self.cache.get_entry_or_none(args, kwargs)
                if cache_entry is None:
                    running_entry = self.running_cache.get_entry_or_none(args, kwargs)
                    click.echo(
                        f"Got {len(self.running_cache.entries)} running_cache entries."
                    )
                    if running_entry is not None:
                        click.echo("running cache hit")
                        return await running_entry.result
                    else:
                        click.echo("running cache miss")

                        async def update_future_with_result() -> Results:
                            result = await fcn(*args, **kwargs)
                            future.set_result(result)
                            self.cache.create_entry(
                                args, kwargs, result, time_to_live=time_to_live
                            )
                            return result

                        loop = asyncio.get_event_loop()
                        future = loop.create_future()

                        running_cache_entry = self.running_cache.create_entry(
                            args, kwargs, future
                        )
                        await update_future_with_result()
                        result = await future
                        self.running_cache.remove_entry(running_cache_entry)
                        return result
                else:
                    click.echo("existing cache hit")
                    return cache_entry.result

            @classmethod
            def build(cls) -> "Wrapper":
                return cls(cache=Cache())

        wrapper = Wrapper.build()
        update_wrapper(wrapper, fcn)

        return wrapper

    return inner
