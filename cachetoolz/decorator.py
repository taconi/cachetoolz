"""Decorator module."""

import asyncio
from datetime import timedelta
from math import inf, isinf
from typing import Optional, Sequence, Union

from funcy import autocurry as curry

from .abc import AsyncBackendABC, BackendABC
from .coder import coder
from .log import get_logger
from .types import Decorator, Func, KeyGenerator, P, T
from .utils import ensure_async, make_key, manipulate


class Cache:
    """Caches a function call and stores it in the namespace.

    Parameters
    ----------
    expire
        cache expiration time in seconds
    namespace
        namespace to cache
    typed
        If typed is set to true, function arguments of different types
        will be cached separately
    keygen
        function to generate a cache identifier key

    Examples
    --------
    >>> @cache()
    ... def foo(_id):
    ...     ...
    ...

    >>> @cache(namespace='bar')  # specific a namespace
    ... def bar(filters):
    ...     ...
    ...

    >>> @cache(60)  # set an expiration time in seconds
    ... def foo_bar(filters):
    ...     ...
    ...

    >>> from datetime import timedelta
    >>> @cache(timedelta(days=1))  # Use timedelta to set the expiration
    ... def foobar(filters):
    ...     ...
    ...

    """

    def __init__(self, backend: Union[AsyncBackendABC, BackendABC]):
        """Initialize the instance.

        Parameters
        ----------
        backend
            Cache backend

        """
        self.backend = backend
        self._logger = get_logger()

    async def _cache(
        self,
        expire: timedelta,
        keygen: KeyGenerator,
        func: Func,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        key = await keygen(func, *args, **kwargs)

        if (result := await ensure_async(self.backend.get, key)) is not None:
            return coder.decode(result)

        result = coder.encode(await ensure_async(func, *args, **kwargs))

        try:
            await ensure_async(self.backend.set, key, result, expire)
        except Exception as exception:
            self._logger.error(
                "Error to set cache 'key=%s': exception=%s", key, exception
            )

        return coder.decode(result)

    def __call__(
        self,
        expire: Union[int, float, timedelta] = inf,
        *,
        namespace: str = 'default',
        typed: bool = False,
        keygen: Optional[KeyGenerator] = None,
    ) -> Decorator:
        """Caches a function call and stores it in the namespace."""
        if isinf(expire):
            expire = timedelta(weeks=20e3)
        elif not isinstance(expire, timedelta):
            expire = timedelta(seconds=expire)

        keygen = curry(make_key)(namespace, keygen, typed)
        _cache = curry(Cache._cache)(self, expire, keygen)
        return manipulate(_cache)

    async def _clear(
        self,
        namespaces: Sequence[str],
        func: Func,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        try:
            await asyncio.gather(
                *[ensure_async(self.backend.clear, ns) for ns in namespaces]
            )
        except Exception as exception:
            self._logger.error(
                "Error to clear cache 'namespaces=%s': exception=%s",
                namespaces,
                exception,
            )

        result = coder.encode(await ensure_async(func, *args, **kwargs))
        return coder.decode(result)

    def clear(self, namespaces: Sequence[str] = ('default',)) -> Decorator:
        """Clears all caches for all namespaces.

        Parameters
        ----------
        namespaces
            namespace to be cleaned.

        Examples
        --------
        >>> @cache.clear(namespaces=['book'])
        ... def create_book(book):
        ...     ...

        """
        _clear = curry(Cache._clear)(self, namespaces)
        return manipulate(_clear)