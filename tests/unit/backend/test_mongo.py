from datetime import timedelta

from faker import Faker
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from ward import each, fixture, test

from cache_tools.backend import AsyncMongoBackend, MongoBackend

fake = Faker()

url = 'mongodb://username:password@localhost:27017'
db_sync = 'sync'
db_async = 'async'


@fixture
def sync_mongo():
    with MongoClient(url) as client:
        yield client[db_sync]

        client.drop_database(db_sync)


@fixture
async def async_mongo():
    client = AsyncIOMotorClient(url)
    yield client[db_async]

    await client.drop_database(db_async)
    client.close()


@fixture
def sync_backend():
    return MongoBackend(url, db_sync)


@fixture
def async_backend():
    return AsyncMongoBackend(url, db_async)


@test('MongoBackend(set): set', tags=['unit', 'backend', 'set'])
def _(
    backend=sync_backend,
    database=sync_mongo,
    namespace=each(*[fake.uuid4() for _ in range(10)]),
    keyhash=each(*[fake.uuid4() for _ in range(10)]),
    value=each(*[fake.paragraph() for _ in range(10)]),
):
    key = f'{namespace}:{keyhash}'
    backend.set(key, value, timedelta(seconds=60))

    cached = database[namespace].find_one({'key': keyhash})
    assert cached['value'] == value


@test('MongoBackend(get): no data', tags=['unit', 'backend', 'mongo', 'get'])
def _(backend=sync_backend):
    assert backend.get(f'namespace:{fake.uuid4()}') is None


@test('MongoBackend(get): expired', tags=['unit', 'backend', 'mongo', 'get'])
def _(backend=sync_backend):
    key = f'namespace:{fake.uuid4()}'
    backend.set(key, value='dummy', expires_at=-timedelta(days=10))

    assert backend.get(key) is None


@test('MongoBackend(get): found', tags=['unit', 'backend', 'mongo', 'get'])
def _(backend=sync_backend):
    key = 'namespace:{fake.uuid4()}'
    value = fake.pystr()
    backend.set(key, value, expires_at=timedelta(days=10))

    assert backend.get(key) == value


@test(
    'MongoBackend(clear): namespace',
    tags=['unit', 'backend', 'mongo', 'clear'],
)
def _(backend=sync_backend, database=sync_mongo):
    namespace = fake.uuid4()

    backend.set(f'{namespace}:key', fake.uuid4(), timedelta(days=10))
    backend.clear(namespace)

    assert namespace not in database.list_collection_names()


@test(
    'AsyncMongoBackend(set): set',
    tags=['unit', 'backend', 'mongo', 'async', 'set'],
)
async def _(
    backend=async_backend,
    database=async_mongo,
    namespace=each(*[fake.uuid4() for _ in range(10)]),
    keyhash=each(*[fake.uuid4() for _ in range(10)]),
    value=each(*[fake.paragraph() for _ in range(10)]),
):
    key = f'{namespace}:{keyhash}'
    await backend.set(key, value, timedelta(seconds=60))

    cached = await database[namespace].find_one({'key': keyhash})
    assert cached['value'] == value


@test(
    'AsyncMongoBackend(get): no data',
    tags=['unit', 'backend', 'mongo', 'async', 'get'],
)
async def _(backend=async_backend):
    assert await backend.get(f'namespace:{fake.uuid4()}') is None


@test(
    'AsyncMongoBackend(get): expired',
    tags=['unit', 'backend', 'mongo', 'async', 'get'],
)
async def _(backend=async_backend):
    key = 'namespace:{fake.uuid4()}'
    await backend.set(key, value='dummy', expires_at=-timedelta(seconds=60))

    assert await backend.get(key) is None


@test(
    'AsyncMongoBackend(get): found',
    tags=['unit', 'backend', 'mongo', 'async', 'get'],
)
async def _(backend=async_backend):
    key = 'namespace:{fake.uuid4()}'
    value = fake.pystr()
    await backend.set(key, value, expires_at=timedelta(seconds=60))

    assert await backend.get(key) == value


@test(
    'AsyncMongoBackend(clear): namespace',
    tags=['unit', 'backend', 'mongo', 'async', 'clear'],
)
async def _(backend=async_backend, database=async_mongo):
    namespace = fake.uuid4()

    await backend.set(f'{namespace}:key', fake.uuid4(), timedelta(days=10))
    await backend.clear(namespace)

    assert namespace not in await database.list_collection_names()
