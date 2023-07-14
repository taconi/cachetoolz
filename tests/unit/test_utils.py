import asyncio
import pickle
from datetime import date, datetime, timedelta
from unittest import mock
from uuid import uuid4

from charset_normalizer import detect
from ward import each, test

from cache_tools import utils


def func(*args, **kwargs):
    return None


@test('default key generator', tags=['unit', 'default_keygen'])
def _(
    args=each(tuple(), (2,)),
    kwargs=each(dict(), {'y': 1}),
    key_hash=each(
        'bd7f1a8de0b4f03beaa74640089d77ab', 'c31adf12d6e7cefe404da1c528820202'
    ),
):
    result = utils.default_keygen(False, func, *args, **kwargs)
    assert result == key_hash


@test('default key generator typed', tags=['unit', 'default_keygen'])
def _(
    args=each((2,), (2.0,)),
    kwargs=each({'y': 1}, {'y': 1.0}),
    key_hash=each(
        '32675843b113612781754aff2740f422', 'bc8a862455ae47765e5546d50dafbf6a'
    ),
):
    result = utils.default_keygen(True, func, *args, **kwargs)
    assert result == key_hash


@test('make key with default key generator', tags=['unit', 'make_key'])
async def _(namespace=each('default', 'hero', 'chips')):
    result = await utils.make_key(namespace, None, False, func)
    assert result == f'{namespace}:bd7f1a8de0b4f03beaa74640089d77ab'


@test('make key with key generator', tags=['unit', 'make_key'])
async def _(namespace=each('default', 'hero', 'chips')):
    def key_gen(typed, func_, *args, **kwargs):
        key = pickle.dumps(None)
        return key.decode(detect(key)['encoding'])

    result = await utils.make_key(namespace, key_gen, False, func)
    assert result == f'{namespace}:耄丮'


@test('make key with async key generator', tags=['unit', 'make_key', 'async'])
async def _(namespace=each('default', 'hero', 'chips')):
    async def key_gen(typed, func_, *args, **kwargs):
        await asyncio.sleep(0.0001)
        key = pickle.dumps(None)
        return key.decode(detect(key)['encoding'])

    result = await utils.make_key(namespace, key_gen, False, func)
    assert result == f'{namespace}:耄丮'


@test('ensure async for synchronous functions', tags=['unit', 'ensure_async'])
async def _():
    def ensure():
        return True

    assert await utils.ensure_async(ensure)


@test(
    'ensure async for asynchronous functions',
    tags=['unit', 'ensure_async', 'async'],
)
async def _():
    async def ensure():
        await asyncio.sleep(0.0001)
        return True

    assert await utils.ensure_async(ensure)


@test('get decoder name', tags=['unit', 'decoder_name'])
def _(
    decoder=each(uuid4(), date.today(), datetime.now(), timedelta(days=1)),
    name=each('uuid', 'date', 'datetime', 'timedelta'),
):
    assert utils.decoder_name(decoder) == name


@test('manipulating synchronous functions', tags=['unit', 'manipulate'])
def _():
    def to_be_manipulated(x, y):
        return x + y

    def manipulator(func, *args, **kwargs):
        result = func(*args, **kwargs)
        return result * 2

    manipulated = utils.manipulate(manipulator)(to_be_manipulated)

    assert manipulated(2, 2) == 8


@test(
    'manipulating synchronous functions with asynchronous manipulator',
    tags=['unit', 'manipulate'],
)
def _():
    def to_be_manipulated(x, y):
        return x + y

    async def manipulator(func, *args, **kwargs):
        result = func(*args, **kwargs)
        return result * 2

    manipulated = utils.manipulate(manipulator)(to_be_manipulated)

    assert manipulated(2, 2) == 8


@test(
    'manipulating asynchronous functions', tags=['unit', 'manipulate', 'async']
)
async def _():
    async def to_be_manipulated(x, y):
        return x + y

    async def manipulator(func, *args, **kwargs):
        result = await func(*args, **kwargs)
        return result * 2

    manipulated = utils.manipulate(manipulator)(to_be_manipulated)

    assert await manipulated(2, 2) == 8
