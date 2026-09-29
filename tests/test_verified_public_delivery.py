import hashlib
import json
from datetime import datetime, timedelta, timezone

import pytest

from tradingagents.scheduled.ai_context import render_payload
from tradingagents.work.public_delivery import (
    PublicDeliveryError, prepare_public_delivery, validate_input,
)
from tradingagents.work.runtime import WorkRuntimeError, validate_account_execution

NOW = datetime(2026, 7, 11, 10, 10, tzinfo=timezone.utc)
SHA = "a" * 40


def payload():
    return {
        "schema": "tradingagents.ai-context/v1", "market": "kr",
        "generated_at": "2026-07-11T10:05:00Z",
        "freshness_receipt": {"analysis_completed_at": "2026-07-11T09:00:00Z",
                              "analysis_lineage_status": "RESOLVED",
                              "market_data_oldest_at": "2026-07-11T10:00:00Z",
                              "market_data_latest_at": "2026-07-11T10:00:00Z"},
        "account": {"status": "available", "snapshot_health": "VALID",
                    "as_of": "2026-07-11T10:00:00Z",
                    "summary": {"position_count": 1, "available_cash_krw": 0, "total_equity_krw": 100},
                    "positions": [{"ticker": "TEST", "quantity": 1, "sellable_quantity": 1}]},
        "rows": [{"ticker": "TEST", "market_data_asof": "2026-07-11T10:00:00Z",
                  "quality_at_build": {"row_valid_until": "2026-07-11T10:30:00Z"}}],
        "report": {},
    }


def transport(value, *, corrupt=False, move=False, inconsistent_text=False):
    data = {"json": json.dumps(value).encode(), "txt": render_payload(value).encode()}
    if inconsistent_text:
        data["txt"] += b" extra"
    manifest = {"schema": value["schema"], "generated_at": value["generated_at"], "files": {
        f"kr/latest.{ext}": {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        for ext, raw in data.items()
    }}
    urls = []
    count = 0
    def fetch(url):
        nonlocal count
        urls.append(url)
        if "/git/ref/" in url:
            count += 1
            return json.dumps({"ref": "refs/heads/public-context", "object": {
                "sha": ("b" if move and count % 2 == 0 else "a") * 40, "type": "commit"}}).encode()
        assert f"/{SHA}/" in url, "Mutable data URL used"
        if url.endswith("/manifest.json"):
            return json.dumps(manifest).encode()
        return data[url.rsplit(".", 1)[1]] + (b"bad" if corrupt else b"")
    return fetch, urls


def test_nonce_discovery_pins_all_files_and_verifies_bytes():
    fetch, urls = transport(payload())
    result = prepare_public_delivery("kr", fetcher=fetch, now=NOW)
    assert result["status"] == "VERIFIED_CURRENT_INPUT"
    assert result["personalized_input"]["account"]["positions"][0]["quantity"] == 1
    assert result["not_order_authorization"] is True
    refs = [url for url in urls if "/git/ref/" in url]
    assert len(refs) == 2 and refs[0] != refs[1]
    assert all("request_id=" in url for url in refs)


@pytest.mark.parametrize("corrupt,move,inconsistent", [(True, False, False), (False, True, False), (False, False, True)])
def test_corruption_moving_head_and_text_disagreement_fail_closed(corrupt, move, inconsistent):
    fetch, _ = transport(payload(), corrupt=corrupt, move=move, inconsistent_text=inconsistent)
    with pytest.raises(PublicDeliveryError):
        prepare_public_delivery("kr", fetcher=fetch, now=NOW)


def test_stale_successful_http_response_never_returns_personalized_input():
    fetch, _ = transport(payload())
    result = prepare_public_delivery("kr", fetcher=fetch, now=NOW + timedelta(days=1))
    assert result["status"] == "REFERENCE_ONLY"
    assert result["personalized_input"] is None and result["context_text"] is None
    assert "ACCOUNT_EXPIRED_OR_INVALID" in result["blockers"]


@pytest.mark.parametrize("field,value,reason", [
    ("as_of", None, "ACCOUNT_EXPIRED_OR_INVALID"),
    ("as_of", "2026-07-11T10:11:00Z", "ACCOUNT_EXPIRED_OR_INVALID"),
    ("as_of", "2026-07-11T10:00:00", "ACCOUNT_EXPIRED_OR_INVALID"),
    ("snapshot_health", None, "ACCOUNT_UNVERIFIED"),
])
def test_bad_account_clock_and_health_are_blocked(field, value, reason):
    data = payload()
    data["account"][field] = value
    assert reason in validate_input(data, market="kr", now=NOW)


def test_missing_cash_duplicate_holdings_and_wrong_market_are_blocked():
    data = payload()
    data["account"]["summary"]["available_cash_krw"] = None
    data["account"]["positions"] *= 2
    failures = validate_input(data, market="us", now=NOW)
    assert "ACCOUNT_CASH_OR_EQUITY_UNVERIFIED" in failures
    assert "ACCOUNT_COVERAGE_INVALID" in failures
    assert "SCHEMA_OR_MARKET_MISMATCH" in failures


def test_missing_and_expired_rows_are_blocked():
    data = payload()
    data["rows"] = []
    assert "HOLDING_ROWS_MISSING_OR_DUPLICATE" in validate_input(data, market="kr", now=NOW)
    data = payload()
    data["rows"][0]["quality_at_build"]["row_valid_until"] = NOW.isoformat()
    assert "ROW_VALIDITY_EXPIRED_OR_INVALID" in validate_input(data, market="kr", now=NOW)


def test_network_disabled_does_not_fall_back_to_saved_chat_or_latest():
    urls = []
    def disabled(url):
        urls.append(url)
        raise OSError("DisabledError")
    with pytest.raises(OSError, match="DisabledError"):
        prepare_public_delivery("kr", fetcher=disabled, now=NOW)
    assert len(urls) == 1


@pytest.mark.parametrize("readiness", ["READY_NOW", "WAIT_FOR_TRIGGER", "ready_now"])
def test_publish_account_guard_rejects_stale_missing_future_and_invalid(readiness):
    strategies = [{"execution": {"readiness": readiness}}]
    good = {"account_as_of": "2026-07-11T10:00:00Z", "account_snapshot_health": "VALID"}
    validate_account_execution(strategies, good, now=NOW)
    for change in ({"account_as_of": None}, {"account_as_of": "2026-07-11T09:40:00Z"},
                   {"account_as_of": "2026-07-11T10:11:00Z"}, {"account_snapshot_health": "INVALID"}):
        with pytest.raises(WorkRuntimeError, match="VALID account"):
            validate_account_execution(strategies, {**good, **change}, now=NOW)
    validate_account_execution([{"execution": {"readiness": "NEEDS_LIVE_RECHECK"}}], {}, now=NOW)
