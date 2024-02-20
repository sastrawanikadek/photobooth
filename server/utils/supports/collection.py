from functools import reduce
from typing import Callable, Generic, Iterable, Iterator, TypeVar, overload

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from typing_extensions import Self

_T = TypeVar("_T")
_RT = TypeVar("_RT")


class Collection(Generic[_T]):
    def __init__(self, iterable: Iterable[_T]) -> None:
        """Initialize the collection."""
        self._iterable = list(iterable)

    @overload
    def first(self) -> _T | None:
        """Return the first item in the collection."""

    @overload
    def first(
        self, filter: Callable[[tuple[_T, Self, int]], bool], default: _T | None = None
    ) -> _T | None:
        """Return the first item in the collection that matches the filter."""

    def first(
        self,
        filter: Callable[[tuple[_T, Self, int]], bool] | None = None,
        default: _T | None = None,
    ) -> _T | None:
        """Return the first item in the collection or the first item that matches the filter."""
        if filter is None:
            return self._iterable[0] if len(self._iterable) > 0 else None

        return next(self.filter(filter), default)

    @overload
    def last(self) -> _T | None:
        """Return the last item in the collection."""

    @overload
    def last(
        self, filter: Callable[[tuple[_T, Self, int]], bool], default: _T | None = None
    ) -> _T | None:
        """Return the last item in the collection that matches the filter."""

    def last(
        self,
        filter: Callable[[tuple[_T, Self, int]], bool] | None = None,
        default: _T | None = None,
    ) -> _T | None:
        """Return the last item in the collection or the last item that matches the filter."""
        if filter is None:
            return self._iterable[-1] if len(self._iterable) > 0 else None

        return next(reversed(self.filter(filter)), default)

    def filter(
        self, callback: Callable[[tuple[_T, Self, int]], bool]
    ) -> "Collection[_T]":
        """Return the items in the collection that match the filter."""
        return Collection(
            [
                item
                for index, item in enumerate(self._iterable)
                if callback((item, self, index))
            ]
        )

    def map(self, callback: Callable[[tuple[_T, Self, int]], _RT]) -> "Collection[_RT]":
        """Return the items in the collection after applying the callback."""
        return Collection(
            [callback((item, self, index)) for index, item in enumerate(self._iterable)]
        )

    def reduce(
        self, callback: Callable[[_RT, tuple[_T, Self, int]], _RT], initial: _RT
    ) -> _RT:
        """Return the result of reducing the collection with the callback."""
        return reduce(
            lambda acc, item: callback(acc, (item[1], self, item[0])),
            enumerate(self._iterable),
            initial,
        )

    def add(self, item: _T) -> None:
        """Add the item to the collection."""
        self._iterable.append(item)

    def remove(self, item: _T) -> None:
        """Remove the item from the collection."""
        self._iterable.remove(item)

    def clear(self) -> None:
        """Clear the collection."""
        self._iterable.clear()

    def is_empty(self) -> bool:
        """Return whether the collection is empty."""
        return len(self._iterable) == 0

    def is_not_empty(self) -> bool:
        """Return whether the collection is not empty."""
        return len(self._iterable) > 0

    def to_list(self) -> list[_T]:
        """Return the collection as a list."""
        return self._iterable

    def __iter__(self) -> Iterator[_T]:
        """Return the iterator."""
        return iter(self._iterable)

    def __next__(self) -> _T:
        """Return the next item in the collection."""
        return next(iter(self))

    def __len__(self) -> int:
        """Return the length of the collection."""
        return len(self._iterable)

    def __getitem__(self, index: int) -> _T:
        """Return the item at the given index."""
        return self._iterable[index]

    def __contains__(self, item: _T) -> bool:
        """Return whether the item is in the collection."""
        return item in self._iterable

    def __reversed__(self) -> Iterator[_T]:
        """Return the reversed iterator."""
        return reversed(self._iterable)

    def __eq__(self, other: object) -> bool:
        """Return whether the collection is equal to the other object."""
        return isinstance(other, Collection) and self._iterable == other._iterable

    def __ne__(self, other: object) -> bool:
        """Return whether the collection is not equal to the other object."""
        return not other == self

    def __str__(self) -> str:
        """Return the string representation of the collection."""
        return str(self._iterable)

    def __repr__(self) -> str:
        """Return the string representation of the collection."""
        return repr(self._iterable)

    def __add__(self, other: "Collection[_T]") -> "Collection[_T]":
        """Return the collection with the other collection added."""
        return Collection(self._iterable + other.to_list())

    def __sub__(self, other: "Collection[_T]") -> "Collection[_T]":
        """Return the collection with the other collection removed."""
        return Collection(
            [item for item in self._iterable if item not in other.to_list()]
        )

    def __and__(self, other: "Collection[_T]") -> "Collection[_T]":
        """Return the intersection of the collection and the other collection."""
        return Collection([item for item in self._iterable if item in other.to_list()])

    def __or__(self, other: "Collection[_T]") -> "Collection[_T]":
        """Return the union of the collection and the other collection."""
        return Collection(self._iterable + other.to_list())

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _: object, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(list, handler(list))
