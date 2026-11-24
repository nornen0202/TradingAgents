"""Regression tests for review fixes (2026-11-22)."""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from tradingagents import translation
from tradingagents.agents.utils.core_stock_tools import get_intraday_snapshot
from tradingagents.dataflows import alpha_vantage_indicator, interface, naver_news
from tradingagents.dataflows.alpha_vantage_common import AlphaVantageRateLimitError
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.integrity import is_historical
from tradingagents.dataflows.intraday import providers as intraday_providers
from tradingagents.dataflows.intraday.kis_quotes import KISQuoteProvider
from tradingagents.dataflows.intraday.microstructure import KISMicrostructureProvider
from tradingagents.dataflows.intraday_market import fetch_intraday_market_snapshot
from tradingagents.dataflows.vendor_exceptions import (
    VendorInputError,
    VendorMalformedResponseError,
    VendorUnavailableError,
)
from tradingagents.graph.reflection import Reflector
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.performance.action_outcomes import initialize_action_tracker, update_action_outcomes
from tradingagents.portfolio.state_store import _write_json as state_write_json
from tradingagents.scheduled import market_calendar
from tradingagents.schemas import IntradayMarketSnapshot
from tradingagents.work import handoff


def _snapshot(*, ticker: str = "005930.KS", asof: str | None = None, provider: str = "yfinance") -> IntradayMarketSnapshot:
    return IntradayMarketSnapshot(
        ticker=ticker,
        asof=asof,
        provider=provider,
        interval="5m",
        last_price=71000.0,
        session_vwap=70800.0,
        day_high=71500.0,
        day_low=70200.0,
        volume=10000,
        avg20_daily_volume=20000.0,
        relative_volume=0.5,
        market_session="regular",
    )


def test_historical_analysis_as_of_blocks_live_kis_and_falls_back(monkeypatch):
    kis_live = Mock(side_effect=AssertionError("KIS live provider must not run on historical analysis_as_of"))
    yf_snap = _snapshot(ticker="005930.KS", asof="2024-05-10T06:00:00+00:00", provider="yfinance")
    providers = {
        "kis_microstructure": SimpleNamespace(fetch=kis_live),
        "kis": SimpleNamespace(fetch=kis_live),
        "yfinance": SimpleNamespace(fetch=Mock(return_value=yf_snap)),
    }
    monkeypatch.setattr("tradingagents.dataflows.intraday_market.get_intraday_provider", lambda name: providers[name])

    with run_config({"analysis_as_of": "2024-05-10"}):
        result = fetch_intraday_market_snapshot("005930.KS")

    kis_live.assert_not_called()
    assert result.provider == "yfinance"
    assert result.missing_reason["provider:kis_microstructure"] == "unavailable:VendorUnavailableError"
    assert result.missing_reason["provider:kis"] == "unavailable:VendorUnavailableError"


def test_direct_kis_intraday_providers_reject_historical_cutoff():
    with run_config({"analysis_as_of": "2024-05-10T15:00:00+09:00"}):
        with pytest.raises(VendorUnavailableError, match="historical"):
            KISQuoteProvider().fetch("005930.KS")
        with pytest.raises(VendorUnavailableError, match="historical"):
            KISMicrostructureProvider().fetch("AAPL")


def test_intraday_snapshot_rejects_future_or_missing_asof_and_exposes_tool_error(monkeypatch):
    future_snap = _snapshot(ticker="AAPL", asof="2026-04-15T14:00:00+00:00", provider="yfinance")
    missing_snap = _snapshot(ticker="AAPL", asof=None, provider="yfinance")

    monkeypatch.setattr(
        "tradingagents.dataflows.intraday_market.get_intraday_provider",
        lambda _name: SimpleNamespace(fetch=Mock(return_value=future_snap)),
    )
    with run_config({"analysis_as_of": "2026-04-14T14:00:00Z"}):
        with pytest.raises(VendorUnavailableError, match="exceeds analysis_as_of"):
            fetch_intraday_market_snapshot("AAPL", provider="yfinance")
        tool_payload = json.loads(get_intraday_snapshot.func("AAPL", "5m"))
        assert tool_payload["ok"] is False
        assert tool_payload["error_type"] == "VendorUnavailableError"

    monkeypatch.setattr(
        "tradingagents.dataflows.intraday_market.get_intraday_provider",
        lambda _name: SimpleNamespace(fetch=Mock(return_value=missing_snap)),
    )
    with run_config({"analysis_as_of": "2024-05-10"}):
        with pytest.raises(VendorUnavailableError, match="omitted snapshot asof"):
            fetch_intraday_market_snapshot("AAPL", provider="yfinance")


