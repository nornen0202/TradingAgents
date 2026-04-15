import json
from types import SimpleNamespace

from tradingagents.agents.utils.core_stock_tools import get_intraday_snapshot


def test_intraday_snapshot_tool_returns_json_payload(monkeypatch):
    def _fake_fetch(symbol: str, interval: str):
        assert symbol == "000660.KS"
        assert interval == "5m"
        return SimpleNamespace(
            to_dict=lambda: {
                "ticker": "000660.KS",
                "as_of": "2026-04-15T12:00:00+09:00",
                "last_price": 1103000.0,
                "volume": 1234567,
            }
        )

    monkeypatch.setattr(
        "tradingagents.agents.utils.core_stock_tools.fetch_intraday_market_snapshot",
        _fake_fetch,
    )

    payload = get_intraday_snapshot.func("000660.KS", "5m")
    data = json.loads(payload)
    assert data["ticker"] == "000660.KS"
    assert data["volume"] == 1234567


def test_intraday_snapshot_tool_returns_readable_error(monkeypatch):
    def _raise(*_args, **_kwargs):
        raise RuntimeError("no intraday data available")

    monkeypatch.setattr(
        "tradingagents.agents.utils.core_stock_tools.fetch_intraday_market_snapshot",
        _raise,
    )

    payload = get_intraday_snapshot.func("005930.KS", "5m")
    assert "Intraday snapshot unavailable for 005930.KS" in payload
