from datetime import timedelta

from faker import Faker
from ward import each, fixture, test

from cache_tools.backend import AsyncInMemory, InMemory

fake = Faker()


@fixture
def sync_backend():
    return InMemory()


@fixture
def async_backend():
    return AsyncInMemory()


@test('InMemory(set): set', tags=['unit', 'backend', 'set'])
def _(
    backend=sync_backend,
    namespace=each(*[fake.uuid4() for _ in range(10)]),
    key=each(*[fake.uuid4() for _ in range(10)]),
    value=each(*[fake.paragraph() for _ in range(10)]),
):
    backend.set(f'{namespace}:{key}', value, timedelta(days=10))
    assert backend._store[namespace][key].value == value


@test('InMemory(get): no data', tags=['unit', 'backend', 'get'])
def _(backend=sync_backend):
    assert backend.get('namespace:key') is None


@test('InMemory(get): expired', tags=['unit', 'backend', 'get'])
def _(backend=sync_backend):
    key = 'namespace:key'
    backend.set(key, value='dummy', expires_at=-timedelta(days=10))
    assert backend.get('namespace:key') is None


@test('InMemory(get): found', tags=['unit', 'backend', 'get'])
def _(backend=sync_backend):
    key = 'namespace:key'
    value = fake.pystr()
    backend.set(key, value, expires_at=timedelta(days=10))
    assert backend.get('namespace:key') == value


@test('InMemory(clear): namespace', tags=['unit', 'backend', 'clear'])
def _(backend=sync_backend):
    namespace = fake.uuid4()

    backend.set(f'{namespace}:key', fake.uuid4(), timedelta(days=10))
    backend.clear(namespace)

    assert not backend._store[namespace]


@test('AsyncInMemory(set): set', tags=['unit', 'backend', 'set'])
async def _(
    backend=async_backend,
    namespace=each(*[fake.uuid4() for _ in range(10)]),
    key=each(*[fake.uuid4() for _ in range(10)]),
    value=each(*[fake.paragraph() for _ in range(10)]),
):
    await backend.set(f'{namespace}:{key}', value, timedelta(days=10))
    assert backend._store[namespace][key].value == value


@test('AsyncInMemory(get): no data', tags=['unit', 'backend', 'get'])
async def _(backend=async_backend):
    assert await backend.get('namespace:key') is None


@test('AsyncInMemory(get): expired', tags=['unit', 'backend', 'get'])
async def _(backend=async_backend):
    key = 'namespace:key'
    await backend.set(key, value='dummy', expires_at=-timedelta(days=10))
    assert await backend.get('namespace:key') is None


@test('AsyncInMemory(get): found', tags=['unit', 'backend', 'get'])
async def _(backend=async_backend):
    key = 'namespace:key'
    value = fake.pystr()
    await backend.set(key, value, expires_at=timedelta(days=10))
    assert await backend.get('namespace:key') == value


@test('AsyncInMemory(clear): namespace', tags=['unit', 'backend', 'clear'])
async def _(backend=async_backend):
    namespace = fake.uuid4()

    await backend.set(f'{namespace}:key', fake.uuid4(), timedelta(days=10))
    await backend.clear(namespace)

    assert not backend._store[namespace]