def test_intraday_cutoff_allows_live_today_and_rejects_naive_cutoff(monkeypatch):
    today_kst = datetime.now(timezone(timedelta(hours=9))).date().isoformat()
    live_snap = _snapshot(ticker="005930.KS", asof=datetime.now(timezone.utc).isoformat(), provider="kis")
    monkeypatch.setattr(
        "tradingagents.dataflows.intraday_market.get_intraday_provider",
        lambda name: SimpleNamespace(fetch=Mock(return_value=live_snap)),
    )
    with run_config({"analysis_as_of": today_kst}):
        assert fetch_intraday_market_snapshot("005930.KS", provider="kis").provider == "kis"

    with run_config({"analysis_as_of": "2026-04-14T14:00:00"}):
        with pytest.raises(ValueError, match="timezone"):
            intraday_providers.require_live_intraday_clock("America/New_York")


def test_is_historical_supports_dates_aware_datetimes_and_rejects_naive():
    assert is_historical(None) is False
    assert is_historical("") is False
    assert is_historical("2020-01-01") is True
    assert is_historical("2099-01-01") is False
    assert is_historical("2020-01-01T14:00:00Z") is True
    assert is_historical("2099-01-01T00:00:00+09:00") is False
    assert is_historical(date(2020, 1, 1)) is True
    assert is_historical(datetime(2020, 1, 1, 12, 0, tzinfo=timezone.utc)) is True

    with pytest.raises(ValueError, match="timezone"):
        is_historical("2020-01-01T14:00:00")
    with pytest.raises(ValueError, match="timezone"):
        is_historical(datetime(2020, 1, 1, 12, 0))


def test_route_to_vendor_insider_transactions_accepts_datetime_analysis_as_of(monkeypatch):
    fake_insider = Mock(return_value="should be withheld")

    monkeypatch.setattr(interface, "get_vendor", lambda *_a: "alpha_vantage")
    monkeypatch.setitem(interface.VENDOR_METHODS, "get_insider_transactions", {"alpha_vantage": fake_insider})
    with run_config({"analysis_as_of": "2024-01-15T12:00:00Z"}):
        result = interface.route_to_vendor("get_insider_transactions", "AAPL", curr_date="2024-01-15")
    assert "historical publication timestamps are not verified" in result
    fake_insider.assert_not_called()


def test_reflect_and_remember_accepts_iso_timestamps_and_enforces_analysis_date():
    llm = Mock()
    llm.invoke.return_value = SimpleNamespace(content="lesson learned")
    graph = TradingAgentsGraph.__new__(TradingAgentsGraph)
    graph.reflector = Reflector(llm)
    for attr in (
        "bull_memory",
        "bear_memory",
        "trader_memory",
        "invest_judge_memory",
        "portfolio_manager_memory",
    ):
        setattr(graph, attr, Mock())

    state = {
        "company_of_interest": "AAPL",
        "trade_date": "2026-03-01",
        "analysis_date": "2026-03-01",
        "market_report": "m",
        "sentiment_report": "s",
        "news_report": "n",
        "fundamentals_report": "f",
        "trader_investment_plan": "p",
        "investment_debate_state": {"bull_history": "b", "bear_history": "r", "judge_decision": "j"},
        "risk_debate_state": {"judge_decision": "pm"},
    }
    graph.reflect_and_remember(0.05, state=state, outcome_known_at="2026-03-02T10:00:00+00:00")
    assert llm.invoke.call_count == 5

    llm.invoke.reset_mock()
    later_analysis_state = {**state, "analysis_date": "2026-03-03"}
    with pytest.raises(ValueError):
        graph.reflect_and_remember(0.05, state=later_analysis_state, outcome_known_at="2026-03-03T12:00:00+00:00")
    with pytest.raises(ValueError):
        graph.reflect_and_remember(0.05, state=state, outcome_known_at="2026-03-02T10:00:00")
    with pytest.raises(ValueError):
        graph.reflect_and_remember(0.05, state=state, outcome_known_at="")
    llm.invoke.assert_not_called()


