"""Decoder module."""

import json
import re
from collections import deque
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from json import JSONDecoder
from pathlib import Path
from typing import Any, ClassVar, Dict
from uuid import UUID

from .. import types
from ..exceptions import RegistryError, UnknownDecoderError


class Decoder(JSONDecoder):
    """JSON decoder class."""

    DECODERS: ClassVar[Dict[str, types.Decoder]] = {
        'time': time.fromisoformat,
        'date': date.fromisoformat,
        'datetime': datetime.fromisoformat,
        'timedelta': lambda val: timedelta(seconds=val),
        'decimal': Decimal,
        'uuid': UUID,
        'posixpath': Path,
        'ipv4address': IPv4Address,
        'ipv4interface': IPv4Interface,
        'ipv4network': IPv4Network,
        'ipv6address': IPv6Address,
        'ipv6interface': IPv6Interface,
        'ipv6network': IPv6Network,
        'set': set,
        'frozenset': frozenset,
        'bytes': lambda val: val['bytes'].encode(val['encoding']),
        'deque': lambda val: deque(val['iterable'], val['maxlen']),
        'pattern': lambda val: re.compile(
            json.loads(val['pattern']), val['flags']
        ),
    }

    def __init__(self, **kwargs):
        """Initialize the instance."""
        kwargs['object_hook'] = self._object_hook
        super().__init__(**kwargs)

    def _object_hook(self, obj) -> Any:
        if not (decoder := obj.get('__decoder')):
            return obj

        if decoder not in self.DECODERS:
            raise UnknownDecoderError(f'Decoder "{decoder}" not registered')

        return self.DECODERS[decoder](obj['__val'])


def register(name: str) -> types.Decorator:
    """Register a decoder.

    Parameters
    ----------
    name : str
        Decoder name.

    Examples
    --------
    >>> from collections import deque
    >>> from typing import Any
    >>> @register('deque')
    ... def _(val: dict[str, Any]):
    ...     return deque(val['iterable'], val['maxlen'])
    ...

    """

    def wrapper(func: types.Decoder) -> types.Decoder:
        if not callable(func):
            raise RegistryError('decoder needs to be a callable')

        Decoder.DECODERS[name] = func
        return func

    return wrapper
