"""In backend module."""

from asyncio import Lock
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from functools import partial
from typing import Any, DefaultDict, Dict, TypeVar

from funcy import walk_values

from ..abc import AsyncBackendABC, BackendABC


@dataclass
class Cached:
    """Cached object."""

    value: str
    expires_at: datetime


Store: TypeVar = DefaultDict[str, Dict[str, Cached]]


class InMemory(BackendABC):
    """In memory backend."""

    def __init__(self):
        """Initialize the instance."""
        self._store: Store = defaultdict(lambda: {})

    def __repr__(self):
        """Creates a visual representation of the instance."""
        store = walk_values(
            partial(walk_values, asdict), dict(self._store.items())
        )
        return f'InMemory({store})'

    def get(self, key: str) -> Any:
        """Get a value if not expired.

        Parameters
        ----------
        key
            cache identifier key

        Returns
        -------
            Value cached if exists and not expired else return None

        """
        self.logger.debug("Get 'key=%s'", key)

        namespace, key_hash = self._separate_namespace(key)

        if cached := self._store[namespace].get(key_hash):
            if cached.expires_at >= datetime.now():
                return cached.value

            del self._store[namespace][key_hash]

        self.logger.debug("No cache to 'key=%s'", key)

    def set(self, key: str, value: str, expires_at: timedelta) -> None:
        """Set a value with expires time.

        Parameters
        ----------
        key
            cache identifier key
        value
            value to cach
        expires_at
            expiry time

        """
        self.logger.debug(
            "Set 'key=%s', 'value=%s', 'expires_at=%s'",
            key,
            value,
            expires_at,
        )

        namespace, key_hash = self._separate_namespace(key)

        self._store[namespace][key_hash] = Cached(
            value=value,
            expires_at=datetime.now() + expires_at,
        )

    def clear(self, namespace: str) -> None:
        """Clear a namespace.

        Parameters
        ----------
        namespaces
            namespace to cache

        """
        self.logger.debug("Clear 'namespace=%s'", namespace)

        self._store.pop(namespace)


class AsyncInMemory(AsyncBackendABC):
    """Async in memory backend."""

    def __init__(self):
        """Initialize the instance."""
        self._store: Store = defaultdict(lambda: {})
        self._lock: Lock = Lock()

    def __repr__(self):
        """Creates a visual representation of the instance."""
        store = walk_values(
            partial(walk_values, asdict), dict(self._store.items())
        )
        return f'AsyncInMemory({store})'

    async def get(self, key: str) -> None:
        """Get a value if not expired.

        Parameters
        ----------
        key
            cache identifier key

        Returns
        -------
            Value cached if exists and not expired else return None

        """
        self.logger.debug("Get 'key=%s'", key)

        namespace, key_hash = self._separate_namespace(key)

        async with self._lock:
            if cached := self._store[namespace].get(key_hash):
                if cached.expires_at >= datetime.now():
                    return cached.value
                del self._store[namespace][key_hash]

        self.logger.debug("No cache to 'key=%s'", key)

    async def set(self, key: str, value: str, expires_at: timedelta) -> None:
        """Set a value with expires time.

        Parameters
        ----------
        key
            cache identifier key
        value
            value to cach
        expires_at
            expiry time

        """
        self.logger.debug(
            "Set 'key=%s', 'value=%s', 'expires_at=%s'",
            key,
            value,
            expires_at,
        )

        namespace, key_hash = self._separate_namespace(key)

        async with self._lock:
            self._store[namespace][key_hash] = Cached(
                value=value,
                expires_at=datetime.now() + expires_at,
            )

    async def clear(self, namespace: str) -> None:
        """Clear a namespace.

        Parameters
        ----------
        namespaces
            namespace to cache

        """
        self.logger.debug("Clear 'namespace=%s'", namespace)

        async with self._lock:
            self._store.pop(namespace, None)