def test_alpha_vantage_indicator_propagates_typed_errors_and_triggers_fallback(monkeypatch):
    with patch.object(alpha_vantage_indicator, "_make_api_request", side_effect=AlphaVantageRateLimitError("rate limit")):
        with pytest.raises(AlphaVantageRateLimitError):
            alpha_vantage_indicator.get_indicator("AAPL", "rsi", "2026-04-02", 5)

    monkeypatch.setattr(interface, "get_vendor", lambda *_a: "alpha_vantage,yfinance")
    monkeypatch.setitem(
        interface.VENDOR_METHODS,
        "get_indicators",
        {
            "alpha_vantage": alpha_vantage_indicator.get_indicator,
            "yfinance": lambda *_a, **_kw: "yfinance rsi fallback",
        },
    )
    with patch.object(alpha_vantage_indicator, "_make_api_request", side_effect=AlphaVantageRateLimitError("limit")):
        assert interface.route_to_vendor("get_indicators", "AAPL", "rsi", "2026-04-02", 5) == "yfinance rsi fallback"

    with patch.object(alpha_vantage_indicator, "_make_api_request", return_value="time,OTHER\n2026-04-02,55.0\n"):
        with pytest.raises(VendorMalformedResponseError):
            alpha_vantage_indicator.get_indicator("AAPL", "rsi", "2026-04-02", 5)

    with patch.object(alpha_vantage_indicator, "_make_api_request", return_value="time,RSI\n2026-04-10,55.0\n"):
        with pytest.raises(VendorUnavailableError):
            alpha_vantage_indicator.get_indicator("AAPL", "rsi", "2026-04-02", 5)

    with pytest.raises(VendorUnavailableError):
        alpha_vantage_indicator.get_indicator("AAPL", "vwma", "2026-04-02", 5)

    with pytest.raises(VendorInputError):
        alpha_vantage_indicator.get_indicator("AAPL", "rsi", "bad-date", 5)

    csv_payload = "time,RSI\n2026-04-01,48.5\n2026-04-02,52.0\n2026-04-05,99.0\n"
    with patch.object(alpha_vantage_indicator, "_make_api_request", return_value=csv_payload):
        formatted = alpha_vantage_indicator.get_indicator("AAPL", "rsi", "2026-04-02", 5)
    assert "2026-04-01: 48.5" in formatted and "2026-04-02: 52.0" in formatted
    assert "2026-04-05" not in formatted


def test_naver_news_parses_dates_handles_malformed_json_and_empty_social_fallback():
    valid_response = Mock(status_code=200)
    valid_response.raise_for_status.return_value = None
    valid_response.json.return_value = {
        "items": [
            {"title": "<b>Samsung</b> Q1", "pubDate": "Wed, 01 Apr 2026 09:00:00 +0900", "link": "https://n.example/1"},
            {"title": "Future article", "pubDate": "Thu, 02 Apr 2026 09:00:00 +0900", "link": "https://n.example/2"},
            {"title": "Bad date", "pubDate": "not-a-date", "link": "https://n.example/3"},
        ]
    }
    with (
        patch("tradingagents.dataflows.naver_news.get_api_key", return_value="key"),
        patch("tradingagents.dataflows.naver_news.requests.get", return_value=valid_response),
    ):
        items = naver_news.fetch_company_news_naver("005930.KS", "2026-04-01", "2026-04-01")
    assert [item.title for item in items] == ["Samsung Q1"]

    bad_json_response = Mock(status_code=200)
    bad_json_response.raise_for_status.return_value = None
    bad_json_response.json.side_effect = ValueError("invalid json")
    with (
        patch("tradingagents.dataflows.naver_news.get_api_key", return_value="key"),
        patch("tradingagents.dataflows.naver_news.requests.get", return_value=bad_json_response),
        pytest.raises(VendorMalformedResponseError, match="valid JSON"),
    ):
        naver_news.fetch_company_news_naver("005930.KS", "2026-04-01", "2026-04-01")

    empty_response = Mock(status_code=200)
    empty_response.raise_for_status.return_value = None
    empty_response.json.return_value = {"items": []}
    with (
        patch("tradingagents.dataflows.naver_news.get_api_key", return_value="key"),
        patch("tradingagents.dataflows.naver_news.requests.get", return_value=empty_response),
    ):
        empty_social = naver_news.get_social_sentiment_naver("005930.KS", "2026-04-01", "2026-04-01")
    assert interface.should_fallback(empty_social) is True


def test_translation_chunking_preserves_fences_without_corrupting_following_prose():
    compact_doc = (
        "Intro paragraph one.\n\n"
        "```python\nx = 1\n```\n\n"
        "Prose A.\n\n"
        "Prose B.\n\n"
        "Prose C."
    )
    chunks = translation._split_markdown_chunks(compact_doc, 40)
    assert "".join(chunks) == compact_doc
    # After the compact fence closes, Prose A/B/C are merged together rather than split one-by-one.
    assert any("Prose A." in chunk and "Prose B." in chunk for chunk in chunks)

    multiline_fence_doc = (
        "Summary before.\n\n"
        "```json\n{\"a\": 1}\n\n{\"b\": 2}\n```\n\n"
        "Summary after."
    )
    multi_chunks = translation._split_markdown_chunks(multiline_fence_doc, 25)
    assert "".join(multi_chunks) == multiline_fence_doc
    fence_chunks = [chunk for chunk in multi_chunks if "{\"a\": 1}" in chunk]
    assert len(fence_chunks) == 1
    assert translation._is_code_fence_block(fence_chunks[0]) is True

    translated_calls: list[str] = []
    fake_settings = translation.TranslationSettings(
        backend="nllb_ct2",
        model="nllb-200-distilled-600m",
        model_path=None,
        tokenizer_path=None,
        device="cpu",
        compute_type="int8",
        max_chunk_chars=25,
        allow_llm_fallback=True,
        allow_large_model=False,
    )
    with (
        patch.object(translation, "get_translation_settings", return_value=fake_settings),
        patch.object(
            translation,
            "_translate_chunk",
            side_effect=lambda chunk, *_a: translated_calls.append(chunk) or f"[KO:{chunk.strip()}]",
        ),
    ):
        output = translation.translate_with_backend(multiline_fence_doc, "Korean")
    assert all("{\"a\": 1}" not in call for call in translated_calls)
    assert '{"a": 1}\n\n{"b": 2}' in output


