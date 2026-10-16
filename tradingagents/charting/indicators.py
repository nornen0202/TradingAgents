"""Deterministic descriptive indicators; these never authorize an order."""
from __future__ import annotations

from .bars import instant, validate_bars


def anchored_vwap(records, *, anchor, analysis_as_of, session_id=None):
    start = instant(anchor)
    cutoff = instant(analysis_as_of)
    if start is None or cutoff is None or start > cutoff:
        raise ValueError("anchor and analysis_as_of must be ordered aware timestamps")
    bars = validate_bars(records, analysis_as_of=cutoff)["bars"]
    bars = [bar for bar in bars if instant(bar["timestamp"]) >= start
            and (session_id is None or bar["session_id"] == session_id)]
    if len({bar["interval"] for bar in bars}) > 1:
        raise ValueError("Do not double count overlapping timeframes")
    numerator = denominator = 0.0
    series = []
    for bar in bars:
        numerator += ((bar["high"] + bar["low"] + bar["close"]) / 3) * bar["volume"]
        denominator += bar["volume"]
        series.append({"timestamp": bar["timestamp"], "value": numerator / denominator if denominator else None})
    return {"series": series, "anchor": start.isoformat(), "session_id": session_id,
            "method": "typical_price_times_bar_volume", "approximate": True,
            "input_interval": bars[0]["interval"] if bars else None}


def volume_profile(records, *, analysis_as_of, bins=24, value_area=0.70, session_id=None):
    if isinstance(bins, bool) or not isinstance(bins, int) or not 2 <= bins <= 200:
        raise ValueError("bins must be between 2 and 200")
    if isinstance(value_area, bool) or not 0 < value_area <= 1:
        raise ValueError("value_area must be in (0,1]")
    bars = validate_bars(records, analysis_as_of=analysis_as_of)["bars"]
    bars = [bar for bar in bars if session_id is None or bar["session_id"] == session_id]
    if len({bar["interval"] for bar in bars}) > 1:
        raise ValueError("Do not double count overlapping timeframes")
    result = {"bins": [], "poc": None, "value_area_low": None, "value_area_high": None,
              "total_volume": 0, "method": "uniform_volume_over_bar_high_low", "approximate": True,
              "session_id": session_id, "input_interval": bars[0]["interval"] if bars else None,
              "limitation": "OHLCV approximation; no actual trade-at-price, footprint or order book reconstruction"}
    if not bars:
        return result
    low, high = min(bar["low"] for bar in bars), max(bar["high"] for bar in bars)
    if low == high:
        high = low + max(low * 1e-9, 1e-9)
    step = (high - low) / bins
    volumes = [0.0] * bins
    for bar in bars:
        width = bar["high"] - bar["low"]
        if width == 0:
            index = min(bins - 1, max(0, int((bar["close"] - low) / step)))
            volumes[index] += bar["volume"]
        else:
            for i in range(bins):
                overlap = max(0, min(bar["high"], low + (i + 1) * step) - max(bar["low"], low + i * step))
                volumes[i] += bar["volume"] * overlap / width
    total = sum(volumes)
    result["bins"] = [{"low": low + i * step, "high": low + (i + 1) * step, "volume": v}
                      for i, v in enumerate(volumes)]
    result["total_volume"] = total
    if total <= 0:
        return result
    poc = max(range(bins), key=lambda i: (volumes[i], -i))
    left = right = poc
    accumulated = volumes[poc]
    while accumulated < total * value_area and (left > 0 or right < bins - 1):
        if right < bins - 1 and (left == 0 or volumes[right + 1] > volumes[left - 1]):
            right += 1
            accumulated += volumes[right]
        else:
            left -= 1
            accumulated += volumes[left]
    result.update(poc=low + (poc + 0.5) * step,
                  value_area_low=low + left * step, value_area_high=low + (right + 1) * step)
    return result
