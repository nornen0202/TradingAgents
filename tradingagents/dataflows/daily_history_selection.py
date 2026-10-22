"""Pin one daily-price source and snapshot within an individual research run."""
from __future__ import annotations

from contextvars import ContextVar, Token
from copy import deepcopy
from dataclasses import dataclass, field
from threading import Lock
from typing import Any

import pandas as pd

from .integrity import safe_symbol
from .vendor_exceptions import VendorMalformedResponseError


@dataclass
class _Selection:
    # Child tool contexts inherit this object, not an independent source value.
    # Their writes are therefore visible to later tools in the same research.
    values: dict[tuple[str, str], dict[str, Any]] = field(default_factory=dict)
    lock: Any = field(default_factory=Lock)


_ACTIVE: ContextVar[_Selection | None] = ContextVar("daily_history_selection", default=None)


def activate_daily_history_selection() -> Token:
    """Start a fresh scope before spawning analyst or tool contexts."""
    return _ACTIVE.set(_Selection())


def reset_daily_history_selection(token: Token) -> None:
    _ACTIVE.reset(token)


def _copy_frame(frame: pd.DataFrame | None) -> pd.DataFrame | None:
    if frame is None:
        return None
    copied = frame.copy(deep=True)
    copied.attrs = deepcopy(frame.attrs)
    return copied


def get_selected_daily_history(symbol: str, end_date: str) -> dict[str, Any] | None:
    """Return an isolated copy of this run's first selected source and frame."""
    selection = _ACTIVE.get()
    if selection is None:
        return None
    key = (safe_symbol(symbol), end_date)
    with selection.lock:
        selected = selection.values.get(key)
        if selected is None:
            return None
        return {"source": selected["source"], "frame": _copy_frame(selected["frame"])}


def select_daily_history(
    symbol: str, end_date: str, source: str, frame: pd.DataFrame | None = None,
) -> None:
    """Select once; concurrent source changes fail without replacing evidence.

    This is intentionally inactive outside a research context. Data cache TTLs
    may expire, but an active research keeps its original selected snapshot.
    """
    selection = _ACTIVE.get()
    if selection is None:
        return
    if not isinstance(source, str) or not source.strip():
        raise VendorMalformedResponseError("Daily history source must be identified")
    if frame is not None and not isinstance(frame, pd.DataFrame):
        raise VendorMalformedResponseError("Daily history snapshot must be a DataFrame")
    key = (safe_symbol(symbol), end_date)
    with selection.lock:
        selected = selection.values.get(key)
        if selected is not None:
            if selected["source"] != source:
                raise VendorMalformedResponseError("Daily history source changed within the same research")
            return
        selection.values[key] = {"source": source, "frame": _copy_frame(frame)}
