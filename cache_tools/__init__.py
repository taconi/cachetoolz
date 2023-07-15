"""Moduel interface."""

from .backend import AsyncInMemory, InMemory
from .decorator import Cache

__all__ = (
    'AsyncInMemory',
    'InMemory',
    'Cache',
    'cache',
)

cache = Cache(AsyncInMemory())
