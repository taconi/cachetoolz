import re
from collections import deque
from dataclasses import asdict, dataclass
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
from pathlib import Path
from typing import Dict
from uuid import UUID


from ward import each, raises, test

from cache_tools.coder import coder
from cache_tools.exceptions import RegistryError, UnknownDecoderError


decoded = (
    {'key': 'value'},
    'string',
    1,
    1.0,
    True,
    False,
    None,
    [1, 2],
    set([1, 2]),
    frozenset([1, 2]),
    timedelta(seconds=60),
    deque([1, 2], 4),
    b'b',
    time(10),
    date.fromisoformat('2023-07-09'),
    datetime.fromisoformat('2023-07-09T17:34:53.149702'),
    Decimal('Infinity'),
    Path('.'),
    IPv4Address('192.0.2.1'),
    IPv4Interface('192.0.2.1/32'),
    IPv4Network('192.0.2.1/32'),
    IPv6Address('2001:db8::'),
    IPv6Interface('2001:db8::/128'),
    IPv6Network('2001:db8::/128'),
    re.compile(r'\s'),
    UUID('aecd57c4-5bf2-433a-b642-08f75465d6b9'),
)

encoded = (
    '{"key": "value"}',
    '"string"',
    '1',
    '1.0',
    'true',
    'false',
    'null',
    '[1, 2]',
    '{"__val": [1, 2], "__decoder": "set"}',
    '{"__val": [1, 2], "__decoder": "frozenset"}',
    '{"__val": 60.0, "__decoder": "timedelta"}',
    '{"__val": {"iterable": [1, 2], "maxlen": 4}, "__decoder": "deque"}',
    '{"__val": {"bytes": "b", "encoding": "ascii"}, "__decoder": "bytes"}',
    '{"__val": "10:00:00", "__decoder": "time"}',
    '{"__val": "2023-07-09", "__decoder": "date"}',
    '{"__val": "2023-07-09 17:34:53.149702", "__decoder": "datetime"}',
    '{"__val": "Infinity", "__decoder": "decimal"}',
    '{"__val": ".", "__decoder": "posixpath"}',
    '{"__val": "192.0.2.1", "__decoder": "ipv4address"}',
    '{"__val": "192.0.2.1/32", "__decoder": "ipv4interface"}',
    '{"__val": "192.0.2.1/32", "__decoder": "ipv4network"}',
    '{"__val": "2001:db8::", "__decoder": "ipv6address"}',
    '{"__val": "2001:db8::/128", "__decoder": "ipv6interface"}',
    '{"__val": "2001:db8::/128", "__decoder": "ipv6network"}',
    '{"__val": {"pattern": "\\"\\\\\\\\s\\"", "flags": 32}, "__decoder": "pattern"}',
    '{"__val": "aecd57c4-5bf2-433a-b642-08f75465d6b9", "__decoder": "uuid"}',
)


@dataclass
class Color:
    name: str


class ColorInstanceSerializer:
    def encode(self, value: Color):
        return asdict(value)

    def decode(self, value: Dict[str, str]):
        return Color(name=value['name'])


class ColorStaticSerializer:
    @staticmethod
    def encode(value: Color):
        return asdict(value)

    @staticmethod
    def decode(value: Dict[str, str]):
        return Color(name=value['name'])


class ColorClassSerializer:
    @classmethod
    def encode(cls, value: Color):
        return asdict(value)

    @classmethod
    def decode(cls, value: Dict[str, str]):
        return Color(name=value['name'])


class ColorMissingDecodeSerializer:
    @staticmethod
    def encode(value: Color):
        return asdict(value)


class ColorMissingEncodeSerializer:
    @staticmethod
    def decode(value: Dict[str, str]):
        return Color(name=value['name'])


@test('json encode object: {encode}', tags=['unit', 'coder', 'encode'])
def _(decode=each(*decoded), encode=each(*encoded)):
    assert coder.encode(decode) == encode


@test('json: decode object', tags=['unit', 'coder', 'decode'])
def _(encode=each(*encoded), decode=each(*decoded)):
    assert coder.decode(encode) == decode


@test('json decoder not found', tags=['unit', 'decode', 'decode', 'raise'])
def _():
    with raises(UnknownDecoderError) as exp:
        coder.decode('{"__val": 1, "__decoder": "unknown"}')

    assert exp.expected_ex_type == UnknownDecoderError
    assert exp.raised.args[0] == 'Decoder "unknown" not registered'


@test('register serializer', tags=['unit', 'coder', 'register'])
def _(
    serializer=each(
        ColorInstanceSerializer,
        ColorStaticSerializer,
        ColorClassSerializer,
        ColorInstanceSerializer(),
        ColorStaticSerializer(),
        ColorClassSerializer(),
    ),
    encode=each(
        '{"__val": {"name": "pink"}, "__decoder": "colorinstance"}',
        '{"__val": {"name": "pink"}, "__decoder": "colorstatic"}',
        '{"__val": {"name": "pink"}, "__decoder": "colorclass"}',
        '{"__val": {"name": "pink"}, "__decoder": "colorinstance"}',
        '{"__val": {"name": "pink"}, "__decoder": "colorstatic"}',
        '{"__val": {"name": "pink"}, "__decoder": "colorclass"}',
    ),
):
    coder.register(serializer)

    color = Color(name='pink')

    assert coder.encode(color) == encode
    assert coder.decode(encode) == color


@test('register serializer', tags=['unit', 'coder', 'register', 'raise'])
def _(
    serializer=each(
        ColorMissingDecodeSerializer,
        ColorMissingEncodeSerializer,
        ColorMissingDecodeSerializer(),
        ColorMissingEncodeSerializer(),
    ),
):
    with raises(RegistryError) as exp:
        coder.register(serializer)

    assert exp.expected_ex_type == RegistryError
    assert exp.raised.args[0] == (
        'Sereliazador is not valid, the class must have implemented '
        'the `encode(value: type)` and `decode(value)` methods'
    )
