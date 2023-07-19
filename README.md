# Cache Toolz
<!-- [![Documentation Status](https://readthedocs.org/projects/cachetoolz/badge/?version=latest)](https://cachetoolz.readthedocs.io/en/latest/?badge=latest) -->
[![Badge License](https://img.shields.io/github/license/taconi/cachetoolz?label=License&color=%234B78E6)](https://raw.githubusercontent.com/taconi/cachetoolz/main/LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/taconi/cachetoolz/tests.yml?logo=githubactions&branch=main&color=%23FA9BFA&label=tests)](https://github.com/taconi/cachetoolz/actions/workflows/tests.yml)
[![codecov](https://img.shields.io/codecov/c/github/taconi/cachetoolz?logo=codecov&style=flat&label=Coverage&color=%2373DC8C)](https://codecov.io/gh/taconi/cachetoolz)
![Repo Size](https://img.shields.io/github/repo-size/taconi/cachetoolz.svg?label=Repo%20size&color=%234B78E6)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/cachetoolz.svg?logo=python&color=%234B78E6)](https://pypi.python.org/pypi/cachetoolz/)
[![PyPI version](https://img.shields.io/pypi/v/cachetoolz.svg?logo=pypi&color=%23FA9BFA)](https://pypi.org/project/cachetoolz/)
[![Downloads](https://img.shields.io/pypi/dm/cachetoolz?logo=pypi&color=%2373DC8C)](https://pypi.org/project/cachetoolz/)


This library offers a decorator that enhances the functionality of caching functions.

Caching is a technique commonly used in software development to improve performance by storing the results of expensive or time-consuming function calls. With this library, you can easily apply caching to your functions using a decorator.

The decorator provided by this library automatically checks if the function has been called with the same set of arguments before. If it has, instead of executing the function again, it returns the cached result, saving valuable processing time. However, if the function is called with new or different arguments, it will execute normally and cache the result for future use.

By incorporating this caching decorator into your code, you can optimize the execution of functions that involve complex computations, database queries, API calls, or any other operations that could benefit from caching.

Overall, this library simplifies the implementation of caching in your applications, allowing you to enhance performance and reduce resource consumption effectively.

---
# Summary
* **[Installation](#installation)**
  * **[Bundles](#bundles)**
* **[Quickstart](#quickstart)**
  * **[Cache parameters](#cache-parameters)**
    * **[Key generator](#key-generator)**
  * **[Cache clear](#cache-clear)**
  * **[Backends](#backends)**
    * **[In Memory](#in-memory)**
    * **[Remote Backends](#remote-backends)**
        * **[Redis](#redis)**
        * **[Mongo](#mongo)**
  * **[Coder](#coder)**
    * **[Supported Types](#supported-types)**
    * **[Register Coder](#register-coder)**
    * **[Register Encode](#register-encode)**
    * **[Register Decode](#register-decode)**
---

# Installation
cachetoolz is available from [PyPI](https://pypi.org/project/cachetoolz/) and can be installed by running

```bash
pip install cachetoolz
```

## Bundles

Cachetoolz also defines a group of bundles that can be used to install cachetoolz and the dependencies for a given feature.

You can specify these in your requirements or on the pip command-line by using brackets. Multiple bundles can be specified by separating them by commas.
```bash
pip install cachetoolz[redis]
pip install cachetoolz[redis,mongo]
```

The following bundles are available:

#### Backends
* `cachetoolz[redis]`: for using Redis as a backend.
* `cachetoolz[mongo]`: for using Mongo as a backend.

# Quickstart
```python
from asyncio import Lock
from dataclasses import asdict, dataclass, field
from uuid import UUID, uui4

from cachetoolz import AsyncRedisBackend, Cache
from cachetoolz.coder import coder

cache = Cache(AsyncRedisBackend('redis://localhost:6379/0'))

lock = Lock()

TODOS: list['Todo'] = []

@dataclass
class Todo:
    id: UUID = field(default_factory=uuid4, compare=False)
    title: str = field(hash=True)
    status: bool = False

@coder.register
class TodoSerializer:
    """Serializes the Todo object to a valid json."""

    # Need annotated by type
    def encode(self, value: Todo):
        """Encode the Todo object to a valid json."""
        return asdict(value)

    def decode(self, value):
        """Decode to the Todo object."""
        return Todo(**value)

@cache(namespace='todo')
async def get_todo(id: UUID):
    """Get one todo by id."""
    async with lock:
        for todo in TODOS:
            if todo['id'] == id:
                return todo

@cache(namespace='todo')
async def get_todos():
    """Get all todos filtering by title or status."""
    return TODOS

# Clear all caches in all namespaces so that no function has the result lagged to the database for example
@cache.clear(namespaces=['todo'])
async def add_todo(title, status=False):
    """Add todo."""
    todo = Todo(title=title, status=status)
    async with lock:
        if todo not in TODOS:
            TODOS.append(todo)
```

## Cache parameters
The decorator may have configured it with some parameters.
All parameters need to be passed namely.

| Parameter   | Description | Type | Default |
| ----------- | ----------- | ---- | ------- |
| `ttl`       | cache ttl (time to live) | `int`, `float`, `timedelta` | `math.inf` |
| `namespace` | namespace to cache | `str` | `"default"` |
| `typed`     | If typed is set to true, function arguments of different types will be cached separately | `bool` | `False` |
| `keygen`    | function to generate a cache identifier key | `cachetoolz.types.KeyGenerator` | `cachetoolz.utils.default_keygen` |

### Key generator
This must be the signature of a key generator function
```python
def keygen(typed: bool, func: Func, *args: P.args, **kwargs: P.kwargs) -> str:
    """Build a key to a function.

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

    """
```

## Cache clear
This decorator will clear all caches contained in the specified namespaces once the decorated function is executed
Examples:
```python
@cache.clear(namespaces=['book'])
def create_book(book):
    ...
```
## Backends

### In Memory
A memory cache is available for both synchronous and asynchronous functions. However, it's crucial to highlight that the cache will be reset or cleared whenever the program is interrupted.
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

If you have no requirement for executing asynchronous code, it is recommended to utilize the InMemory backend.
Asynchronous functions can be decorated, but it's important to be cautious as there might be potential errors or inconsistencies when attempting to access the backend
```python
from cachetoolz import InMemory, Cache

cache = Cache(InMemory())

@cache()
def sub(x, y):
    return x - y

@cache()
async def mul(x, y):
    return x * y
```

### Remote backends
Support for remote backends such as Redis and MongoDB.

#### Redis
With Redis, you have the flexibility to choose between using either the asynchronous or synchronous backend by simply specifying the connection string.
```python
from cachetoolz import AsyncRedisBackend, RedisBackend, Cache

cache = Cache(AsyncRedisBackend('redis://localhost:6379/0'))

@cache()
def sub(x, y):
    return x - y

@cache()
async def mul(x, y):
    return x * y
```

#### Mongo
Mongo also supports asynchronous and synchronous backend
```python
from cachetoolz import AsyncMongoBackend, MongoBackend, Cache

cache = Cache(AsyncMongoBackend('mongodb://username:password@localhost:27017'))


@cache()
def sub(x, y):
    return x - y

@cache()
async def mul(x, y):
    return x * y
```

## Coder
The coder object is responsible for encoding and decoding python objects to json to be cached. Some classes are already supported but if you need you can add new encoders and decoders

#### Supported Types
```python
None
bytes
str
int
float
bool
dict
set
frozenset
list
tuple  # is decoded to a list
uuid.UUID
pathlib.Path
collections.deque
re.Pattern
datetime.time
datetime.date
datetime.datetime
datetime.timedelta
decimal.Decimal
ipaddress.IPv4Address
apaddress.IPv4Interface
apaddress.IPv4Network
apaddress.IPv6Address
apaddress.IPv6Interface
apaddress.IPv6Network
```

### Register Coder
You can register a class for decoding, it needs to have `encode` and `decode` methods where the `encode` method must have a parameter named `value` and must be annotated by type. These methods can be instance, static or class methods.

The decode function will receive the exact value that is returned by the encode function.

```python
from collections import deque

from cachetoolz.coder import coder

@coder.register
class DequeCoder:
    def encode(self, value: deque):
        return {'iterable': list(value), 'maxlen': value.maxlen}

    def decode(self, value):
        return deque(val['iterable'], val['maxlen'])

@coder.register
class DequeStaticCoder:
    @staticmethod
    def encode(value: deque):
        return {'iterable': list(value), 'maxlen': value.maxlen}

    @staticmethod
    def decode(value):
        return deque(val['iterable'], val['maxlen'])

@coder.register
class DequeClassCoder:
    @classmethod
    def encode(value: deque):
        return {'iterable': list(value), 'maxlen': value.maxlen}

    @classmethod
    def decode(value):
        return deque(val['iterable'], val['maxlen'])
```

When registering a class, it will be instantiated. Therefore, if the class requires any initialization parameters, you can register an instance of it along with the necessary parameters.
```python
from cachetoolz.coder import coder

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
