"""Module interface."""

import json
from inspect import isclass
from typing import Any, Dict

from ..abc import CoderABC, SerializerABC
from ..exceptions import RegistryError
from ..utils import decoder_name
from .decoder import Decoder
from .decoder import register as decoder_register
from .encoder import Encoder
from .encoder import register as encoder_register


class Coder(CoderABC):
    """Coder class."""

    def encode(self, value: Any) -> str:
        """Encode value.

        Parameters
        ----------
        value
            Value to encode

        Returns
        -------
            Value encoded

        """
        return json.dumps(value, cls=Encoder)

    def decode(self, value: str) -> Dict[str, Any]:
        """Decode value.

        Parameters
        ----------
        value
            Value to decode

        Returns
        -------
            Value decoded

        """
        return json.loads(value, cls=Decoder)

    @staticmethod
    def register(serializer: SerializerABC):
        """Register a JSON serializer class.

        Parameters:
        ----------
        class_
            Serializer class

        Examples
        --------
        >>> from collections import deque
        >>> @coder.register
        >>> class DequeSerializer:
        ...     def encode(self, value: deque):
        ...         return {'iterable': list(value), 'maxlen': value.maxlen}
        ...
        ...     def decode(self, value):
        ...         return deque(val['iterable'], val['maxlen'])
        ...

        """
        if not hasattr(serializer, 'encode') or not hasattr(
            serializer, 'decode'
        ):
            raise RegistryError(
                'Sereliazador is not valid, the class must have implemented '
                'the `encode(value: type)` and `decode(value)` methods'
            )

        instance = serializer() if isclass(serializer) else serializer

        name = decoder_name(instance).replace('serializer', '').strip('_')

        encoder_register(name)(instance.encode)
        decoder_register(name)(instance.decode)

        return serializer


coder = Coder()
