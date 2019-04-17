import itertools
from abc import ABC, abstractmethod
from typing import AbstractSet, Generic, Iterable, Mapping, Optional, Sequence, TypeVar

from basilisp.lang.obj import LispObject as _LispObject, seq_lrepr

T = TypeVar("T")


class IDeref(Generic[T]):
    __slots__ = ()

    @abstractmethod
    def deref(self) -> Optional[T]:
        raise NotImplementedError()


class IBlockingDeref(IDeref[T]):
    __slots__ = ()

    @abstractmethod
    def deref(
        self, timeout: Optional[float] = None, timeout_val: Optional[T] = None
    ) -> Optional[T]:
        raise NotImplementedError()


# Making this interface Generic causes the __repr__ to differ between
# Python 3.6 and 3.6, which affects a few simple test assertions.
# Since there is little benefit to this type being Generic, I'm leaving
# it as is for now.
class IExceptionInfo(Exception):
    __slots__ = ()

    @property
    @abstractmethod
    def data(self) -> "IPersistentMap":
        raise NotImplementedError()


K = TypeVar("K")
V = TypeVar("V")


class IMapEntry(Generic[K, V]):
    __slots__ = ()

    @property
    @abstractmethod
    def key(self) -> K:
        raise NotImplementedError()

    @property
    @abstractmethod
    def value(self) -> V:
        raise NotImplementedError()


class IMeta(ABC):
    __slots__ = ()

    @property
    @abstractmethod
    def meta(self) -> Optional["IPersistentMap"]:
        raise NotImplementedError()

    @abstractmethod
    def with_meta(self, meta: "IPersistentMap") -> "IMeta":
        raise NotImplementedError()


ILispObject = _LispObject


class ISeqable(Iterable[T]):
    __slots__ = ()

    @abstractmethod
    def seq(self) -> "ISeq[T]":
        raise NotImplementedError()


class IPersistentCollection(ISeqable[T]):
    __slots__ = ()

    @abstractmethod
    def cons(self, *elems: T) -> "IPersistentCollection[T]":
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def empty() -> "IPersistentCollection[T]":
        raise NotImplementedError()


class IAssociative(Mapping[K, V], IPersistentCollection[IMapEntry[K, V]]):
    __slots__ = ()

    @abstractmethod
    def assoc(self, *kvs) -> "IAssociative[K, V]":
        raise NotImplementedError()

    @abstractmethod
    def contains(self, k: K) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def entry(self, k: K, default: Optional[V] = None) -> Optional[V]:
        raise NotImplementedError()


class IPersistentStack(IPersistentCollection[T]):
    __slots__ = ()

    @abstractmethod
    def peek(self) -> Optional[T]:
        raise NotImplementedError()

    @abstractmethod
    def pop(self) -> "IPersistentStack[T]":
        raise NotImplementedError()


class IPersistentList(IPersistentStack[T]):
    __slots__ = ()


class IPersistentMap(IAssociative[K, V]):
    __slots__ = ()

    @abstractmethod
    def dissoc(self, *ks: K) -> "IPersistentMap[K, V]":
        raise NotImplementedError()


class IPersistentSet(AbstractSet[T], IPersistentCollection[T]):
    __slots__ = ()

    @abstractmethod
    def disj(self, *elems: T) -> "IPersistentSet[T]":
        raise NotImplementedError()


# MyPy has a lot of trouble dealing with the fact that Vectors are
# considered as mapping types (from int -> T) and more traditional
# sequential collections since the Python supertypes signatures conflict.
# Below, we override the supertype signatures to select the signature
# we specifically want to appear, but MyPy still complains. For now,
# we will simply silence MyPy.
class IPersistentVector(  # type: ignore
    Sequence[T], IAssociative[int, T], IPersistentStack[T]
):
    __slots__ = ()

    @abstractmethod
    def cons(self, *elems: T) -> "IPersistentVector[T]":  # type: ignore
        raise NotImplementedError()

    @abstractmethod
    def seq(self) -> "ISeq[T]":  # type: ignore
        raise NotImplementedError()


class IRecord(ABC):
    __slots__ = ()


class ISeq(ILispObject, ISeqable[T]):
    __slots__ = ()

    @property
    @abstractmethod
    def is_empty(self) -> bool:
        raise NotImplementedError()

    @property
    @abstractmethod
    def first(self) -> Optional[T]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def rest(self) -> "ISeq[T]":
        raise NotImplementedError()

    @abstractmethod
    def cons(self, elem: T) -> "ISeq[T]":
        raise NotImplementedError()

    def seq(self) -> "ISeq[T]":
        return self

    def _lrepr(self, **kwargs):
        return seq_lrepr(iter(self), "(", ")", **kwargs)

    def __eq__(self, other):
        sentinel = object()
        for e1, e2 in itertools.zip_longest(self, other, fillvalue=sentinel):
            if bool(e1 is sentinel) or bool(e2 is sentinel):
                return False
            if e1 != e2:
                return False
        return True

    def __iter__(self):
        o = self
        while o:
            yield o.first
            o = o.rest


class IType(ABC):
    __slots__ = ()