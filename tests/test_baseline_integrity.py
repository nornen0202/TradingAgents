from datetime import datetime, timezone
import json
import os
import time
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from tradingagents.dataflows import alpha_vantage_fundamentals as av
from tradingagents.dataflows.alpha_vantage_news import fetch_company_news_alpha_vantage
from tradingagents.dataflows.integrity import safe_symbol, validate_daily_bars
from tradingagents.dataflows.news_models import NewsItem, filter_news_items_by_date, normalize_datetime
from tradingagents.dataflows.vendor_exceptions import VendorInputError, VendorMalformedResponseError
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.agents.trader.trader import create_trader
from tradingagents.dataflows import stockstats_utils


def test_json_financials_filter_publication_dates_without_mutation():
    payload = {"annualReports": [
        {"fiscalDateEnding": "2025-12-31", "reportedDate": "2026-02-01"},
        {"fiscalDateEnding": "2025-12-31", "reportedDate": "2026-04-01"},
        {"fiscalDateEnding": "2026-12-31"},
        {"fiscalDateEnding": "2024-12-31"},
    ]}
    with patch.object(av, "get_config", return_value={"point_in_time_strict": True}):
        filtered = json.loads(av._filter_reports_by_date(json.dumps(payload), "2026-03-01"))
    assert len(filtered["annualReports"]) == 1
    assert len(payload["annualReports"]) == 4


def test_malformed_financials_are_not_reported_as_success():
    with pytest.raises(VendorMalformedResponseError):
        av._filter_reports_by_date("bad json", "2026-03-01")


def test_news_window_excludes_unknown_and_next_day_midnight():
    items = [NewsItem("a", "test", None),
             NewsItem("b", "test", datetime(2026, 3, 1, 23, 59, tzinfo=timezone.utc)),
             NewsItem("c", "test", datetime(2026, 3, 2, tzinfo=timezone.utc))]
    actual = filter_news_items_by_date(items, start_date=datetime(2026, 3, 1), end_date=datetime(2026, 3, 2))
    assert [item.title for item in actual] == ["b"]
    assert normalize_datetime("2026-03-01T12:00:00").tzinfo is not None


def test_alpha_news_filters_vendor_results_locally():
    feed = {"feed": [{"title": "valid", "time_published": "20260301T235959"},
                     {"title": "future", "time_published": "20260302T000000"},
                     {"title": "unknown"}]}
    with patch("tradingagents.dataflows.alpha_vantage_news._make_api_request", return_value=json.dumps(feed)) as call:
        items = fetch_company_news_alpha_vantage("AAPL", "2026-03-01", "2026-03-01")
    assert [item.title for item in items] == ["valid"]
    assert call.call_args.args[1]["time_to"] == "20260302T0000"


def test_latest_missing_close_is_not_replaced_by_previous_day():
    frame = pd.DataFrame({"Date": ["2026-03-01", "2026-03-02"], "Close": [100, float("nan")]})
    with pytest.raises(VendorMalformedResponseError, match="Latest"):
        validate_daily_bars(frame, "2026-03-02")
    assert len(validate_daily_bars(frame, "2026-03-01")) == 1


def test_active_price_cache_is_shared_but_refreshed_when_old(tmp_path):
    today = pd.Timestamp.today().normalize()
    frame = pd.DataFrame({"Close": [100]}, index=pd.DatetimeIndex([today], name="Date"))
    with patch.object(stockstats_utils, "get_config", return_value={"data_cache_dir": str(tmp_path)}), patch.object(stockstats_utils.yf, "download", return_value=frame) as download:
        stockstats_utils.load_ohlcv("AAPL", today.date().isoformat())
        stockstats_utils.load_ohlcv("AAPL", today.date().isoformat())
        assert download.call_count == 1
        cache = next(tmp_path.glob("*.csv"))
        old = time.time() - 600
        os.utime(cache, (old, old))
        stockstats_utils.load_ohlcv("AAPL", today.date().isoformat())
        assert download.call_count == 2


def test_dst_dates_preserve_exchange_day_and_do_not_backfill():
    frame = pd.DataFrame({"Date": ["2026-03-06T00:00:00-05:00", "2026-03-09T00:00:00-04:00", "2026-03-10T00:00:00+09:00"],
                          "Close": [100, 101, 102], "Volume": [None, 12, 20]})
    result = validate_daily_bars(frame, "2026-03-10")
    assert result.iloc[-1]["Date"] == pd.Timestamp("2026-03-10")
    assert pd.isna(result.iloc[0]["Volume"])


@pytest.mark.parametrize("symbol", ["../secret", "A/B", "C:\\secret", "..", "AAPL\n/secret"])
def test_ticker_paths_rejected(symbol):
    with pytest.raises(VendorInputError):
        safe_symbol(symbol)


def test_persistent_memory_excludes_unknown_and_future_outcomes(tmp_path):
    config = {"memory_dir": str(tmp_path)}
    memory = FinancialSituationMemory("test", config)
    memory.add_situations([
        ("earnings bullish", "known", {"outcome_known_at": "2026-03-01"}),
        ("earnings bullish", "future", {"outcome_known_at": "2026-04-01"}),
        ("earnings bullish", "undated"),
    ])
    loaded = FinancialSituationMemory("test", config)
    assert [item["recommendation"] for item in loaded.get_memories("earnings", as_of="2026-03-02")] == ["known"]
    assert loaded.get_memories("earnings", n_matches=0) == []


def test_empty_token_memory_does_not_crash():
    memory = FinancialSituationMemory("empty")
    memory.add_situations([("", "no evidence")])
    assert len(memory.get_memories("question")) == 1


def test_trader_receives_original_evidence_not_just_plan():
    state = {"company_of_interest": "AAPL", "investment_plan": "plan only", "market_report": "source-price 101.23",
             "sentiment_report": "sentiment source", "news_report": "event source", "fundamentals_report": "filing source", "trade_date": "2026-03-01"}
    memory = Mock()
    memory.get_memories.return_value = []
    with patch("tradingagents.agents.trader.trader.invoke_structured_decision_with_retry", return_value=(Mock(), "{}")) as invoke:
        create_trader(Mock(), memory)(state)
    prompt = str(invoke.call_args.args[1])
    for evidence in ("source-price 101.23", "event source", "filing source", "2026-03-01"):
        assert evidence in prompt


def test_default_model_cannot_silently_downgrade(monkeypatch):
    from tradingagents.llm_clients.codex_preflight import codex_preflight_fallback_models
    from tradingagents.llm_clients.codex_chat_model import CodexChatModel
    monkeypatch.delenv("TRADINGAGENTS_CODEX_PREFLIGHT_ALLOW_MODEL_FALLBACK", raising=False)
    monkeypatch.delenv("TRADINGAGENTS_CODEX_ALLOW_MODEL_FALLBACK", raising=False)
    assert codex_preflight_fallback_models("deep") == ()
    captured = {}
    def preflight(**kwargs):
        captured.update(kwargs)
        return Mock(resolved_model="gpt-5.6-sol")
    model = CodexChatModel(model="gpt-5.6-sol", codex_workspace_dir=".", preflight_runner=preflight)
    model.preflight()
    assert captured["fallback_models"] == ()
