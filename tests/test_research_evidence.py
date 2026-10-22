from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from tradingagents.dataflows import interface
from tradingagents.dataflows.research_evidence import (
    REQUIRED_METHODS,
    SCHEMA,
    assess_tool_evidence,
    evidence_review_reason,
    evidence_risk_count,
)
from tradingagents.dataflows.vendor_exceptions import VendorInputError


START = datetime(2026, 10, 22, 10, tzinfo=timezone.utc)
END = START + timedelta(minutes=5)


def receipt():
    outcomes, events = [], []
    for index, method in enumerate(sorted(REQUIRED_METHODS)):
        identity = f"{index:032x}"
        outcomes.append(
            {
                "request_id": identity,
                "method": method,
                "status": "available",
                "result_sha256": "a" * 64,
                "started_at": START.isoformat(),
                "completed_at": END.isoformat(),
            }
        )
        events.extend(
            [
                {
                    "request_id": identity,
                    "method": method,
                    "vendor": "first",
                    "status": "fallback",
                    "fallback": True,
                },
                {
                    "request_id": identity,
                    "method": method,
                    "vendor": "second",
                    "status": "success",
                    "fallback": False,
                },
            ]
        )
    return {"request_schema": SCHEMA, "request_outcomes": outcomes, "events": events}


def assess(data):
    return assess_tool_evidence(
        data, started_at=START.isoformat(), finished_at=END.isoformat()
    )


def test_recovered_provider_attempts_are_not_missing_core_evidence():
    evidence = assess(receipt())
    assert evidence["status"] == "COMPLETE"
    assert evidence["recovered_request_count"] == len(REQUIRED_METHODS)
    assert (
        evidence_review_reason({"fallback_count": 30, "request_evidence": evidence})
        is None
    )
    assert (
        evidence_risk_count({"fallback_count": 30, "request_evidence": evidence}) == 0
    )


def test_optional_unavailability_is_visible_without_replacing_core_evidence():
    data = receipt()
    data["request_outcomes"].append(
        {
            "request_id": "f" * 32,
            "method": "get_social_sentiment",
            "status": "unavailable",
            "started_at": START.isoformat(),
            "completed_at": END.isoformat(),
        }
    )
    evidence = assess(data)
    assert evidence["status"] == "COMPLETE"
    assert evidence["optional_unavailable_methods"] == ["get_social_sentiment"]
    assert evidence_risk_count({"request_evidence": evidence}) == 1


@pytest.mark.parametrize(
    "change",
    [
        "missing_method",
        "unavailable",
        "missing_digest",
        "bad_digest",
        "missing_time",
        "naive_time",
        "future_time",
        "backwards_time",
        "duplicate",
        "unknown_event",
        "method_mismatch",
        "bad_schema",
        "empty",
        "no_events",
        "no_final_success",
        "last_event_failed",
    ],
)
def test_invalid_or_incomplete_evidence_never_clears_review(change):
    data = receipt()
    row = data["request_outcomes"][0]
    if change == "missing_method":
        data["request_outcomes"] = data["request_outcomes"][1:]
        data["events"] = data["events"][2:]
    elif change == "unavailable":
        row["status"] = "unavailable"
    elif change == "missing_digest":
        row.pop("result_sha256")
    elif change == "bad_digest":
        row["result_sha256"] = "claimed"
    elif change == "missing_time":
        row.pop("completed_at")
    elif change == "naive_time":
        row["completed_at"] = "2026-10-22T10:05:00"
    elif change == "future_time":
        row["completed_at"] = (END + timedelta(seconds=1)).isoformat()
    elif change == "backwards_time":
        row["completed_at"] = (START - timedelta(seconds=1)).isoformat()
    elif change == "duplicate":
        data["request_outcomes"].append(deepcopy(row))
    elif change == "unknown_event":
        data["events"][0]["request_id"] = "e" * 32
    elif change == "method_mismatch":
        data["events"][0]["method"] = "get_unrelated"
    elif change == "bad_schema":
        data["request_schema"] = "unknown"
    elif change == "empty":
        data["request_outcomes"] = []
    elif change == "no_events":
        data["events"] = []
    elif change == "no_final_success":
        data["events"] = [e for e in data["events"] if e["fallback"]]
    elif change == "last_event_failed":
        data["events"].append(deepcopy(data["events"][0]))
    assert (
        evidence_review_reason({"fallback_count": 0, "request_evidence": assess(data)})
        == "required_research_evidence_missing"
    )


