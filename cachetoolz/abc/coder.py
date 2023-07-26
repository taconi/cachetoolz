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
        value : Any
            Value to encode.

        Returns
        -------
        encode : Any
            Value encoded.

        """

    @abstractmethod
    def decode(self, value: Any) -> Any:
        """Decode value.

        Parameters
        ----------
        value : Any
            Value to decode.

        Returns
        -------
        decoded : Any
            Value decoded.

        """
