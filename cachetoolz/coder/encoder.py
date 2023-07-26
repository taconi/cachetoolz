"""Encoder module."""

import json
import re
from collections import deque
from collections.abc import Set
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from functools import singledispatch
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from json import JSONEncoder
from pathlib import PosixPath
from uuid import UUID

try:
    from inspect import get_annotations
except ImportError:
    from get_annotations import get_annotations

from charset_normalizer import detect
from funcy import walk

from .. import types
from ..exceptions import RegistryError, UnknownEncoderError
from ..utils import decoder_name


class Encoder(JSONEncoder):
    """JSON encoder class."""

    def default(self, o):
        """Turns a python object into a json object.

        Parameters
        ----------
        o
            Python object

        """
        return encode(o)


def register(name: str) -> types.Decorator:
    """Register a encoder.

    Parameters
    ----------
    name
        Encoder name.

    Examples
    --------
    >>> from collections import deque
    >>> @register('deque')
    ... def _(value: deque):
    ...     return {'iterable': list(value), 'maxlen': value.maxlen}
    ...

    """

    def wrapper(func: types.Encoder) -> types.Encoder:
        if not callable(func):
            raise RegistryError('encoder needs to be a callable')
        if 'value' not in (annotations := get_annotations(func)):
            raise RegistryError(
                'encoder needs to have a parameter named `value` '
                'and it needs to have the type annotated'
            )

        _type = annotations['value']

        encode.register(_type)(
            lambda value: {'__val': func(value), '__decoder': name}
        )
        return func

    return wrapper


@singledispatch
def encode(value):
    """Turns a python object into a json object.

    Parameters
    ----------
    value
        Python object

    """
    raise UnknownEncoderError(
        f'Encoder not implemented {value=} type {type(value)}'
    )


@encode.register(str)
@encode.register(int)
@encode.register(float)
@encode.register(bool)
@encode.register(type(None))
def _(value):
    return value


@encode.register
def _(value: Set) -> types.Encoded:
    return {
        '__val': walk(encode, list(value)),
        '__decoder': decoder_name(value),
    }


@encode.register
def _(value: timedelta) -> types.Encoded:
    return {'__val': value.total_seconds(), '__decoder': decoder_name(value)}


@encode.register
def _(value: deque) -> types.Encoded:
    return {
        '__val': {
            'iterable': walk(encode, list(value)),
            'maxlen': value.maxlen,
        },
        '__decoder': decoder_name(value),
    }


@encode.register
def _(value: re.Pattern) -> types.Encoded:
    return {
        '__val': {'pattern': json.dumps(value.pattern), 'flags': value.flags},
        '__decoder': decoder_name(value),
    }


@encode.register
def _(value: bytes) -> types.Encoded:
    encoding = detect(value).get('encoding', 'utf-8')
    return {
        '__val': {'bytes': value.decode(encoding), 'encoding': encoding},
        '__decoder': decoder_name(value),
    }


@encode.register(time)
@encode.register(date)
@encode.register(datetime)
@encode.register(Decimal)
@encode.register(UUID)
@encode.register(PosixPath)
@encode.register(IPv4Address)
@encode.register(IPv4Interface)
@encode.register(IPv4Network)
@encode.register(IPv6Address)
@encode.register(IPv6Interface)
@encode.register(
    IPv6Network,
)
def _(value) -> types.Encoded:
    return {'__val': str(value), '__decoder': decoder_name(value)}
