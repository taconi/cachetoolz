"""Mongo backend."""

from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Dict

from ..abc import AsyncBackendABC, BackendABC


class MongoBackend(BackendABC):
    """MongoDB cache.

    This backend is used to store caches mongo synchronous.

    Parameters
    ----------
    host : str
        MongoDB URI.
    database : str
        Cache database name.
    kwargs : dict[str, Any]
        Takes the same constructor arguments as
        `pymongo.mongo_client.MongoClient`.

    """

    def __init__(
        self,
        host: str = 'localhost',
        database: str = '.cachetoolz',
        **kwargs: Dict[str, Any],
    ):
        """Initialize the instance."""
        try:
            from pymongo import MongoClient
        except ImportError as exc:
            raise RuntimeError(
                "Install cachetoolz with the 'mongo' extra in order "
                "to use mongo backend."
            ) from exc

        self._client_cls = MongoClient
        self._kwargs = kwargs

        self._kwargs['host'] = host

        self._host = host
        self._database = database

    def __repr__(self):
        """Creates a visual representation of the instance."""
        _cls = self.__class__.__name__
        return f'{_cls}(host="{self._host}", database="{self._database}")'

    @contextmanager
    def _get_database_or_collection(self, collection=None):
        with self._client_cls(**self._kwargs) as client:
            if collection:
                yield client[self._database][collection]
            else:
                yield client[self._database]

    def get(self, key: str) -> Any:
        """Get a value if not expired.

        Parameters
        ----------
        key : str
            cache identifier key.

        Returns
        -------
        with_cache : Any
            Value cached.
        without_cache : None
            If not exists or expired.

        """
        self.logger.debug("Get 'key=%s'", key)

        namespace, key_hash = self._separate_namespace(key)

        with self._get_database_or_collection(namespace) as collection:
            doc = collection.find_one({'key': key_hash})

        if doc and doc['expires_at'] >= datetime.now():
            return doc['value']

        self.logger.debug("No cache to 'key=%s'", key)

    def set(self, key: str, value: str, expires_at: timedelta) -> None:
        """Set a value with expires time.

        Parameters
        ----------
        key : str
            cache identifier key.
        value : str
            value to cache encoded.
        expires_at : datetime.timedelta
            expiry time.

        """
        self.logger.debug(
            "Set 'key=%s', 'value=%s', 'expires_at=%s'",
            key,
            value,
            expires_at,
        )

        namespace, key_hash = self._separate_namespace(key)

        with self._get_database_or_collection(namespace) as collection:
            collection.create_index('expires_at', expireAfterSeconds=0)

            collection.update_one(
                {'key': key_hash},
                {
                    '$set': {
                        'key': key_hash,
                        'value': value,
                        'expires_at': datetime.now() + expires_at,
                    },
                },
                upsert=True,
            )

    def clear(self, namespace: str) -> None:
        """Clear a namespace.

        Parameters
        ----------
        namespaces : str
            namespace to cache.

        """
        self.logger.debug("Clear 'namespace=%s'", namespace)

        with self._get_database_or_collection() as database:
            database.drop_collection(namespace)


class AsyncMongoBackend(AsyncBackendABC):
    """Async MongoDB cache.

    This backend is used to store caches mongo asynchronous.

    Parameters
    ----------
    host : str
        MongoDB URI.
    database : str
        Cache database name.
    kwargs : dict[str, Any]
        Takes the same constructor arguments as
        `pymongo.mongo_client.MongoClient`.

    """

    def __init__(
        self,
        host: str = 'localhost',
        database: str = '.cachetoolz',
        **kwargs: Dict[str, Any],
    ):
        """Initialize the instance."""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
        except ImportError as exc:
            raise RuntimeError(
                "Install cachetoolz with the 'mongo' extra in order "
                "to use mongo backend."
            ) from exc

        self._client_cls = AsyncIOMotorClient
        self._kwargs = kwargs
        self._kwargs['host'] = host

        self._host = host
        self._database = database

    def __repr__(self):
        """Creates a visual representation of the instance."""
        _cls = self.__class__.__name__
        return f'{_cls}(host="{self._host}", database="{self._database}")'

    @contextmanager
    def _get_database_or_collection(self, collection=None):
        client = self._client_cls(**self._kwargs)
        try:
            if collection:
                yield client[self._database][collection]
            else:
                yield client[self._database]
        finally:
            client.close()

    async def get(self, key: str) -> Any:
        """Get a value if not expired.

        Parameters
        ----------
        key : str
            cache identifier key.

        Returns
        -------
        with_cache : Any
            Value cached.
        without_cache : None
            If not exists or expired.

        """
        self.logger.debug("Get 'key=%s'", key)

        namespace, key_hash = self._separate_namespace(key)

        with self._get_database_or_collection(namespace) as collection:
            doc = await collection.find_one({'key': key_hash})

        if doc and doc['expires_at'] >= datetime.now():
            return doc['value']

        self.logger.debug("No cache to 'key=%s'", key)

    async def set(self, key: str, value: str, expires_at: timedelta) -> None:
        """Set a value with expires time.

        Parameters
        ----------
        key : str
            cache identifier key.
        value : str
            value to cache encoded.
        expires_at : datetime.timedelta
            expiry time.

        """
        self.logger.debug(
            "Set 'key=%s', 'value=%s', 'expires_at=%s'",
            key,
            value,
            expires_at,
        )

        namespace, key_hash = self._separate_namespace(key)

        with self._get_database_or_collection(namespace) as collection:
            await collection.create_index('expires_at', expireAfterSeconds=0)

            await collection.update_one(
                {'key': key_hash},
                {
                    '$set': {
                        'key': key_hash,
                        'value': value,
                        'expires_at': datetime.now() + expires_at,
                    },
                },
                upsert=True,
            )

    async def clear(self, namespace: str) -> None:
        """Clear a namespace.

        Parameters
        ----------
        namespaces : str
            namespace to cache.

        """
        self.logger.debug("Clear 'namespace=%s'", namespace)

        with self._get_database_or_collection() as database:
            await database.drop_collection(namespace)
