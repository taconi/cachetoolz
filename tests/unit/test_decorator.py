import operator
from datetime import timedelta
from functools import reduce
from unittest.mock import AsyncMock, Mock, create_autospec, patch
from typing import Coroutine

from ward import each, test

from cachetoolz.decorator import Cache


def sub(*args):
    return reduce(operator.sub, args)


async def mul(*args):
    return reduce(operator.mul, args)


@test(
    '(cache) synchronous functions without caching',
    tags=['unit', 'decorator', 'cache'],
)
def _(
    Backend=each(AsyncMock, Mock),
    args=each((3, 5, 7), (2, 6, 8)),
    expect=each('-9', '-12'),
    key=each(
        'default:694a0d3cd39806a828716e4fa01cffbd',
        'default:61cc1194bdab22449db8981152909985',
    ),
):
    backend = Backend()
    backend.get.return_value = None

    result = str(Cache(backend)(sub)(*args))

    expires_at = timedelta(weeks=20e3)
    if isinstance(backend, AsyncMock):
        backend.get.assert_awaited_once_with(key)
        backend.set.assert_awaited_once_with(key, result, expires_at)
    else:
        backend.get.assert_called_once_with(key)
        backend.set.assert_called_once_with(key, result, expires_at)
    assert result == expect


@test(
    '(cache) asynchronous functions without caching',
    tags=['unit', 'decorator', 'cache'],
)
async def _(
    Backend=each(AsyncMock, Mock),
    args=each((3, 5, 7), (2, 6, 8)),
    expect=each('105', '96'),
    key=each(
        'default:9608330b4ed4c0cc3c33cdb518f6f3ec',
        'default:ae24fe22eecba3c67041c0b143f75713',
    ),
):
    backend = Backend()
    backend.get.return_value = None

    result = str(await Cache(backend)(mul)(*args))

    expires_at = timedelta(weeks=20e3)
    if isinstance(backend, AsyncMock):
        backend.get.assert_awaited_once_with(key)
        backend.set.assert_awaited_once_with(key, result, expires_at)
    else:
        backend.get.assert_called_once_with(key)
        backend.set.assert_called_once_with(key, result, expires_at)
    assert result == expect


@test(
    '(cache) synchronous functions with caching',
    tags=['unit', 'decorator', 'cache'],
)
def _(
    Backend=each(AsyncMock, Mock),
):
    key = 'default:e7125ccd908f05eb3f898f41fa71106f'
    expect = [1, 2]
    backend = Backend()
    backend.get.return_value = str(expect)

    sub_mock = create_autospec(sub)

    result = Cache(backend)(sub_mock)()

    if isinstance(backend, AsyncMock):
        backend.get.assert_awaited_once_with(key)
    else:
        backend.get.assert_called_once_with(key)
    sub_mock.assert_not_called()
    assert result == expect


@test(
    '(cache) asynchronous functions with caching',
    tags=['unit', 'decorator', 'cache'],
)
async def _(
    Backend=each(AsyncMock, Mock),
):
    key = 'default:3ebfe1c6cffc1aeefaf4aa1141935bba'
    expect = [1, 2]
    backend = Backend()
    backend.get.return_value = str(expect)

    coroutine_mock = AsyncMock(spec=Coroutine)
    coroutine_mock.configure_mock(__name__='AsyncMock')

    result = await Cache(backend)(coroutine_mock)()

    if isinstance(backend, AsyncMock):
        backend.get.assert_awaited_once_with(key)
    else:
        backend.get.assert_called_once_with(key)
    coroutine_mock.assert_not_called()
    assert result == expect


