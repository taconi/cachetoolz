from typing import Any

from cachetoolz import AsyncRedisBackend, Cache
from cachetoolz.coder import coder

from .models import Hero

cache = Cache(AsyncRedisBackend('redis://localhost:6379/0'))


@coder.register
class HeroCoder:
    def encode(self, value: Hero):
        return value.dict()

    def decode(self, value: dict[str, Any]):
        return Hero(**value)
