"""Compact in-memory storage for immutable, already-validated result rows.

Rows are materialized as ordinary dictionaries only while a view uses them.
The original export and its hashes remain the source of truth.
"""

from array import array
from collections.abc import Sequence
from operator import index

_MISSING = object()


def _pack(values):
    """Preserve Python scalar types and float64 precision; never coerce nulls."""
    kinds = {type(value) for value in values}
    if kinds == {float}:
        return array("d", values)
    if kinds == {int}:
        try:
            return array("q", values)
        except OverflowError:
            pass
    return values


class ColumnTable(Sequence):
    """An ordered row sequence backed by columns, with independent dict reads."""

    def __init__(self, rows):
        self._length = len(rows)
        self._keys = tuple(dict.fromkeys(key for row in rows for key in row))
        self._columns = tuple(
            _pack(tuple(row.get(key, _MISSING) for row in rows)) for key in self._keys
        )
        self._sparse = any(len(row) != len(self._keys) for row in rows)

    def __len__(self):
        return self._length

    def _row(self, values):
        if self._sparse:
            return {
                key: value
                for key, value in zip(self._keys, values)
                if value is not _MISSING
            }
        return dict(zip(self._keys, values))

    def __iter__(self):
        # zip's column iterators avoid indexing each array for every row.
        if not self._keys:
            return ({} for _ in range(self._length))
        return (self._row(values) for values in zip(*self._columns))

    def __getitem__(self, position):
        if isinstance(position, slice):
            return tuple(self[i] for i in range(*position.indices(self._length)))
        position = index(position)
        if position < 0:
            position += self._length
        if not 0 <= position < self._length:
            raise IndexError(position)
        return self._row(column[position] for column in self._columns)
