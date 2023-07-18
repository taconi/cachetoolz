"""Abstract backend module."""

import logging
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, List

from ..log import get_logger


class BaseBackend:
    """Base abstract backend."""

    def _separate_namespace(self, key: str) -> List[str]:
        """Separete the namespace with key_hash.

        Parameters
        ----------
        key
            Key with namespace and key_hash

        """
        return key.split(':')

    @property
    def logger(self) -> logging.Logger:
        """Get logger."""
        return get_logger()


class BackendABC(BaseBackend, ABC):
    """Abstract backend."""

    @abstractmethod
    def get(self, key: str) -> Any:
        """Get a value if not expired.

        Parameters
        ----------
        key
            Cache identifier key

        Returns
        -------
            Value cached if exists and not expired else return None

        """

    @abstractmethod
    def set(self, key: str, value: str, expires_at: timedelta) -> None:
        """Set a value with expires time."""

    @abstractmethod
    def clear(self, namespace: str) -> None:
        """Clear a namespace.

        Parameters
        ----------
        namespaces
            namespace to cache.

        """


class AsyncBackendABC(BaseBackend, ABC):
    """Abstract async backend."""

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    async def clear(self, namespace: str) -> None:
        """Clear a namespace.

        Parameters
        ----------
        namespaces
            namespace to cache

        """
