from contextvars import copy_context
from copy import deepcopy
import hashlib
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest

from tradingagents.dataflows import interface
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.daily_history_evidence import DailyHistoryEvidenceRecorder
from tradingagents.dataflows.daily_history_selection import select_daily_history
from tradingagents.dataflows.us_daily_history import SOURCE
from tradingagents.dataflows.vendor_exceptions import VendorInputError, VendorMalformedResponseError


DAY = "2024-01-03"


def frame():
    result = pd.DataFrame({"Date": pd.to_datetime(["2024-01-02", DAY]),
                           "Open": [100., 101.], "High": [103., 104.], "Low": [99., 100.],
                           "Close": [102., 103.], "Volume": [1000., 1200.]})
    result.attrs = {"source": SOURCE, "provider": "kis", "exchange": "NAS", "adjustment": "MODP=1",
                    "requested_start": "2024-01-02", "requested_end": DAY,
                    "observed_at": "2024-01-04T00:00:00+00:00", "complete": True,
                    "session_count": 2, "series_sha256": hashlib.sha256(result.to_csv(index=False).encode()).hexdigest()}
    return result


def collect(data, *, source=SOURCE, end=DAY):
    recorder = DailyHistoryEvidenceRecorder("AAPL")
    token = recorder.activate()
    try:
        with run_config({}):
            select_daily_history("AAPL", end, source, data)
    finally:
        recorder.reset(token)
    return recorder.receipt()


def test_child_context_receipt_survives_scope_cleanup_and_original_mutation():
    recorder = DailyHistoryEvidenceRecorder("AAPL")
    token = recorder.activate()
    data = frame()
    original = deepcopy(data.attrs)
    try:
        with run_config({}):
            copy_context().run(select_daily_history, "AAPL", DAY, SOURCE, data)
            data.loc[0, "Close"] = 10
            data.attrs.clear()
            select_daily_history("AAPL", DAY, SOURCE, data)
        receipt = recorder.receipt()
    finally:
        recorder.reset(token)
    entry = receipt["entries"][0]
    assert entry["status"] == "VERIFIED_RETRIEVED_SERIES"
    assert entry["series_sha256"] == original["series_sha256"]
    assert entry["source"] == SOURCE and entry["adjustment"] == "MODP=1"
    assert entry["row_count"] == 2 and entry["last_session"] == DAY
    assert entry["historical_vintage_verified"] is False
    assert "not a verified historical snapshot vintage" in entry["limitations"][0]
    entry["limitations"].clear()
    assert recorder.receipt()["entries"][0]["limitations"]
    with run_config({}):
        select_daily_history("AAPL", DAY, "yfinance")
    assert len(recorder.receipt()["entries"]) == 1


def test_receipt_only_contains_allowlisted_provenance_not_prices_or_secret_metadata():
    data = frame()
    data.attrs.update(api_key="private-key", raw_prompt="private-prompt", raw_response={"secret": "private-value"})
    receipt = collect(data)
    serialized = json.dumps(receipt)
    assert "private" not in serialized
    assert "Open" not in serialized and "Close" not in serialized
    assert receipt["entries"][0]["status"] == "VERIFIED_RETRIEVED_SERIES"


@pytest.mark.parametrize("end", [None, "bad", "2099-01-01"])
def test_invalid_or_future_requested_date_is_never_verified(end):
    entry = collect(frame(), end=end)["entries"][0]
    assert entry["status"] == "UNVERIFIED"
    assert "series_sha256" not in entry


@pytest.mark.parametrize("change", [
    {"observed_at": None}, {"observed_at": "bad"}, {"observed_at": "2024-01-04"},
    {"observed_at": "2099-01-04T00:00:00Z"}, {"observed_at": "2024-01-01T00:00:00Z"},
    {"requested_end": "2024-01-04"}, {"requested_end": "bad"}, {"requested_start": None},
    {"requested_start": "2024-01-04"}, {"complete": False}, {"series_sha256": "a" * 64},
    {"session_count": 3}, {"adjustment": "unknown"}, {"provider": "yfinance"}, {"source": "yfinance"},
])
def test_invalid_snapshot_metadata_cannot_become_verified_evidence(change):
    data = frame()
    data.attrs.update(change)
    receipt = collect(data)
    entry = receipt["entries"][0]
    assert entry["status"] == "UNVERIFIED"
    assert "series_sha256" not in entry and "observed_at" not in entry
    assert entry["historical_vintage_verified"] is False


