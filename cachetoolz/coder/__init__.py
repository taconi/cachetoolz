"""Module interface."""

import json
from inspect import isclass
from typing import Any, Dict, Type, Union

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
        value : Any
            Value to encode.

        Returns
        -------
        encoded : Any
            Value encoded.

        """
        return json.dumps(value, cls=Encoder)

    def decode(self, value: str) -> Dict[str, Any]:
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
        return json.loads(value, cls=Decoder)

    @staticmethod
    def register(serializer: Union[Type[SerializerABC], SerializerABC]):
        """Register a JSON serializer class.

        You can register a class for decoding, it needs to have the ``encode``
        and ``decode`` methods where the ``encode`` method must have a
        parameter called ``value`` and must have the type annotated.
        These methods can be ``instance``, ``@staticmethod``, or
        ``@classmethod``.
        The decode function will receive the exact value that is returned by
        the encode function.

        Parameters
        ----------
        class_ : Union[Type[SerializerABC], SerializerABC]
            Serializer class.

        Examples
        --------
        Class methods
        >>> from collections import deque
        >>> @coder.register
        >>> class DequeSerializer:
        ...     @classmethod
        ...     def encode(cls, value: deque):
        ...         return {'iterable': list(value), 'maxlen': value.maxlen}
        ...
        ...     @classmethod
        ...     def decode(cls, value):
        ...         return deque(val['iterable'], val['maxlen'])
        ...

        Static methods
        >>> from collections import deque
        >>> @coder.register
        >>> class DequeSerializer:
        ...     @staticmethod
        ...     def encode(value: deque):
        ...         return {'iterable': list(value), 'maxlen': value.maxlen}
        ...
        ...     @staticmethod
        ...     def decode(value):
        ...         return deque(val['iterable'], val['maxlen'])
        ...

        Instace methods
        >>> from collections import deque
        >>> @coder.register
        >>> class DequeSerializer:
        ...     def encode(self, value: deque):
        ...         return {'iterable': list(value), 'maxlen': value.maxlen}
        ...
        ...     def decode(self, value):
        ...         return deque(val['iterable'], val['maxlen'])
        ...

        When registering a class, it will be instantiated.
        Therefore, if the class requires any initialization parameters,
        you can register an instance of it along with the necessary parameters.

        >>> from collections import deque
        >>> class DequeCoder:
        ...     def __init__(self, foo):
        ...         self.foo = foo
        ...
        ...      def encode(self, value: deque):
        ...         return {'iterable': list(value), 'maxlen': value.maxlen}
        ...
        ...     def decode(self, value):
        ...         return deque(val['iterable'], val['maxlen'])
        ...
        >>> coder.register(DequeCoder(foo='bar'))

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
