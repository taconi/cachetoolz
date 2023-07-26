## Cache
A memory cache is available for both synchronous and asynchronous functions.
However, it's crucial to highlight that the cache will be reset or cleared
whenever the program is interrupted.

```python
from cachetoolz import cache

# It's equivalent to that
from cachetoolz import AsyncInMemory, Cache
cache = Cache(AsyncInMemory())

@cache()
def sub(x, y):
    return x - y

@cache()
async def mul(x, y):
    return x * y
```

Caches a function call and stores it in the namespace.

Bare decorator, ``@cache``, is supported as well as a call with
keyword arguments ``@cache(ttl=7200)``.



| Parameter   | Type | Description | Default |
| ----------- | ----------- | ---- | ------- |
| `backend`   | Union[AsyncBackendABC, BackendABC] | Cache backend | _required_ |

With redis async backend
```python
from cachetoolz import AsyncRedisBackend, Cache
cache = Cache(AsyncRedisBackend())
```

With redis sync backend
```python
from cachetoolz import RedisBackend, Cache
cache = Cache(RedisBackend())
```

For more details on backends see [backends](/backends/)

### @cache


| Parameter   | Type | Description | Default |
| ----------- | ----------- | ---- | ------- |
| `ttl`       | `int`, `float`, `timedelta` | cache ttl (time to live) | `math.inf` |
| `namespace` | `str` | namespace to cache | `"default"` |
| `typed`     | `bool` | If typed is set to true, function arguments of different types will be cached separately | `False` |
| `keygen`    | `cachetoolz.types.KeyGenerator` | function to generate a cache identifier key | `cachetoolz.utils.default_keygen` |


Examples:

A simple cache
```python
>>> @cache
def func(*args, **kwargs):
    ...
```

Specific a namespace
```python
@cache(namespace='bar')
def func(*args, **kwargs):
    ...
```

Set an expiration time in seconds
```python
@cache(ttl=60)
def func(*args, **kwargs):
    ...
```

Use timedelta to set the expiration
```python
from datetime import timedelta
@cache(ttl=timedelta(days=1))
def func(*args, **kwargs):
    ...
```

Differentiate caching based on argument types
```python
@cache(typed=True)
def func(*args, **kwargs):
    ...
```

Using a custom keygen
```python
def custom_keygen(
    typed: bool, func: Func, *args: P.args, **kwargs: P.kwargs
) -> str:
    '''Build a key to a function.

    Parameters
    ----------
    typed
        If typed is set to true, function arguments of different types
        will be cached separately
    func
        Function
    args
        Function positional arguments
    kwargs
        Named function arguments

    Returns
    -------
        Cache identifier key

     '''

@cache(keygen=custom_keygen)
def func(*args, **kwargs):
    ...
```

### @cache.clear
Clears all caches for all namespaces.

This decorator will clear all caches contained in the specified namespaces once
the decorated function is executed

| Parameter    | Type | Description | Default |
| ------------ | ----------- | ---- | ------- |
| `namespaces` | `Sequence[str]` | namespace to be cleaned. | `('default',)` |

Examples:

A simple clear cache
```python
@cache.clear
def func(*args, **kwargs):
    ...
```

Defining the namespaces to be cleaned up
```python
@cache.clear(namespaces=['foo'])
def func(*args, **kwargs):
    ...
```

## Backend
### In Memory

Both synchronous and asynchronous in-memory backends are available.
Just instantiate them, they don't take any arguments.

```python
from cachetoolz import AsyncInMemory, InMemory

async_in_memory = AsyncInMemory()
sync_in_memory = InMemory()
```
Async functions can be decorated when the synchronous backend is being used,
but it is important to be careful as there can be potential errors or
inconsistencies when trying to access the backend

### Redis
With Redis, you have the flexibility to choose between using either the
asynchronous or synchronous backend by simply specifying the connection string.