@pytest.mark.parametrize("kind", ["empty", "missing_date", "invalid_date", "future_date", "nan_price"])
def test_empty_missing_invalid_or_future_rows_are_not_verified(kind):
    data = frame()
    if kind == "empty":
        data = data.iloc[:0].copy()
    elif kind == "missing_date":
        data = data.drop(columns=["Date"])
    elif kind in {"invalid_date", "future_date"}:
        data["Date"] = ["2024-01-02", "bad" if kind == "invalid_date" else "2099-01-01"]
    else:
        data.loc[0, "Close"] = float("nan")
    assert collect(data)["entries"][0]["status"] == "UNVERIFIED"


@pytest.mark.parametrize("source", ["yfinance", "alpha_vantage"])
def test_source_only_evidence_never_invents_snapshot_or_observation(source):
    entry = collect(None, source=source)["entries"][0]
    assert entry["source"] == source and entry["status"] == "UNVERIFIED"
    assert entry["reason"] == "selected_source_without_snapshot"
    assert "observed_at" not in entry and "series_sha256" not in entry


def test_empty_scope_and_different_ticker_cannot_create_evidence():
    recorder = DailyHistoryEvidenceRecorder("AAPL")
    assert recorder.receipt()["status"] == "NOT_COLLECTED"
    token = recorder.activate()
    try:
        with run_config({}):
            select_daily_history("MSFT", DAY, SOURCE, frame())
        assert recorder.receipt()["entries"] == []
    finally:
        recorder.reset(token)


def test_mixed_source_rejection_and_nested_recorders_preserve_original_receipt():
    first, second = DailyHistoryEvidenceRecorder("AAPL"), DailyHistoryEvidenceRecorder("AAPL")
    outer = first.activate()
    try:
        with run_config({}):
            select_daily_history("AAPL", DAY, SOURCE, frame())
            original = first.receipt()
            with pytest.raises(VendorMalformedResponseError, match="source changed"):
                select_daily_history("AAPL", DAY, "yfinance")
            inner = second.activate()
            try:
                with run_config({}):
                    select_daily_history("AAPL", DAY, "yfinance")
            finally:
                second.reset(inner)
            assert first.receipt() == original
            assert second.receipt()["entries"][0]["source"] == "yfinance"
    finally:
        first.reset(outer)


@pytest.mark.parametrize("method", ["get_stock_data", "get_indicators"])
def test_actual_provider_and_wrapper_are_separate_without_fabricated_attempts(monkeypatch, method):
    monkeypatch.setenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED", "1")
    def provider(*args):
        select_daily_history("AAPL", DAY, SOURCE, frame())
        return "verified prices without copying source metadata into report"
    monkeypatch.setitem(interface.VENDOR_METHODS, method, {"yfinance": Mock(side_effect=provider)})
    interface.reset_tool_telemetry()
    with run_config({}):
        args = ("AAPL", "2024-01-02", DAY) if method == "get_stock_data" else ("AAPL", "close_50_sma", DAY, 1)
        interface.route_to_vendor(method, *args)
    events, requests = interface.snapshot_tool_telemetry(), interface.snapshot_tool_requests()
    assert len(events) == len(requests) == 1
    assert events[0]["vendor"] == "kis" and events[0]["wrapper_vendor"] == "yfinance"
    assert events[0]["internal_recovery"] is True and events[0]["daily_history_source"] == SOURCE
    assert events[0]["status"] == "success" and events[0]["fallback"] is False
    assert requests[0]["status"] == "available" and len(requests[0]["result_sha256"]) == 64
    interface.reset_tool_telemetry()


