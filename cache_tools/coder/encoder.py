"""Encoder module."""

import inspect
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

from charset_normalizer import detect
from funcy import walk

from .. import types
from ..exceptions import RegistryError, UnknownEncoderError
from ..utils import decoder_name


class Encoder(JSONEncoder):
    """Encoder class."""

    def default(self, o):
        """Turns a python object into a json object.

        Parameters
        ----------
        o
            Python object

        """
        return encode(o)


def register(func: types.Encoder, decoder: str | None = None) -> types.Encoder:
    """Register a encoder.

    Parameters
    ----------
    func
        Encoder function.
    decoder
        Decoder key to keep de function.

    Examples
    --------
    >>> from collections import deque
    >>> @register
    ... def deque_encoder(value: deque):
    ...     return {'iterable': list(value), 'maxlen': value.maxlen}
    ...

    """
    if not callable(func):
        raise RegistryError('encoder needs to be a callable')
    if 'value' not in (annotations := inspect.get_annotations(func)):
        raise RegistryError(
            'encoder needs to have a parameter named `value` '
            'and it needs to have the type annotated'
        )

    _type = annotations['value']
    decoder = decoder or re.sub('encode[r]?', '', func.__name__).strip('_')

    encode.register(_type)(
        lambda value: {'__val': func(value), '__decoder': decoder}
    )
    return func


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


@encode.register
def _(value: str | int | float | bool | None):
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


@encode.register
def _(
    value: time
    | date
    | datetime
    | Decimal
    | UUID
    | PosixPath
    | IPv4Address
    | IPv4Interface
    | IPv4Network
    | IPv6Address
    | IPv6Interface
    | IPv6Network,
) -> types.Encoded:
    return {'__val': str(value), '__decoder': decoder_name(value)}
