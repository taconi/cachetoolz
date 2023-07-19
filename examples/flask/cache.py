from typing import Any

from cachetoolz import AsyncMemoryMongo, Cache
from cachetoolz.coder import decoder, encoder

from .models import Hero

cache = Cache(AsyncMemoryMongo('mongodb://root:password@localhost:27017'))


@encoder.register('hero')
def _(value: Hero):
    return value.dict()


@decoder.register('hero')
def _(value: dict[str, Any]):
    return Hero(**value)
