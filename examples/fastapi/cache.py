from typing import Any

from cachetoolz import AsyncMemoryRedis, Cache
from cachetoolz.coder import coder

from .models import Hero

cache = Cache(AsyncMemoryRedis('redis://localhost:6379/0'))


@coder.register
class HeroSerializer:
    def encode(self, value: Hero):
        return value.dict()

    def decode(self, value: dict[str, Any]):
        return Hero(**value)
