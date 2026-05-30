from __future__ import annotations

from datetime import datetime, timedelta, timezone

import requests

from tradingagents.dataflows.intraday.us_microstructure_sources import (
    AlpacaUSMicrostructureSource,
    MassiveUSMicrostructureSource,
)


class FakeResponse:
    def __init__(self, payload, *, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")

    def json(self):
        return self._payload


class FakeMassiveSession:
    def __init__(self, now_utc):
        self.now_utc = now_utc

    def get(self, url, *, headers, params, timeout):
        if "/v2/aggs/ticker/AAPL/range/1/day/" in url:
            return FakeResponse({"results": [{"v": 1000 + index} for index in range(20)]})
        if "/v2/last/nbbo/AAPL" in url:
            return FakeResponse({"results": {"p": 99.0, "P": 101.0, "s": 600, "S": 400, "t": _ns(self.now_utc)}})
        if "/v3/trades/AAPL" in url:
            return FakeResponse(
                {
                    "results": [
                        {"p": 101.0, "s": 100, "t": _ns(self.now_utc - timedelta(seconds=20))},
                        {"p": 99.0, "s": 50, "t": _ns(self.now_utc - timedelta(seconds=10))},
                    ]
                }
            )
        return FakeResponse({}, status_code=404)


class FakeAlpacaSession:
    def get(self, url, *, headers, params, timeout):
        feed = params.get("feed")
        if feed == "sip":
            return FakeResponse({}, status_code=403)
        if "quotes/latest" in url and feed == "delayed_sip":
            return FakeResponse({}, status_code=403)
        if "quotes/latest" in url and feed == "iex":
            return FakeResponse({"quote": {"bp": 99.0, "ap": 101.0, "bs": 600, "as": 400, "t": "2026-05-29T14:00:00Z"}})
        if url.endswith("/v2/stocks/bars") and feed == "iex":
            return FakeResponse({"bars": {"AAPL": [{"v": 1000} for _ in range(20)]}})
        if url.endswith("/v2/stocks/trades") and feed == "iex":
            return FakeResponse(
                {
                    "trades": {
                        "AAPL": [
                            {"p": 101.0, "s": 100, "t": "2026-05-29T14:00:01Z"},
                            {"p": 99.0, "s": 50, "t": "2026-05-29T14:00:02Z"},
                        ]
                    }
                }
            )
        return FakeResponse({}, status_code=404)


def test_massive_source_parses_daily_nbbo_and_trade_strength():
    now_utc = datetime(2026, 5, 29, 14, 0, 30, tzinfo=timezone.utc)
    source = MassiveUSMicrostructureSource(api_key="test-key", session=FakeMassiveSession(now_utc))

    supplement = source.fetch("AAPL", now_local=now_utc)

    assert supplement.avg20_daily_volume == 1009.5
    assert supplement.spread_bps is not None
    assert supplement.orderbook_imbalance == 0.2
    assert supplement.execution_strength == 200.0
    assert supplement.pilot_blockers == ()
    assert "massive.last_nbbo" in supplement.raw_source_names


def test_alpaca_source_falls_back_to_iex_and_marks_feed_limited():
    now_utc = datetime(2026, 5, 29, 14, 0, 30, tzinfo=timezone.utc)
    source = AlpacaUSMicrostructureSource(
        key_id="test-key",
        secret_key="test-secret",
        session=FakeAlpacaSession(),
    )

    supplement = source.fetch("AAPL", now_local=now_utc)

    assert supplement.avg20_daily_volume == 1000.0
    assert supplement.spread_bps is not None
    assert supplement.orderbook_imbalance == 0.2
    assert supplement.execution_strength == 200.0
    assert supplement.limited_reason["orderbook"] == "alpaca_feed=iex; non_consolidated"
    assert "orderbook_iex_limited" in supplement.pilot_blockers
    assert "alpaca.iex.latest_quote" in supplement.raw_source_names


def _ns(value: datetime) -> int:
    return int(value.timestamp() * 1_000_000_000)