def test_later_success_for_different_request_cannot_repair_previous_failure():
    data = receipt()
    earlier = deepcopy(data["request_outcomes"][0])
    earlier.update(request_id="f" * 32, status="unavailable", result_sha256=None)
    data["request_outcomes"].append(earlier)
    assert assess(data)["status"] == "REQUIRED_EVIDENCE_MISSING"


def test_legacy_failures_keep_their_original_gate():
    assert (
        assess_tool_evidence({"fallback_count": 9}, started_at=None, finished_at=None)
        is None
    )
    assert evidence_review_reason({"fallback_count": 9}) == "high_fallback_count"


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        [],
        {},
        False,
        {"status": "error", "message": "unavailable"},
        [{"undated": "record"}],
        "DATA_UNAVAILABLE: missing",
        "No insider data: historical publication timestamps are not verified.",
        "SEC disclosure coverage: UNMAPPED",
        "SEC disclosure coverage: PARTIAL_WINDOW",
    ],
)
def test_empty_or_unverified_result_does_not_become_available_when_fallback_disabled(
    value,
):
    interface.reset_tool_telemetry()
    with patch.object(interface, "_route_to_vendor", return_value=value):
        assert interface.route_to_vendor("get_company_news") == value
    assert interface.snapshot_tool_requests()[0]["status"] == "unavailable"


def test_actual_vendor_failover_is_one_correlated_available_request():
    interface.reset_tool_telemetry()
    with (
        patch.object(interface, "get_config", return_value={}),
        patch.object(interface, "get_vendor", return_value="alpha_vantage,yfinance"),
        patch.dict(
            interface.VENDOR_METHODS,
            {
                "get_company_news": {
                    "alpha_vantage": lambda *a, **kw: None,
                    "yfinance": lambda *a, **kw: "Dated usable news",
                }
            },
        ),
    ):
        assert (
            interface.route_to_vendor(
                "get_company_news", "AAPL", "2026-10-21", "2026-10-22"
            )
            == "Dated usable news"
        )
    outcomes, events = (
        interface.snapshot_tool_requests(),
        interface.snapshot_tool_telemetry(),
    )
    assert len(outcomes) == 1 and outcomes[0]["status"] == "available"
    assert len(events) == 2 and {e["request_id"] for e in events} == {
        outcomes[0]["request_id"]
    }
    assert "AAPL" not in str(outcomes)


def test_failed_input_is_not_an_available_request():
    interface.reset_tool_telemetry()
    with patch.object(
        interface, "_route_to_vendor", side_effect=VendorInputError("invalid date")
    ):
        with pytest.raises(VendorInputError):
            interface.route_to_vendor("get_stock_data")
    assert interface.snapshot_tool_requests()[0]["status"] == "input_error"


def test_parallel_calls_keep_distinct_request_identities_and_reset():
    interface.reset_tool_telemetry()

    def routed(method, *a, **kw):
        interface._record_tool_telemetry(
            method=method, vendor="fixture", status="success", fallback=False
        )
        return "Dated usable result"

    with (
        patch.object(interface, "_route_to_vendor", side_effect=routed),
        ThreadPoolExecutor(4) as pool,
    ):
        list(pool.map(interface.route_to_vendor, ["get_company_news"] * 8))
    assert len({row["request_id"] for row in interface.snapshot_tool_requests()}) == 8
    assert {row["request_id"] for row in interface.snapshot_tool_telemetry()} == {
        row["request_id"] for row in interface.snapshot_tool_requests()
    }
    interface.reset_tool_telemetry()
    assert (
        not interface.snapshot_tool_requests()
        and not interface.snapshot_tool_telemetry()
    )
