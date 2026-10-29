import json
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from tradingagents.agents.utils import technical_indicators_tools as indicators
from tradingagents.dataflows import interface
from tradingagents.dataflows.research_evidence import REQUIRED_METHODS, SCHEMA, assess_tool_evidence, evidence_review_reason
from tradingagents.dataflows.vendor_exceptions import InsufficientIndicatorHistoryError, VendorMalformedResponseError


def test_unavailable_indicator_keeps_failed_evidence_and_execution_gate(monkeypatch):
    interface.reset_tool_telemetry()
    begin = datetime.now(timezone.utc).isoformat()
    provider = Mock(side_effect=InsufficientIndicatorHistoryError("private diagnostic must not be returned"))
    monkeypatch.setattr(interface, "_route_to_vendor", provider)
    response = json.loads(indicators.get_indicators.invoke({"symbol": "179880.KQ", "indicator": "close_200_sma",
                                                          "curr_date": "2026-10-28", "look_back_days": 30}))
    assert response["status"] == "UNAVAILABLE" and response["value"] is None
    assert response["execution_authorized"] is False and response["as_of"] == "2026-10-28"
    assert "private diagnostic" not in str(response)
    requests = interface.snapshot_tool_requests()
    assert len(requests) == 1 and requests[0]["status"] == "error" and requests[0]["result_sha256"] is None
    evidence = assess_tool_evidence({"request_schema": SCHEMA, "request_outcomes": requests,
                                    "events": interface.snapshot_tool_telemetry()},
                                   started_at=begin, finished_at=datetime.now(timezone.utc).isoformat())
    assert "get_indicators" in evidence["missing_required_methods"]
    assert evidence_review_reason({"request_evidence": evidence}) == "required_research_evidence_missing"
    provider.assert_called_once()


def test_one_unavailable_indicator_does_not_drop_other_requested_results(monkeypatch):
    provider = Mock(side_effect=[InsufficientIndicatorHistoryError("short history"), "2026-10-28: 123.4"])
    monkeypatch.setattr(indicators, "route_to_vendor", provider)
    response = indicators.get_indicators.invoke({"symbol": "179880.KQ", "indicator": "close_200_sma,close_10_ema",
                                                "curr_date": "2026-10-28", "look_back_days": 0})
    unavailable, available = response.split("\n\n")
    assert json.loads(unavailable)["value"] is None and available == "2026-10-28: 123.4"
    assert provider.call_count == 2


@pytest.mark.parametrize("error", [VendorMalformedResponseError("invalid data"), RuntimeError("unknown failure")])
def test_unrelated_integrity_or_runtime_errors_are_not_hidden(monkeypatch, error):
    monkeypatch.setattr(indicators, "route_to_vendor", Mock(side_effect=error))
    with pytest.raises(type(error)):
        indicators.get_indicators.invoke({"symbol": "179880.KQ", "indicator": "close_10_ema",
                                          "curr_date": "2026-10-28"})


def test_available_short_indicator_cannot_clear_missing_long_indicator(monkeypatch):
    interface.reset_tool_telemetry()
    begin = datetime.now(timezone.utc).isoformat()
    monkeypatch.setitem(interface.VENDOR_METHODS, "get_indicators", {
        "yfinance": Mock(side_effect=[InsufficientIndicatorHistoryError("short IPO history"), "10 EMA: 123.4"]),
    })
    from tradingagents.dataflows.config import run_config
    with run_config({"tool_vendors": {"get_indicators": "yfinance"}}):
        indicators.get_indicators.invoke({"symbol": "179880.KQ", "indicator": "close_200_sma,close_10_ema",
                                          "curr_date": "2026-10-28", "look_back_days": 0})
    requests = interface.snapshot_tool_requests()
    events = interface.snapshot_tool_telemetry()
    assert [row["status"] for row in requests] == ["error", "available"]
    # Every other required method is available, so the failed long indicator
    # must independently retain the execution gate even after a valid short one.
    from uuid import uuid4
    for method in REQUIRED_METHODS - {"get_indicators"}:
        identity = uuid4().hex
        requests.append({"request_id": identity, "method": method, "status": "available",
                         "started_at": begin, "completed_at": begin, "result_sha256": "a" * 64})
        events.append({"request_id": identity, "method": method, "status": "success", "fallback": False})
    evidence = assess_tool_evidence({"request_schema": SCHEMA, "request_outcomes": requests, "events": events},
                                   started_at=begin, finished_at=datetime.now(timezone.utc).isoformat())
    assert evidence["missing_required_methods"] == ["get_indicators"]
    assert evidence_review_reason({"request_evidence": evidence}) == "required_research_evidence_missing"
