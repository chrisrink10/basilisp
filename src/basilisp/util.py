import functools
import inspect
import os.path
from typing import Optional, Callable, TypeVar, Generic

from functional import seq
from functional.pipeline import Sequence

from basilisp.lang.util import lrepr


def trace(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        calling_frame = inspect.getframeinfo(inspect.stack()[1][0])
        filename = os.path.relpath(calling_frame.filename)
        lineno = calling_frame.lineno
        strargs = ', '.join(map(repr, args))
        strkwargs = ', '.join(
            [f'{lrepr(k)}={lrepr(v)}' for k, v in kwargs.items()])

        try:
            ret = f(*args, **kwargs)
            print(
                f"[{filename}:{lineno}] {f.__name__}({strargs}, {strkwargs}) => {ret}"
            )
            return ret
        except Exception as e:
            print(
                f"[{filename}:{lineno}] {f.__name__}({strargs}, {strkwargs}) => raised {type(e)}"
            )
            raise e

    return wrapper


T = TypeVar('T')
U = TypeVar('U')


class Maybe(Generic[T]):
    __slots__ = ('_inner', )

    def __init__(self, inner: Optional[T]) -> None:
        self._inner = inner  # pylint:disable=assigning-non-slot

    def __eq__(self, other):
        if isinstance(other, Maybe):
            return self._inner == other.value
        return self._inner == other

    def __repr__(self):
        return repr(self._inner)

    def __str__(self):
        return str(self._inner)

    def or_else(self, else_fn: Callable[[], T]) -> T:
        if self._inner is None:
            return else_fn()
        return self._inner

    def or_else_get(self, else_v: T) -> T:
        if self._inner is None:
            return else_v
        return self._inner

    def or_else_raise(self, raise_fn: Callable[[], Exception]) -> T:
        if self._inner is None:
            raise raise_fn()
        return self._inner

    def map(self, f: Callable[[T], U]) -> "Maybe[U]":
        if self._inner is None:
            return Maybe(None)
        return Maybe(f(self._inner))

    @property
    def value(self) -> Optional[T]:
        return self._inner

    def stream(self) -> Sequence:
        if self._inner is None:
            return seq([])
        return seq([self._inner])

    @property
    def is_present(self) -> bool:
        return self._inner is not None