"""Preserve host-observed research quotes independently of execution refreshes."""
from copy import deepcopy
from datetime import datetime, timezone
import json
import math
import threading

from langchain_core.callbacks import BaseCallbackHandler


class ResearchObservationRecorder(BaseCallbackHandler):
    """Keep a bounded, allowlisted receipt even when graph messages are cleared."""

    def __init__(self, ticker: str):
        self.ticker = ticker
        self._lock = threading.Lock()
        self._calls = set()
        self._receipt = {"status": "NOT_COLLECTED", "ticker": ticker}

    def on_tool_start(self, serialized, input_str, *, run_id, **kwargs):
        if (serialized or {}).get("name") == "get_intraday_snapshot":
            with self._lock:
                self._calls.add(run_id)

    def on_tool_end(self, output, *, run_id, **kwargs):
        with self._lock:
            if run_id not in self._calls:
                return
            self._calls.remove(run_id)
            receipt = {"ticker": self.ticker, "status": "UNAVAILABLE",
                       "observed_at": datetime.now(timezone.utc).isoformat(),
                       "tool": "get_intraday_snapshot", "execution_authorized": False}
            try:
                payload = json.loads(getattr(output, "content", output))
                snapshot = payload.get("snapshot") or {}
                if payload.get("ok") is True:
                    asof = snapshot.get("asof")
                    stamp = datetime.fromisoformat(str(asof).replace("Z", "+00:00"))
                    price = snapshot.get("last_price")
                    if (payload.get("symbol") != self.ticker or snapshot.get("ticker") != self.ticker
                            or stamp.tzinfo is None or stamp.utcoffset() is None
                            or stamp > datetime.now(timezone.utc)
                            or isinstance(price, bool) or not isinstance(price, (int, float))
                            or not math.isfinite(price) or price <= 0):
                        raise ValueError("Invalid quote identity, clock or price")
                    receipt.update(status="AVAILABLE", market_data_asof=asof, last_price=price)
                    for key in ("provider", "market_session", "execution_data_quality"):
                        value = snapshot.get(key)
                        if isinstance(value, str) and len(value) <= 80:
                            receipt[key] = value
                    for key in ("session_vwap", "relative_volume", "quote_delay_seconds"):
                        value = snapshot.get(key)
                        if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
                            receipt[key] = value
            except (ValueError, TypeError, AttributeError):
                receipt["status"] = "INVALID"
            self._receipt = receipt

    def on_tool_error(self, error, *, run_id, **kwargs):
        self.on_tool_end('{"ok":false}', run_id=run_id)

    def receipt(self):
        with self._lock:
            return deepcopy(self._receipt)
