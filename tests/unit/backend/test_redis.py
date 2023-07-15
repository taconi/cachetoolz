from datetime import timedelta

from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from faker import Faker
from ward import each, fixture, test

from cache_tools.backend import AsyncRedisBackend, RedisBackend

fake = Faker()
url = 'redis://localhost:6379/{db}'

sync_url = url.format(db='0')
async_url = url.format(db='1')


@fixture
def sync_redis():
    client = Redis.from_url(sync_url, decode_responses=True)
    yield client
    client.flushdb()


@fixture
async def async_redis():
    client = AsyncRedis.from_url(async_url, decode_responses=True)
    yield client
    await client.flushdb()


@fixture
def sync_backend():
    return RedisBackend(sync_url)


@fixture
def async_backend():
    return AsyncRedisBackend(async_url)


@test('RedisBackend(set): set', tags=['unit', 'backend', 'redis', 'set'])
def _(
    backend=sync_backend,
    database=sync_redis,
    namespace=each(*[fake.uuid4() for _ in range(10)]),
    key=each(*[fake.uuid4() for _ in range(10)]),
    value=each(*[fake.paragraph() for _ in range(10)]),
):
    key = f'{namespace}:{key}'
    backend.set(key, value, timedelta(seconds=60))

    assert database.get(key) == value


@test('RedisBackend(get): no data', tags=['unit', 'backend', 'redis', 'get'])
def _(backend=sync_backend):
    assert backend.get(f'namespace:{fake.uuid4()}') is None


@test('RedisBackend(get): expired', tags=['unit', 'backend', 'redis', 'get'])
def _(backend=sync_backend, database=sync_redis):
    key = f'namespace:{fake.uuid4()}'
    backend.set(key, value='dummy', expires_at=timedelta(seconds=1))
    database.expire(key, timedelta(seconds=-1))

    assert backend.get(key) is None


@test('RedisBackend(get): found', tags=['unit', 'backend', 'redis', 'get'])
def _(backend=sync_backend):
    key = f'namespace:{fake.uuid4()}'
    value = fake.pystr()
    backend.set(key, value, expires_at=timedelta(seconds=60))

    assert backend.get(key) == value


@test(
    'RedisBackend(clear): namespace',
    tags=['unit', 'backend', 'redis', 'clear'],
)
def _(backend=sync_backend, database=sync_redis):
    namespace = fake.uuid4()

    backend.set(f'{namespace}:key', fake.uuid4(), timedelta(seconds=60))
    backend.clear(namespace)

    assert not database.exists(f'{namespace}:*')


@test(
    'AsyncRedisBackend(set): set',
    tags=['unit', 'backend', 'redis', 'async', 'set'],
)
async def _(
    backend=async_backend,
    database=async_redis,
    namespace=each(*[fake.uuid4() for _ in range(10)]),
    key=each(*[fake.uuid4() for _ in range(10)]),
    value=each(*[fake.paragraph() for _ in range(10)]),
):
    key = f'{namespace}:{key}'
    await backend.set(key, value, timedelta(days=10))

    assert await database.get(key) == value


@test(
    'AsyncRedisBackend(get): no data',
    tags=['unit', 'backend', 'redis', 'async', 'get'],
)
async def _(backend=async_backend):
    assert await backend.get(f'namespace:{fake.uuid4()}') is None


@test(
    'AsyncRedisBackend(get): expired',
    tags=['unit', 'backend', 'redis', 'async', 'get'],
)
async def _(backend=async_backend, database=async_redis):
    key = 'namespace:{fake.uuid4()}'
    await backend.set(key, value='dummy', expires_at=timedelta(seconds=1))
    await database.expire(key, timedelta(seconds=-1))

    assert await backend.get(key) is None


@test(
    'AsyncRedisBackend(get): found',
    tags=['unit', 'backend', 'redis', 'async', 'get'],
)
async def _(backend=async_backend):
    key = f'namespace:{fake.uuid4()}'
    value = fake.pystr()
    await backend.set(key, value, expires_at=timedelta(seconds=60))

    assert await backend.get(key) == value


@test(
    'AsyncRedisBackend(clear): namespace',
    tags=['unit', 'backend', 'redis', 'async', 'clear'],
)
async def _(backend=async_backend, database=async_redis):
    namespace = fake.uuid4()

    await backend.set(f'{namespace}:key', fake.uuid4(), timedelta(seconds=60))
    await backend.clear(namespace)

    assert not await database.exists(f'{namespace}:*')
