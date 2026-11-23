"""Explicit currency and price-basis evidence for recommendation measurement."""

from dataclasses import dataclass
import math
import re
from typing import Any, Mapping

from .lifecycle import timestamp


@dataclass(frozen=True)
class PriceReference:
    price: float
    currency: str
    basis: str
    source: str
    observed_at: str

    @classmethod
    def read(cls, value: Any) -> "PriceReference | None":
        if not isinstance(value, Mapping):
            return None
        price, currency, basis, source, observed = (
            value.get(key) for key in ("price", "currency", "basis", "source", "observed_at")
        )
        if (type(price) not in (int, float) or not math.isfinite(price) or price <= 0
                or not isinstance(currency, str) or not re.fullmatch("[A-Z]{3}", currency)
                or basis not in ("unadjusted", "split_adjusted", "total_return")
                or not isinstance(source, str) or not source.strip()):
            return None
        try:
            timestamp(observed)
        except ValueError:
            return None
        return cls(price, currency, basis, source, observed)


def series_terms(payload: Any) -> tuple[str, str] | None:
    """Require proof carried by each retained bar, never a ticker convention."""
    rows = payload.get("prices") if isinstance(payload, Mapping) else payload
    if not isinstance(rows, list) or not rows:
        return None
    terms = set()
    for row in rows:
        if not isinstance(row, Mapping):
            return None
        currency, basis, source = (row.get(key) for key in ("currency", "basis", "source"))
        if (not isinstance(currency, str) or not re.fullmatch("[A-Z]{3}", currency)
                or basis not in ("unadjusted", "split_adjusted", "total_return")
                or not isinstance(source, str) or not source.strip()):
            return None
        if basis == "unadjusted" and (row.get("split_ratio") != 1 or row.get("dividend") != 0):
            # An unadjusted path requires a verified no-action window. A split
            # or distribution requires a consistently adjusted price series.
            return None
        terms.add((currency, basis))
    return next(iter(terms)) if len(terms) == 1 else None