def test_market_calendar_fallback_converts_utc_clock_to_market_timezone(monkeypatch):
    monkeypatch.setattr(market_calendar, "_exchange_calendar_state", lambda **_: None)
    # 2026-10-01 02:00 UTC == 11:00 KST (KR regular open) == 2026-09-30 22:00 EDT (US closed).
    utc_stamp = datetime(2026, 10, 1, 2, 0, tzinfo=timezone.utc)
    kr_state = market_calendar.market_session_state(market="KR", now_local=utc_stamp)
    us_state = market_calendar.market_session_state(market="US", now_local=utc_stamp)
    assert kr_state["estimated_is_open"] is True
    assert us_state["estimated_is_open"] is False
    assert market_calendar._fallback_phase("KR", utc_stamp) == "regular"
    assert market_calendar._fallback_phase("US", utc_stamp) == "post_close"

    # 2026-10-02 19:00 UTC == Friday 15:00 EDT (US open) == Saturday 04:00 KST (KR weekend closed).
    friday_ny_utc = datetime(2026, 10, 2, 19, 0, tzinfo=timezone.utc)
    assert market_calendar.market_session_state(market="US", now_local=friday_ny_utc)["estimated_is_open"] is True
    assert market_calendar.market_session_state(market="KR", now_local=friday_ny_utc)["estimated_is_open"] is False


def test_atomic_writes_and_case_insensitive_action_outcomes(tmp_path: Path, monkeypatch):
    state_target = tmp_path / "portfolio" / "snapshot.json"
    state_write_json(state_target, {"ok": True})
    assert json.loads(state_target.read_text(encoding="utf-8")) == {"ok": True}
    assert list(state_target.parent.glob("*.tmp*")) == []

    report_file = tmp_path / "report.json"
    digest = "a" * 64
    report_file.write_text(json.dumps({"surface": "kr", "event_id": "kr:" + "b" * 32,
                                      "report_sha256": digest}), encoding="utf-8")
    monkeypatch.setattr(handoff, "validate_work_report", lambda _report: None)
    runtime = SimpleNamespace(
        root=tmp_path,
        status=lambda _surface: {
            "state": {
                "last_acked_event_id": "kr:" + "b" * 32,
                "last_acked_report_sha256": digest,
                "last_acked_report_path": str(report_file),
            }
        },
    )
    monkeypatch.setattr(handoff.shutil, "which", lambda _name: "gh")
    receipt = handoff.dispatch_pages_handoff(
        runtime,
        surface="kr",
        event_id="kr:" + "b" * 32,
        report_sha256=digest,
        repository="nornen0202/TradingAgents",
        runner=lambda *a, **k: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )
    receipt_path = tmp_path / "handoffs" / "kr" / f"{digest}.json"
    assert receipt["status"] == "DISPATCH_ACCEPTED"
    assert json.loads(receipt_path.read_text(encoding="utf-8"))["status"] == "DISPATCH_ACCEPTED"
    assert list(receipt_path.parent.glob("*.tmp*")) == []

    db_path = tmp_path / "outcomes.sqlite"
    initialize_action_tracker(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO action_recommendations (run_id, ticker, action, created_at) VALUES (?, ?, ?, ?)",
            ("run-1", "aapl", "BUY", "2026-09-21T00:00:00+00:00"),
        )
    prices = {
        "AAPL": [
            {"date": "2026-09-21", "close": 100.0},
            {"date": "2026-09-22", "close": 110.0},
        ]
    }
    update_action_outcomes(
        db_path,
        "2026-09-22",
        price_history=prices,
        horizons=(1,),
        recorded_at="2026-09-22T23:59:59+00:00",
    )
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT return_1d FROM action_outcomes").fetchone()
    assert row is not None and row[0] == pytest.approx(0.10)
