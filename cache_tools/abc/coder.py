"""Coder abstract module."""

from abc import ABC, abstractmethod
from typing import Any


class CoderABC(ABC):
    """Abstract coder."""

    @abstractmethod
    def encode(self, value: Any) -> Any:
        """Encode value.

        Parameters
        ----------
        value
            Value to encode

        Returns
        -------
            Value encoded

        """

    @abstractmethod
    def decode(self, value: Any) -> Any:
        """Decode value.

        Parameters
        ----------
        value
            Value to decode

        Returns
        -------
            Value decoded

        """
