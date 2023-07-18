"""Moduel interface."""

from .backend import (
    AsyncInMemory,
    AsyncMongoBackend,
    AsyncRedisBackend,
    InMemory,
    MongoBackend,
    RedisBackend,
)
from .decorator import Cache

__all__ = (
    'AsyncInMemory',
    'InMemory',
    'AsyncMongoBackend',
    'MongoBackend',
    'AsyncRedisBackend',
    'RedisBackend',
    'Cache',
    'cache',
)

cache = Cache(AsyncInMemory())
