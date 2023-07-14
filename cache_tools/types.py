"""Types implemetations."""

from typing import (
    Any,
    Awaitable,
    Callable,
    Concatenate,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
)

T = TypeVar('T')
P = ParamSpec('P')

Func: TypeAlias = Callable[P, Awaitable[T] | T]
Decorator: TypeAlias = Callable[[Func], Func]
KeyGenerator: TypeAlias = Callable[Concatenate[bool, Func, P], str]
Manipulator: TypeAlias = Callable[Concatenate[Any, Func, P], Awaitable[T] | T]
Encoder: TypeAlias = Callable[[Any], Any]
Decoder: TypeAlias = Callable[[Any], Any]


class Encoded(TypedDict):
    """Encoded type."""

    __val: Any
    __decoder: str