@test(
    '(cache) synchronous functions with ttl time',
    tags=['unit', 'decorator', 'cache'],
)
def _(
    Backend=each(AsyncMock, Mock),
    ttl=each(7.0, 10),
    args=each((3, 5, 7), (2, 6, 8)),
    expect=each('-9', '-12'),
    key=each(
        'default:694a0d3cd39806a828716e4fa01cffbd',
        'default:61cc1194bdab22449db8981152909985',
    ),
):
    backend = Backend()
    backend.get.return_value = None

    result = str(Cache(backend)(ttl=ttl)(sub)(*args))

    expires_at = timedelta(seconds=ttl)
    if isinstance(backend, AsyncMock):
        backend.get.assert_awaited_once_with(key)
        backend.set.assert_awaited_once_with(key, result, expires_at)
    else:
        backend.get.assert_called_once_with(key)
        backend.set.assert_called_once_with(key, result, expires_at)
    assert result == expect


@test(
    '(cache) asynchronous functions with ttl time',
    tags=['unit', 'decorator', 'cache'],
)
async def _(
    Backend=each(AsyncMock, Mock),
    ttl=each(7.0, 10),
    args=each((3, 5, 7), (2, 6, 8)),
    expect=each('105', '96'),
    key=each(
        'default:9608330b4ed4c0cc3c33cdb518f6f3ec',
        'default:ae24fe22eecba3c67041c0b143f75713',
    ),
):
    backend = Backend()
    backend.get.return_value = None

    result = str(await Cache(backend)(ttl=ttl)(mul)(*args))

    expires_at = timedelta(seconds=ttl)
    if isinstance(backend, AsyncMock):
        backend.get.assert_awaited_once_with(key)
        backend.set.assert_awaited_once_with(key, result, expires_at)
    else:
        backend.get.assert_called_once_with(key)
        backend.set.assert_called_once_with(key, result, expires_at)
    assert result == expect


@test(
    "(cache) Don't crash when giving error when setting the cache",
    tags=['unit', 'decorator', 'cache', 'raise'],
)
def _(
    Backend=each(AsyncMock, Mock),
):
    exc = TypeError('Error clearing cache')
    backend = Backend()
    backend.get.return_value = None
    backend.set.side_effect = exc
    logger_mocked = Mock()

    with patch('cachetoolz.decorator.get_logger', return_value=logger_mocked):
        cache = Cache(backend)

    result = cache(keygen=lambda *args: 'key')(sub)(3, 2)

    logger_mocked.error.assert_called_once_with(
        "Error to set cache 'key=%s': exception=%s", 'default:key', exc
    )
    assert result == 1


@test(
    '(cache) clear namespaces with synchronous function',
    tags=['unit', 'decorator', 'clear'],
)
def _(
    Backend=each(AsyncMock, Mock),
    args=each((3, 5, 7), (2, 6, 8)),
    expect=each('-9', '-12'),
):
    backend = Backend()
    namespace = 'ns1'

    result = str(Cache(backend).clear(namespaces=[namespace])(sub)(*args))

    if isinstance(backend, AsyncMock):
        backend.clear.assert_awaited_once_with(namespace)
    else:
        backend.clear.assert_called_once_with(namespace)
    assert result == expect


@test(
    '(cache) clear namespaces with asynchronous function',
    tags=['unit', 'decorator', 'clear'],
)
async def _(
    Backend=each(AsyncMock, Mock),
    args=each((3, 5, 7), (2, 6, 8)),
    expect=each('105', '96'),
):
    backend = Backend()
    namespace = 'ns1'

    result = await Cache(backend).clear(namespaces=[namespace])(mul)(*args)

    if isinstance(backend, AsyncMock):
        backend.clear.assert_awaited_once_with(namespace)
    else:
        backend.clear.assert_called_once_with(namespace)
    assert str(result) == expect


@test(
    "(cache) Don't crash when giving error clearing cache",
    tags=['unit', 'decorator', 'clear', 'raise'],
)
def _(
    Backend=each(AsyncMock, Mock),
):
    exc = TypeError('Error clearing cache')
    backend = Backend()
    backend.clear.side_effect = exc
    logger_mocked = Mock()

    with patch('cachetoolz.decorator.get_logger', return_value=logger_mocked):
        cache = Cache(backend)

    result = cache.clear(sub)(3, 2)

    logger_mocked.error.assert_called_once_with(
        "Error to clear cache 'namespaces=%s': exception=%s", ('default',), exc
    )
    assert result == 1
