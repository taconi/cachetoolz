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

    Bare decorator, ``@cache``, is supported as well as a call with
    keyword arguments ``@cache(ttl=7200)``.


    Parameters
    ----------
    backend
        Cache backend

    Examples
    --------

    With redis async backend
    >>> from cachetoolz import AsyncRedisBackend, Cache
    >>> cache = Cache(AsyncRedisBackend())

    With redis sync backend
    >>> from cachetoolz import RedisBackend, Cache
    >>> cache = Cache(RedisBackend())


    # @cache
    Decorator for caching a function call.

    Parameters
    ----------
    ttl : int | float | timedelta, default=math.inf
        cache ttl (time to live)
    namespace : str, default='default'
        namespace to cache
    typed : bool, default=False
        If typed is set to true, function arguments of different types
        will be cached separately
    keygen : Optional[cachetoolz.types.KeyGenerator], default=None
        function to generate a cache identifier key

    Examples
    --------
    A simple cache
    >>> @cache
    ... def func(*args, **kwargs):
    ...     ...
    ...

    Specific a namespace
    >>> @cache(namespace='bar')
    ... def func(*args, **kwargs):
    ...     ...
    ...

    Set an expiration time in seconds
    >>> @cache(ttl=60)
    ... def func(*args, **kwargs):
    ...     ...
    ...

    Use timedelta to set the expiration
    >>> from datetime import timedelta
    >>> @cache(ttl=timedelta(days=1))
    ... def func(*args, **kwargs):
    ...     ...
    ...

    Differentiate caching based on argument types
    >>> @cache(typed=True)
    ... def func(*args, **kwargs):
    ...     ...
    ...

    Using a custom keygen
    >>> def custom_keygen(
    ...     typed: bool, func: Func, *args: P.args, **kwargs: P.kwargs
    ... ) -> str:
    ...     '''Build a key to a function.
    ...
    ...     Parameters
    ...     ----------
    ...     typed
    ...         If typed is set to true, function arguments of different types
    ...         will be cached separately
    ...     func
    ...         Function
    ...     args
    ...         Function positional arguments
    ...     kwargs
    ...         Named function arguments
    ...
    ...     Returns
    ...     -------
    ...         Cache identifier key
    ...
    ...     '''
    ...
    >>> @cache(keygen=custom_keygen)
    ... def func(*args, **kwargs):
    ...     ...
    ...

    """

    def __init__(self, backend: Union[AsyncBackendABC, BackendABC]):
        """Initialize the cache instance.

        Parameters
        ----------
        backend
            Cache backend

        """
        self.backend = backend
        self._logger = get_logger()

    async def _cache(
        self,
        ttl: timedelta,
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
            await ensure_async(self.backend.set, key, result, ttl)
        except Exception as exception:
            self._logger.error(
                "Error to set cache 'key=%s': exception=%s", key, exception
            )

        return coder.decode(result)

    def __call__(
        self,
        func: Optional[Func] = None,
        /,
        *,
        ttl: Union[int, float, timedelta] = inf,
        namespace: str = 'default',
        typed: bool = False,
        keygen: Optional[KeyGenerator] = None,
    ) -> Decorator:
        """Caches a function call and stores it in the namespace."""
        if isinstance(ttl, (int, float)) and not isinf(ttl):
            ttl = timedelta(seconds=ttl)
        elif isinstance(ttl, timedelta):
            pass
        elif isinf(ttl):
            ttl = timedelta(weeks=20e3)

        keygen = curry(make_key)(namespace, keygen, typed)
        manipulator = manipulate(curry(Cache._cache)(self, ttl, keygen))

        if func:
            # @cache
            return manipulator(func)
        # @cache()
        return manipulator

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

    def clear(
        self,
        func: Optional[Func] = None,
        /,
        *,
        namespaces: Sequence[str] = ('default',),
    ) -> Decorator:
        """Clears all caches for all namespaces.

        This decorator will clear all caches contained in the specified
        namespaces once the decorated function is executed

        Parameters
        ----------
        namespaces : Sequence[str], default=('default',)
            namespace to be cleaned.

        Examples
        --------
        A simple clear cache
        >>> @cache.clear
        ... def func(*args, **kwargs):
        ...     ...

        Defining the namespaces to be cleaned up
        >>> @cache.clear(namespaces=['foo'])
        ... def func(*args, **kwargs):
        ...     ...

        """
        manipulator = manipulate(curry(Cache._clear)(self, namespaces))

        if func:
            # @cache.clear
            return manipulator(func)
        # @cache.clear(namespaces=['ns1'])
        return manipulator
