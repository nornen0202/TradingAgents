import copy
import json

import pytest

from tradingagents.dataflows import institutional as module


def payload():
    return {"timestamp_envelope": {"published_at": "2026-06-08T10:00:00Z", "observed_at": "2026-06-08T11:00:00Z"},
            "estimate_revision_direction": "positive",
            "source_refs": [{"provider": "factset", "date": "2026-06-08", "confidence": .9}],
            "evidence_ledger": [{"claim": "Dated fixture evidence", "quality": .9}],
            "earnings_event_pack": {"transcript_available": True}}


@pytest.fixture
def imported(tmp_path, monkeypatch):
    config = {"institutional_data_dir": str(tmp_path)}
    monkeypatch.setattr(module, "get_config", lambda: config)
    monkeypatch.setattr(module, "route_to_vendor", lambda *a, **k: pytest.fail("Unexpected external API call"))
    path = tmp_path / "factset/MSFT/estimates.json"
    path.parent.mkdir(parents=True)
    return path, config


@pytest.mark.parametrize("fault", [None, "empty", "no_envelope", "no_publication", "no_observation",
    "future_publication", "future_observation", "bad_publication", "naive_observation", "backwards",
    "amended_old_period", "nested_future", "nested_missing", "nested_invalid", "future_date"])
def test_imports_are_filtered_before_routing_evidence_and_quality(imported, fault):
    path, _ = imported
    baseline = module.build_public_equity_intelligence(ticker="MSFT", curr_date="2026-06-08")
    value = payload()
    envelope = value["timestamp_envelope"]
    if fault == "empty": value = {}
    if fault == "no_envelope": value.pop("timestamp_envelope")
    if fault == "no_publication": envelope.pop("published_at")
    if fault == "no_observation": envelope.pop("observed_at")
    if fault == "future_publication": envelope["published_at"] = "2026-06-09T10:00:00Z"
    if fault == "future_observation": envelope["observed_at"] = "2026-06-09T10:00:00Z"
    if fault == "bad_publication": envelope["published_at"] = "2026-02-30T10:00:00Z"
    if fault == "naive_observation": envelope["observed_at"] = "2026-06-08T11:00:00"
    if fault == "backwards": envelope["observed_at"] = "2026-06-08T09:00:00Z"
    if fault == "amended_old_period":
        value.update(period_end="2025-12-31", amended_at="2026-06-09T10:00:00Z")
    if fault == "nested_future": value["evidence_ledger"][0]["published_at"] = "2026-06-09T10:00:00Z"
    if fault == "nested_missing": value["evidence_ledger"][0]["published_at"] = None
    if fault == "nested_invalid": value["evidence_ledger"][0]["date"] = "invalid"
    if fault == "future_date": value["source_refs"][0]["date"] = "2026-06-09"
    path.write_text(json.dumps(value), encoding="utf-8")
    before = path.read_bytes()
    routed = module.route_to_institutional_provider(module.CAP_ESTIMATES, "MSFT", "2026-06-08")
    result = module.build_public_equity_intelligence(ticker="MSFT", curr_date="2026-06-08")
    if fault is None:
        assert routed["status"] == "success" and routed["mode"] == "imported"
        assert result["source_quality_score"] > baseline["source_quality_score"]
        assert result["earnings_event_pack"]["transcript_available"]
    else:
        assert routed["status"] == "unavailable"
        assert result["source_quality_score"] == baseline["source_quality_score"]
        assert result["evidence_ledger"] == baseline["evidence_ledger"]
        assert result["coverage"] == baseline["coverage"]
        assert result["provider_catalog"] == baseline["provider_catalog"]
    assert path.read_bytes() == before


@pytest.mark.parametrize("day", [None, "", "bad", "2026-02-30", "9999-01-01"])
def test_invalid_analysis_date_never_defaults_to_today_or_calls_api(imported, day):
    with pytest.raises(ValueError):
        module.route_to_institutional_provider(module.CAP_FINANCIALS, "MSFT", day)


@pytest.mark.parametrize("scoped", ["2026-06-07", "2026-06-08T09:00:00Z"])
def test_execution_context_caps_requested_date_before_imports_and_scores(imported, scoped):
    path, config = imported
    path.write_text(json.dumps(payload()))
    config["analysis_as_of"] = scoped
    result = module.route_to_institutional_provider(module.CAP_ESTIMATES, "MSFT", "2026-06-08")
    assert result["status"] == "unavailable"


def test_free_adapter_receives_scoped_date_without_wall_clock_fallback(imported, monkeypatch):
    _, config = imported
    config["analysis_as_of"] = "2026-06-07"
    calls = []
    monkeypatch.setattr(module, "route_to_vendor", lambda *a: calls.append(a) or "fixture response")
    result = module.route_to_institutional_provider(module.CAP_FINANCIALS, "MSFT", "2026-06-08")
    assert result["status"] == "success" and result["asof"] == "2026-06-07"
    assert calls == [("get_fundamentals", "MSFT", "2026-06-07")]


@pytest.mark.parametrize("ticker,published,observed,expected", [
    ("005930", "2026-06-08T15:00:00Z", "2026-06-08T15:01:00Z", False),
    ("MSFT", "2026-06-09T02:00:00Z", "2026-06-09T03:00:00Z", True)])
def test_import_cutoff_uses_market_day_not_utc_day(imported, ticker, published, observed, expected):
    value = payload()
    value["timestamp_envelope"] = {"published_at": published, "observed_at": observed}
    _, cutoff = module._analysis_cutoff("2026-06-08", ticker)
    assert module._import_available(value, cutoff) is expected


def test_scheduled_future_event_is_distinct_from_future_publication(imported):
    value = copy.deepcopy(payload())
    value["event_records"] = [{"scheduled_at": "2026-07-01T12:00:00Z"}]
    _, cutoff = module._analysis_cutoff("2026-06-08", "MSFT")
    assert module._import_available(value, cutoff)


def test_other_ticker_imports_do_not_change_analysis_provider_availability(imported):
    path, _ = imported
    other = path.parent.parent / "AAPL" / path.name
    other.parent.mkdir()
    baseline = module.build_public_equity_intelligence(ticker="MSFT", curr_date="2026-06-08")
    other.write_text(json.dumps(payload()))
    result = module.build_public_equity_intelligence(ticker="MSFT", curr_date="2026-06-08")
    assert result["provider_catalog"] == baseline["provider_catalog"]
