"""Redis memory."""

from datetime import timedelta
from typing import Any, Dict

from ..abc import AsyncBackendABC, BackendABC


class RedisBackend(BackendABC):
    """Redis cache."""

    def __init__(self, url: str, **kwargs: Dict[str, Any]):
        """Initialize the instance.

        The ``decode_responses`` parameter will always be True
        as the result needs to be returned as a string.

        Parameters
        ----------
        url
            Redis url
        kwargs
            Takes the same constructor arguments as
            :method:`~redis.client.Redis.from_url`

        """
        try:
            from redis import Redis
        except ImportError as exc:
            raise RuntimeError(
                "Install cachetoolz with the 'redis' extra in order "
                "to use redis backend."
            ) from exc

        self._url = url
        kwargs['decode_responses'] = True
        self._backend = Redis.from_url(self._url, **kwargs)

    def __repr__(self):
        """Creates a visual representation of the instance."""
        return f'{self.__class__.__name__}(url="{self._url}")'

    def get(self, key: str) -> Any:
        """Get a value if not expired.

        Parameters
        ----------
        key
            cache identifier key.

        Returns
        -------
            Value cached if exists and not expired else return None

        """
        self.logger.debug("Get 'key=%s'", key)

        if result := self._backend.get(key):
            return result

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

        self._backend.set(key, str(value), ex=expires_at)

    def clear(self, namespace: str) -> None:
        """Clear a namespace.

        Parameters
        ----------
        namespaces
            namespace to cache.

        """
        self.logger.debug("Clear 'namespace=%s'", namespace)

        for key in self._backend.scan_iter(f'{namespace}:*'):
            self._backend.delete(key)


class AsyncRedisBackend(AsyncBackendABC):
    """Async Redis backend."""

    def __init__(self, url: str, **kwargs):
        """Initialize the instance.

        The ``decode_responses`` parameter will always be True
        as the result needs to be returned as a string.

        Parameters
        ----------
        url
            Redis url
        kwargs
            Takes the same constructor arguments as
            :method:`~redis.asyncio. client.Redis.from_url`

        """
        try:
            from redis.asyncio import Redis
        except ImportError as exc:
            raise RuntimeError(
                "Install cachetoolz with the 'redis' extra in order "
                "to use redis backend."
            ) from exc

        self._url = url
        kwargs['decode_responses'] = True
        self._backend = Redis.from_url(self._url, **kwargs)

    def __repr__(self):
        """Creates a visual representation of the instance."""
        return f'{self.__class__.__name__}(url="{self._url}")'

    async def get(self, key: str) -> Any:
        """Get a value if not expired.

        Parameters
        -----------
        key
            cache identifier key

        Returns
        -------
            Value cached if exists and not expired else return None

        """
        self.logger.debug("Get 'key=%s'", key)

        if result := await self._backend.get(key):
            return result

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

        await self._backend.set(key, str(value), ex=expires_at)

    async def clear(self, namespace: str) -> None:
        """Clear a namespace.

        Parameters
        ----------
        namespaces
            namespace to cache.

        """
        self.logger.debug("Clear 'namespace=%s'", namespace)

        async for key in self._backend.scan_iter(f'{namespace}:*'):
            await self._backend.delete(key)