@pytest.mark.parametrize("failure,status,request_status", [
    ("empty", "fallback", "unavailable"), ("calculation", "fallback", "error"),
    ("input", "input_error", "input_error"),
])
@pytest.mark.parametrize("method", ["get_stock_data", "get_indicators"])
def test_selected_source_remains_visible_after_empty_or_failed_wrapper(
        monkeypatch, method, failure, status, request_status):
    from tradingagents.scheduled.runner import _failed_tool_telemetry
    monkeypatch.setenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED", "1")
    def provider(*args):
        select_daily_history("AAPL", DAY, SOURCE, frame())
        if failure == "input":
            raise VendorInputError("invalid indicator")
        if failure == "calculation":
            raise RuntimeError("private calculation diagnostic")
        return "No data found"
    monkeypatch.setitem(interface.VENDOR_METHODS, method, {"yfinance": Mock(side_effect=provider)})
    interface.reset_tool_telemetry()
    with run_config({}):
        args = ("AAPL", "2024-01-02", DAY) if method == "get_stock_data" else ("AAPL", "close_50_sma", DAY, 1)
        if failure == "empty":
            assert interface.route_to_vendor(method, *args) == "No data found"
        else:
            with pytest.raises((RuntimeError, VendorInputError)):
                interface.route_to_vendor(method, *args)
    evidence = _failed_tool_telemetry({})
    events, requests = evidence["events"], evidence["request_outcomes"]
    assert len(events) == len(requests) == 1
    assert events[0]["vendor"] == "kis" and events[0]["wrapper_vendor"] == "yfinance"
    assert events[0]["daily_history_source"] == SOURCE and events[0]["internal_recovery"] is True
    assert events[0]["status"] == status and events[0]["fallback"] is (status == "fallback")
    assert requests[0]["status"] == request_status
    assert "private" not in json.dumps(evidence)
    interface.reset_tool_telemetry()


@pytest.mark.parametrize("fail", [False, True])
def test_runner_saves_receipt_after_graph_context_closes_and_always_resets(tmp_path, monkeypatch, fail):
    from tradingagents.scheduled import runner
    from tradingagents.scheduled.config import load_scheduled_config
    path = tmp_path / "config.toml"
    path.write_text('[run]\ntickers=["AAPL"]\nmarket="US"\n[storage]\n'
                    f'archive_dir="{(tmp_path / "archive").as_posix()}"\nsite_dir="{(tmp_path / "site").as_posix()}"\n')
    config = load_scheduled_config(path)
    def propagate(*args, **kwargs):
        with run_config({}):
            copy_context().run(select_daily_history, "AAPL", DAY, SOURCE, frame())
        if fail:
            raise RuntimeError("research failed after obtaining prices")
        return {"company_of_interest": "AAPL", "messages": [], "market_report": "Summary omits provider details"}, "WAIT"
    graph = SimpleNamespace(propagate=propagate, close=Mock())
    monkeypatch.setattr(runner, "TradingAgentsGraph", lambda *a, **k: graph)
    monkeypatch.setattr(runner, "_select_public_decision", lambda *a: "WAIT")
    monkeypatch.setattr(runner, "polish_ticker_report", lambda state, **k: (state, {}))
    monkeypatch.setattr(runner, "save_report_bundle", lambda state, ticker, directory, **k: directory / "report.md")
    monkeypatch.setattr(runner, "build_public_equity_intelligence_artifacts", Mock(side_effect=ValueError("fixture")))
    monkeypatch.setattr(runner, "build_execution_contract", Mock(side_effect=ValueError("fixture")))
    monkeypatch.setattr("tradingagents.charting.report.build_review", lambda *a, **k: {})
    monkeypatch.setattr("tradingagents.charting.report.render_review", lambda *a, **k: "")
    outer = DailyHistoryEvidenceRecorder("AAPL")
    token = outer.activate()
    try:
        result = runner._run_single_ticker(config=config, ticker="AAPL", run_dir=tmp_path / "run",
                                          engine_results_dir=tmp_path / "engine", trade_date_override=DAY)
        assert result["status"] == ("failed" if fail else "success")
        payload = json.loads((tmp_path / "run/tickers/AAPL" / ("error.json" if fail else "analysis.json")).read_text())
        evidence = payload["daily_history_evidence"]
        assert evidence["entries"][0]["status"] == "VERIFIED_RETRIEVED_SERIES"
        assert evidence["entries"][0]["source"] == SOURCE
        assert evidence["historical_vintage_verified"] is False
        assert outer.receipt()["entries"] == []
        with run_config({}):
            select_daily_history("AAPL", DAY, "yfinance")
        assert outer.receipt()["entries"][0]["source"] == "yfinance"
    finally:
        outer.reset(token)
    graph.close.assert_called_once()
