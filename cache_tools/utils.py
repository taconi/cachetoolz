"""Utils functions."""

import asyncio
import pickle
from functools import wraps
from hashlib import md5
from inspect import isawaitable
from itertools import chain
from typing import Any, Optional

import nest_asyncio

from .types import Decorator, Func, KeyGenerator, Manipulator, P, T


def default_keygen(
    typed: bool, func: Func, *args: P.args, **kwargs: P.kwargs
) -> str:
    """Build a key to a function.

    Parameters
    ----------
    typed
        If typed is set to true, function arguments of different types
        will be cached separately
    func
        Function
    args
        Function positional arguments
    kwargs
        Named function arguments

    Returns
    -------
        Cache identifier key

    """
    hashable_args = (
        (func.__module__, func.__name__),
        args,
        tuple(sorted(kwargs.items())),
    )
    if typed:
        hashable_args += tuple(
            type(value) for value in chain(args, sorted(kwargs.values()))
        )
    return md5(pickle.dumps(hashable_args)).hexdigest()


async def make_key(
    namespace: str,
    keygen: Optional[KeyGenerator],
    typed: bool,
    func: Func,
    *args: P.args,
    **kwargs: P.kwargs,
) -> str:
    """Make a key to a function.

    Parameters
    ----------
    namespaces
        namespace to cache
    keygen
        function to generate a cache identifier key
    func
        Function
    typed
        If typed is set to true, function arguments of different types
        will be cached separately
    args
        Function positional arguments
    kwargs
        Named function arguments

    Returns
    -------
        Cache identifier key with namespace

    """
    key = await ensure_async(
        keygen or default_keygen, typed, func, *args, **kwargs
    )
    return f'{namespace}:{key}'


def decoder_name(obj) -> str:
    """Gets a class name.

    Parameters
    ----------
    obj
        Object to get class name

    """
    return obj.__class__.__name__.lower()


async def ensure_async(func: Func, *args: P.args, **kwargs: P.kwargs) -> Any:
    """Wait a function that needs to be awaited.

    Parameters
    ----------
    func
        Function
    args
        Function positional arguments
    kwargs
        Named function arguments

    """
    result = func(*args, **kwargs)
    return await result if isawaitable(result) else result


def manipulate(manipulator: Manipulator) -> Decorator:
    """Decorate a function.

    Parameters
    ----------
    manipulator
        Function that will handle a decorated function

    """
    try:
        nest_asyncio.apply()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        nest_asyncio.apply(loop)

    def wrapper(func: Func) -> Func:
        async def _async(*args: P.args, **kwargs: P.kwargs) -> T:
            return await manipulator(func, *args, **kwargs)

        def _sync(*args: P.args, **kwargs: P.kwargs) -> T:
            return asyncio.run(
                ensure_async(manipulator, func, *args, **kwargs)
            )

        if asyncio.iscoroutinefunction(func):
            return wraps(func)(_async)
        return wraps(func)(_sync)

    return wrapper
