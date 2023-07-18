"""Mongo backend."""

from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any

from ..abc import AsyncBackendABC, BackendABC


class MongoBackend(BackendABC):
    """MongoDB cache."""

    def __init__(self, url: str, database: str = '.cachetoolz'):
        """Initialize the instance.

        Parameters
        ----------
        url
            Mongo url
        database
            Cache database name

        """
        try:
            from pymongo import MongoClient
        except ImportError as exc:
            raise RuntimeError(
                "Install cachetoolz with the 'mongo' extra in order "
                "to use mongo backend."
            ) from exc

        self._client_cls = MongoClient

        self._url = url
        self._database = database

    def __repr__(self):
        """Creates a visual representation of the instance."""
        _cls = self.__class__.__name__
        return f'{_cls}(url="{self._url}", database="{self._database}")'

    @contextmanager
    def _get_database_or_collection(self, collection=None):
        with self._client_cls(self._url) as client:
            if collection:
                yield client[self._database][collection]
            else:
                yield client[self._database]

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

        with self._get_database_or_collection(namespace) as collection:
            doc = collection.find_one({'key': key_hash})

        if doc and doc['expires_at'] >= datetime.now():
            return doc['value']

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
        namespaces
            namespace to cache

        """
        self.logger.debug("Clear 'namespace=%s'", namespace)

        with self._get_database_or_collection() as database:
            database.drop_collection(namespace)


class AsyncMongoBackend(AsyncBackendABC):
    """Async MongoDB cache."""

    def __init__(self, url: str, database: str = '.cachetoolz'):
        """Initialize the instance.

        Parameters
        ----------
        url
            Mongo url
        database
            Cache database name

        """
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
        except ImportError as exc:
            raise RuntimeError(
                "Install cachetoolz with the 'mongo' extra in order "
                "to use mongo backend."
            ) from exc

        self._client_cls = AsyncIOMotorClient

        self._url = url
        self._database = database

    def __repr__(self):
        """Creates a visual representation of the instance."""
        _cls = self.__class__.__name__
        return f'{_cls}(url="{self._url}", database="{self._database}")'

    @contextmanager
    def _get_database_or_collection(self, collection=None):
        client = self._client_cls(self._url)
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
        key
            cache identifier key

        Returns
        -------
            Value cached if exists and not expired else return None

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
        namespaces
            namespace to cache

        """
        self.logger.debug("Clear 'namespace=%s'", namespace)

        with self._get_database_or_collection() as database:
            await database.drop_collection(namespace)
