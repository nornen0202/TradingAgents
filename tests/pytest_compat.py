from __future__ import annotations

from math import isclose
from typing import Any


class _Approx:
    def __init__(self, expected: Any, *, abs: float | None = None, rel: float | None = None) -> None:
        self.expected = expected
        self.abs = 1e-12 if abs is None else float(abs)
        self.rel = 1e-6 if rel is None else float(rel)

    def __eq__(self, actual: Any) -> bool:
        return self._matches(actual, self.expected)

    def _matches(self, actual: Any, expected: Any) -> bool:
        if isinstance(expected, dict) and isinstance(actual, dict):
            return expected.keys() == actual.keys() and all(self._matches(actual[key], expected[key]) for key in expected)
        try:
            return isclose(float(actual), float(expected), abs_tol=self.abs, rel_tol=self.rel)
        except (TypeError, ValueError):
            return actual == expected


class _PytestCompat:
    @staticmethod
    def approx(expected: Any, *, abs: float | None = None, rel: float | None = None) -> _Approx:
        return _Approx(expected, abs=abs, rel=rel)


pytest = _PytestCompat()