#### RedisBackend
| Parameter    | Type | Description | Default |
| ------------ | ----------- | ---- | ------- |
| `url` | `str` | Redis url. | _required_ |
| `kwargs` | `dict[str, Any]` | Takes the same constructor arguments as [`redis.client.Redis.from_url`](https://redis.readthedocs.io/en/latest/connections.html#redis.Redis.from_url). The `decode_responses` parameter will always be `True` as the result needs to be returned as a string. | `{}` |

---

#### AsyncRedisBackend
| Parameter    | Type | Description | Default |
| ------------ | ----------- | ---- | ------- |
| `url` | `str` | Redis url. | _required_ |
| `kwargs` | `dict[str, Any]` | Takes the same constructor arguments as [`redis.asyncio.client.Redis.from_url`](https://redis.readthedocs.io/en/latest/connections.html#redis.asyncio.client.Redis.from_url). The `decode_responses` parameter will always be ``True`` as the result needs to be returned as a string. | `{}` |

### Mongo

Mongo also supports asynchronous and synchronous backend

#### MongoBackend
| Parameter    | Type | Description | Default |
| ------------ | ----------- | ---- | ------- |
| `host` | `str` | MongoDB URI. | ``'localhost'`` |
| `database` | `str` | Cache database name. | ``'.cachetoolz'`` |
| `kwargs` | `dict[str, Any]` | Takes the same constructor arguments as [`pymongo.mongo_client.MongoClient`](https://pymongo.readthedocs.io/en/stable/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient). | ``{}`` |


---

#### AsyncMongoBackend
| Parameter    | Type | Description | Default |
| ------------ | ----------- | ---- | ------- |
| `host` | `str` | MongoDB URI. | ``'localhost'`` |
| `database` | `str` | Cache database name. | ``'.cachetoolz'`` |
| `kwargs` | `dict[str, Any]` | Takes the same constructor arguments as [`pymongo.mongo_client.MongoClient`](https://pymongo.readthedocs.io/en/stable/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient). | ``{}`` |

## Coder
The coder object is responsible for encoding and decoding python objects to json
to be cached. Some classes are already supported but if you need you can add new encoders and decoders

### Supported Types
* None
* bytes
* str
* int
* float
* bool
* dict
* set
* frozenset
* list
* tuple  # is decoded to a list
* uuid.UUID
* pathlib.Path
* collections.deque
* re.Pattern
* datetime.time
* datetime.date
* datetime.datetime
* datetime.timedelta
* decimal.Decimal
* ipaddress.IPv4Address
* apaddress.IPv4Interface
* apaddress.IPv4Network
* apaddress.IPv6Address
* apaddress.IPv6Interface
* apaddress.IPv6Network

### Register Coder

You can register a class for decoding, it needs to have the ``encode``
and ``decode`` methods where the ``encode`` method must have a
parameter called ``value`` and must have the type annotated.
These methods can be ``instance``, ``@staticmethod``, or
``@classmethod``.
The decode function will receive the exact value that is returned by
the encode function.

Class methods
```python
from collections import deque

@coder.register
class DequeCoder:
    @classmethod
    def encode(cls, value: deque):
        return {'iterable': list(value), 'maxlen': value.maxlen}

    @classmethod
    def decode(cls, value):
        return deque(val['iterable'], val['maxlen'])
```

Static methods
```python
from collections import deque

@coder.register
class DequeCoder:
    @staticmethod
    def encode(value: deque):
        return {'iterable': list(value), 'maxlen': value.maxlen}

    @staticmethod
    def decode(value):
        return deque(val['iterable'], val['maxlen'])
```

Instace methods
```python
from collections import deque

@coder.register
class DequeCoder:
    def encode(self, value: deque):
        return {'iterable': list(value), 'maxlen': value.maxlen}

    def decode(self, value):
         return deque(val['iterable'], val['maxlen'])
```

When registering a class, it will be instantiated.
Therefore, if the class requires any initialization parameters,
you can register an instance of it along with the necessary parameters.

```python
from collections import deque

class DequeCoder:
    def __init__(self, foo):
        self.foo = foo

     def encode(self, value: deque):
        return {'iterable': list(value), 'maxlen': value.maxlen}

    def decode(self, value):
        return deque(val['iterable'], val['maxlen'])

coder.register(DequeCoder(foo='bar'))
```

### Register Encode
If you have no need to decode the result or prefer to add it separately, you have the option to register a single encoder.

```python
from collections import deque

from cachetoolz.coder import encoder


@encoder.register('deque')
def _(value: deque):
    return {'iterable': list(value), 'maxlen': value.maxlen}
```

### Register Decode
When registering a decoder, it is essential to ensure that the name matches the name of the encoder. Failure to do so will result in a lack of connection between them.

```python
from collections import deque

from cachetoolz.coder import decoder

@decoder.register('deque')
def _(value):
    return deque(value['iterable'], value['maxlen'])
```
