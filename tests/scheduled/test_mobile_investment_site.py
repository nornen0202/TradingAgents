from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest

from tradingagents.scheduled.config import SiteSettings
from tradingagents.scheduled.mobile_site import (
    MOBILE_SCHEMA,
    PRIVATE_SCHEMA,
    assert_public_payload_safe,
    build_mobile_site,
    decode_dashboard_key,
    decrypt_private_payload,
    encrypt_private_payload,
    sanitize_public_decision_bundle,
    _private_market_payload,
)
from tradingagents.scheduled.site import _public_ticker_summaries, build_site
from tradingagents.work.packet import _compact_public_market_bundle


def _packet(market: str, *, public: bool) -> dict:
    public_row = {
        "ticker": "PUBLIC",
        "display_name": "Public candidate",
        "last_price": 123.45,
        "market_data_asof": "2026-07-16T09:00:00+09:00",
        "vwap_position_ko": "VWAP 위",
        "relative_volume": 1.2,
        "sync_summary_ko": "지수 동조",
        "data_status_ko": "현재 데이터",
        "quality": {
            "row_mode": "CONDITIONAL",
            "row_valid_until": "2026-07-16T09:30:00+09:00",
            "generated_in_current_run": True,
            "execution_ready": False,
            "conditional_strategy_ready": True,
        },
    }
    rows = [public_row]
    current = {
        "run_id": f"run-{market}",
        "started_at": "2026-07-16T09:00:00+09:00",
        "bundle": {
            "run_id": f"run-{market}",
            "market": market.upper(),
            "analysis_source_run_id": f"run-{market}",
            "execution_source_run_id": f"run-{market}",
            "quality": {
                "decision_ready": False,
                "conditional_strategy_ready": True,
                "total_rows": 1,
            },
            "strategy_table": rows,
            "transmission_scope": {"all_holdings_included": not public},
        },
        "universe_coverage": {
            "status": "COMPLETE",
            "complete": True,
            "source_run_id": f"run-{market}",
            "ticker_universe_mode": "config_only",
            "expected_holding_count": 0,
            "missing_holding_count": 0,
            "expected_watchlist_count": 1,
            "missing_watchlist_count": 0,
            "expected_analysis_count": 1,
            "missing_analysis_count": 0,
            "analysis_total_count": 1,
            "analysis_successful_count": 1,
            "analysis_failed_count": 0,
        },
    }
    if not public:
        held = {
            **public_row,
            "ticker": "SECRET.HOLD",
            "display_name": "Private holding",
            "is_held": True,
            "strategy_code": "REDUCE",
            "strategy_ko": "리스크 축소",
            "execution_condition_ko": "조건 충족 시 축소",
            "risk_condition_ko": "무효화 가격",
        }
        current["bundle"]["strategy_table"] = [held, public_row]
        current["bundle"]["quality"]["total_rows"] = 2
        current["universe_coverage"].update(
            {
                "expected_holding_count": 1,
                "expected_analysis_count": 2,
                "analysis_total_count": 2,
                "analysis_successful_count": 2,
            }
        )
        current["private_portfolio_overlay"] = {
            "privacy": "LOCAL_ONLY_DO_NOT_PUBLISH",
            "actions": [
                {
                    "canonical_ticker": "SECRET.HOLD",
                    "action_now": "REDUCE_RISK",
                    "delta_krw_now": -987654321,
                    "target_weight_now": 0.12,
                }
            ],
        }
    return {
        "surface": market,
        "event_id": f"{market}:event",
        "body": {
            "market": market.upper(),
            "source_health": "OK",
            "report_mode": "MIXED",
            "source": {"run_id": f"run-{market}", "status": "success"},
            "current": current,
            "guardrails": {
                "valid_until": "2026-07-16T09:30:00+09:00",
                "decision_ready": False,
            },
        },
    }


def test_public_bundle_excludes_held_rows_and_portfolio_actions() -> None:
    bundle = {
        "run_id": "run-us",
        "market": "US",
        "quality": {"decision_ready": True, "quality_label_ko": "장중 판단 가능"},
        "strategy_table": [
            {
                "ticker": "SECRET.HOLD",
                "is_held": True,
                "strategy_ko": "보유 유지",
                "action_now": "HOLD",
                "last_price": 10,
            },
            {
                "ticker": "PUBLIC",
                "is_held": False,
                "strategy_ko": "분할매수",
                "execution_condition_ko": "매수 조건",
                "last_price": 20,
                "quality": {"row_mode": "CONDITIONAL"},
            },
        ],
    }

    public = sanitize_public_decision_bundle(bundle)
    serialized = json.dumps(public, ensure_ascii=False)

    assert [row["ticker"] for row in public["strategy_table"]] == ["PUBLIC"]
    assert "SECRET.HOLD" not in serialized
    assert "is_held" not in serialized
    assert "strategy_ko" not in serialized
    assert "execution_condition_ko" not in serialized
    assert_public_payload_safe(public)


def test_public_safety_check_fails_closed_on_nested_private_key() -> None:
    with pytest.raises(ValueError, match="Forbidden private key"):
        assert_public_payload_safe({"markets": {"kr": {"rows": [{"is_held": True}]}}})


def test_legacy_manifest_without_public_universe_provenance_fails_closed() -> None:
    manifest = {
        "tickers": [
            {"ticker": "PUBLIC-UNKNOWN", "status": "success"},
            {"ticker": "POSSIBLE-HOLDING", "status": "success"},
        ]
    }

    assert _public_ticker_summaries(manifest) == []


def test_public_bundle_keeps_allowed_watchlist_ticker_without_revealing_held_flag() -> None:
    bundle = {
        "strategy_table": [
            {"ticker": "005930.KS", "is_held": True, "last_price": 70000, "strategy_ko": "보유 유지"},
            {"ticker": "SECRET.HOLD", "is_held": True, "last_price": 1},
        ]
    }

    public = sanitize_public_decision_bundle(bundle, allowed_tickers=["005930"])
    serialized = json.dumps(public, ensure_ascii=False)

    assert [row["ticker"] for row in public["strategy_table"]] == ["005930.KS"]
    assert "is_held" not in serialized
    assert "strategy_ko" not in serialized
    assert "SECRET.HOLD" not in serialized


def test_public_mobile_sanitizer_does_not_truncate_safe_watchlist_rows() -> None:
    tickers = [f"PUBLIC{i}" for i in range(8)]
    bundle = {
        "strategy_table": [
            {"ticker": ticker, "is_held": False, "last_price": index + 1}
            for index, ticker in enumerate(tickers)
        ]
    }

    public = sanitize_public_decision_bundle(bundle, allowed_tickers=tickers)

    assert [row["ticker"] for row in public["strategy_table"]] == tickers

    packet_bundle = _compact_public_market_bundle(bundle, allowed_tickers=tickers)
    assert [row["ticker"] for row in packet_bundle["strategy_table"]] == tickers


def test_aes_gcm_private_payload_round_trip_and_wrong_key_fails() -> None:
    key = bytes(range(32))
    payload = {
        "schema": PRIVATE_SCHEMA,
        "generated_at": "2026-07-16T09:00:00+09:00",
        "markets": {"kr": {"rows": [{"ticker": "SECRET.HOLD", "delta_krw_now": -987654321}]}},
    }
    envelope = encrypt_private_payload(payload, key=key, nonce=b"\x01" * 12)
    serialized = json.dumps(envelope)

    assert "SECRET.HOLD" not in serialized
    assert "987654321" not in serialized
    assert "plaintext_sha256" not in envelope
    assert decrypt_private_payload(envelope, key=key) == payload
    with pytest.raises(Exception):
        decrypt_private_payload(envelope, key=b"x" * 32)
    wrong_context = {
        **envelope,
        "aad": base64.urlsafe_b64encode(b"wrong-context").decode("ascii").rstrip("="),
    }
    with pytest.raises(ValueError, match="authenticated context"):
        decrypt_private_payload(wrong_context, key=key)


def test_dashboard_key_accepts_only_browser_compatible_base64url() -> None:
    key = bytes(range(32))
    encoded = base64.urlsafe_b64encode(key).decode("ascii").rstrip("=")
    assert decode_dashboard_key(encoded) == key
    with pytest.raises(ValueError, match="43-character base64url"):
        decode_dashboard_key(key.hex())
    with pytest.raises(ValueError, match="43-character base64url"):
        decode_dashboard_key("short")


def test_private_action_matches_kr_broker_and_canonical_ticker_aliases() -> None:
    packet = _packet("kr", public=False)
    packet["body"]["current"]["bundle"]["strategy_table"][0]["ticker"] = "005930.KS"
    packet["body"]["current"]["private_portfolio_overlay"]["actions"][0]["canonical_ticker"] = "005930"

    market = _private_market_payload(packet)

    assert market["rows"][0]["portfolio_action"]["action_now"] == "REDUCE_RISK"


def test_mobile_build_writes_only_ciphertext_for_private_values(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    key = bytes(range(32))
    encoded_key = base64.urlsafe_b64encode(key).decode("ascii").rstrip("=")
    monkeypatch.setenv("TRADINGAGENTS_MOBILE_DASHBOARD_KEY", encoded_key)

    def fake_packet(market: str, **kwargs) -> dict:
        return _packet(market, public=bool(kwargs.get("public")))

    monkeypatch.setattr("tradingagents.scheduled.mobile_site.build_surface_packet", fake_packet)
    status = build_mobile_site(site_dir=tmp_path / "site", archive_dir=tmp_path / "archive")
    mobile = tmp_path / "site" / "mobile"
    public_payload = json.loads((mobile / "public.json").read_text(encoding="utf-8"))
    envelope = json.loads((mobile / "private.enc.json").read_text(encoding="utf-8"))
    private_payload = decrypt_private_payload(envelope, key=key)

    assert status["private_dashboard"]["enabled"] is True
    assert public_payload["schema"] == MOBILE_SCHEMA
    assert "SECRET.HOLD" not in json.dumps(public_payload, ensure_ascii=False)
    assert private_payload["markets"]["kr"]["rows"][0]["ticker"] == "SECRET.HOLD"
    assert private_payload["markets"]["kr"]["rows"][0]["portfolio_action"]["delta_krw_now"] == -987654321
    assert private_payload["markets"]["kr"]["portfolio_action_count"] == 1
    assert private_payload["markets"]["kr"]["manifest_status"] == "success"
    assert private_payload["markets"]["kr"]["decision_ready"] is False
    assert private_payload["markets"]["kr"]["universe_coverage"]["expected_analysis_count"] == 2
    assert private_payload["markets"]["kr"]["provenance"] == {
        "surface_run_id": "run-kr",
        "manifest_run_id": "run-kr",
        "universe_source_run_id": "run-kr",
        "decision_bundle_run_id": "run-kr",
        "analysis_source_run_id": "run-kr",
        "execution_source_run_id": "run-kr",
    }

    all_public_bytes = b"\n".join(path.read_bytes() for path in mobile.rglob("*") if path.is_file())
    assert b"SECRET.HOLD" not in all_public_bytes
    assert b"987654321" not in all_public_bytes
    assert encoded_key.encode("ascii") not in all_public_bytes
    assert b"viewport-fit=cover" in (mobile / "index.html").read_bytes()
    assert b"data-valid-until" in (mobile / "index.html").read_bytes()
    mobile_css = (mobile / "mobile.css").read_text(encoding="utf-8")
    assert "env(safe-area-inset-top)" in mobile_css
    assert "overflow-wrap: anywhere" in mobile_css
    assert "main { width: 100%; max-width: 760px; min-width: 0;" in mobile_css
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in mobile_css
    assert ".cards { display: grid; grid-template-columns: minmax(0, 1fr);" in mobile_css
    assert ".market-panel, #private-root { min-width: 0; max-width: 100%; }" in mobile_css
    assert b"crypto.subtle.decrypt" in (mobile / "private.js").read_bytes()
    private_js = (mobile / "private.js").read_text(encoding="utf-8")
    assert "리스크 축소" in private_js
    assert "currency: 'KRW'" in private_js
    assert "style: 'percent'" in private_js
    assert "history.replaceState" in private_js
    assert "[A-Za-z0-9_-]{43}" in private_js
    assert "[0-9a-fA-F]{64}" not in private_js
    assert "암호화 context가 올바르지 않습니다" in private_js
    assert "데이터 만료·불완전 — 지금 주문하지 마세요" in private_js
    assert "guardrails.expired_at_build" in private_js
    assert "!Number.isFinite(marketValid)" in private_js
    assert "!Number.isFinite(valid)" in private_js
    assert "sourceHealth !== 'OK'" in private_js
    assert "coverage.status === 'COMPLETE'" in private_js
    assert "accountReady" in private_js
    assert "quality.decision_ready === true" in private_js
    assert "boundRunIds.every((value) => value === runId)" in private_js
    assert "requestedRun" in private_js


def test_mobile_build_without_key_fails_when_private_actions_exist(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TRADINGAGENTS_MOBILE_DASHBOARD_KEY", raising=False)
    monkeypatch.setattr(
        "tradingagents.scheduled.mobile_site.build_surface_packet",
        lambda market, **kwargs: _packet(market, public=bool(kwargs.get("public"))),
    )
    with pytest.raises(ValueError, match="required when private portfolio actions exist"):
        build_mobile_site(site_dir=tmp_path / "site", archive_dir=tmp_path / "archive")

    assert not (tmp_path / "site" / "mobile" / "private.enc.json").exists()


def test_mobile_research_only_build_can_omit_private_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TRADINGAGENTS_MOBILE_DASHBOARD_KEY", raising=False)

    def research_packet(market: str, **kwargs) -> dict:
        packet = _packet(market, public=bool(kwargs.get("public")))
        packet["body"]["current"].pop("private_portfolio_overlay", None)
        for row in packet["body"]["current"]["bundle"]["strategy_table"]:
            row.pop("is_held", None)
        return packet

    monkeypatch.setattr("tradingagents.scheduled.mobile_site.build_surface_packet", research_packet)
    status = build_mobile_site(site_dir=tmp_path / "site", archive_dir=tmp_path / "archive")

    assert status["private_dashboard"]["enabled"] is False
    assert not (tmp_path / "site" / "mobile" / "private.enc.json").exists()


def test_full_site_never_copies_raw_private_or_execution_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    archive = tmp_path / "archive"
    site = tmp_path / "site"
    run_id = "20260716T090000_privacy-us"
    run_dir = archive / "runs" / "2026" / run_id
    ticker_report = run_dir / "tickers" / "AAPL" / "report" / "complete_report.md"
    private_dir = run_dir / "portfolio-private"
    execution_dir = run_dir / "execution"
    ticker_report.parent.mkdir(parents=True)
    private_dir.mkdir(parents=True)
    execution_dir.mkdir(parents=True)
    ticker_report.write_text("# Public AAPL research\n", encoding="utf-8")
    secret_marker = "PRIVATE-ACCOUNT-987654321"
    (private_dir / "status.json").write_text(json.dumps({"status": "success", "profile": "private"}), encoding="utf-8")
    (private_dir / "portfolio_report.json").write_text(json.dumps({"action_now": secret_marker}), encoding="utf-8")
    (private_dir / "portfolio_report.md").write_text(secret_marker, encoding="utf-8")
    (private_dir / "summary_card.svg").write_text(f"<svg><text>{secret_marker}</text></svg>", encoding="utf-8")
    (execution_dir / "chatgpt_execution_context.json").write_text(json.dumps({"private": secret_marker}), encoding="utf-8")
    decision_bundle = {
        "run_id": run_id,
        "market": "US",
        "quality": {"decision_ready": True},
        "strategy_table": [
            {"ticker": "SECRET.HOLD", "is_held": True, "strategy_ko": "보유 유지"},
            {"ticker": "AAPL", "is_held": True, "last_price": 10, "quality": {"row_mode": "CONDITIONAL"}},
        ],
    }
    (run_dir / "decision_bundle_v2.json").write_text(json.dumps(decision_bundle), encoding="utf-8")
    manifest = {
        "version": 1,
        "run_id": run_id,
        "status": "success",
        "started_at": "2026-07-16T09:00:00+09:00",
        "summary": {"total_tickers": 1, "successful_tickers": 1, "failed_tickers": 0},
        "settings": {"output_language": "Korean", "market": "US", "run_mode": "full"},
        "active_universe": {
            "expected_watchlist_tickers": ["AAPL"],
            "scanner_candidates": [],
            "expected_holding_tickers": ["SECRET.HOLD"],
            "missing_holding_tickers": ["FRESH.NEW.PRIVATE"],
            "missing_analysis_tickers": ["ANALYSIS.MISSING.PRIVATE"],
            "fresh_snapshot_drift": {
                "status": "VERIFIED",
                "added_holding_tickers": ["DRIFT.ADDED.PRIVATE"],
                "removed_holding_tickers": ["DRIFT.REMOVED.PRIVATE"],
            },
        },
        "portfolio": {
            "status": "success",
            "profile": "private",
            "private_coverage_snapshot": {
                "holding_set_complete": True,
                "canonical_holding_tickers": ["SNAPSHOT.HOLD.PRIVATE"],
            },
            "artifacts": {
                "portfolio_report_json": "portfolio-private/portfolio_report.json",
                "portfolio_report_md": "portfolio-private/portfolio_report.md",
                "summary_card_svg": "portfolio-private/summary_card.svg",
            },
        },
        "execution": {
            "artifacts": {"chatgpt_execution_context_json": "execution/chatgpt_execution_context.json"},
            "overlay_phase": {"selected_checkpoints": []},
            "notes": ["RAW-EXECUTION-NOTE-SECRET.HOLD"],
        },
        "warnings": ["RAW-WARNING-PRIVATE-TICKER-SECRET.HOLD"],
        "decision_bundle": {
            "decision_ready": True,
            "artifacts": {"decision_bundle_v2_json": "decision_bundle_v2.json"},
        },
        "tickers": [
            {
                "ticker": "AAPL",
                "status": "success",
                "analysis_date": "2026-07-16",
                "trade_date": "2026-07-16",
                "decision": {"action": "HOLD", "confidence": 0.5},
                "error": "PRIVATE-ERROR-C:/Users/JY/account-SECRET.HOLD",
                "is_held": True,
                "portfolio_action": {
                    "action_now": "REDUCE_NOW",
                    "rationale": "PUBLIC-TICKER-PRIVATE-ACTION-MARKER",
                    "delta_krw_now": -123456789,
                },
                "action_lift_audit": {
                    "lift_status": "ACTION_LIFT_FAILURE",
                    "next_valid_action": "PUBLIC-TICKER-PRIVATE-LIFT-MARKER",
                },
                "artifacts": {"report_markdown": "tickers/AAPL/report/complete_report.md"},
            },
            {
                "ticker": "SECRET.HOLD",
                "status": "success",
                "analysis_date": "2026-07-16",
                "trade_date": "2026-07-16",
                "decision": {"action": "HOLD", "confidence": 0.5},
                "artifacts": {},
            },
        ],
    }
    (run_dir / "run.json").write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setenv(
        "TRADINGAGENTS_MOBILE_DASHBOARD_KEY",
        base64.urlsafe_b64encode(bytes(range(32))).decode("ascii").rstrip("="),
    )

    build_site(archive, site, SiteSettings(title="TA", subtitle="Daily"))

    relative_files = {path.relative_to(site).as_posix() for path in site.rglob("*") if path.is_file()}
    forbidden_names = {
        "portfolio_report.json",
        "portfolio_report.md",
        "summary_card.svg",
        "strategy_table_ko.md",
        "decision_bundle_v2.json",
        "chatgpt_execution_context.json",
    }
    assert not {Path(name).name for name in relative_files} & forbidden_names
    all_bytes = b"\n".join(path.read_bytes() for path in site.rglob("*") if path.is_file())
    assert secret_marker.encode() not in all_bytes
    assert b"PUBLIC-TICKER-PRIVATE-ACTION-MARKER" not in all_bytes
    assert b"PUBLIC-TICKER-PRIVATE-LIFT-MARKER" not in all_bytes
    assert b"123456789" not in all_bytes
    assert b"RAW-WARNING-PRIVATE-TICKER" not in all_bytes
    assert b"RAW-EXECUTION-NOTE" not in all_bytes
    assert b"PRIVATE-ERROR-C:/Users/JY" not in all_bytes
    assert b"SECRET.HOLD" not in all_bytes
    for private_ticker_marker in (
        b"FRESH.NEW.PRIVATE",
        b"ANALYSIS.MISSING.PRIVATE",
        b"DRIFT.ADDED.PRIVATE",
        b"DRIFT.REMOVED.PRIVATE",
        b"SNAPSHOT.HOLD.PRIVATE",
    ):
        assert private_ticker_marker not in all_bytes
    assert not (site / "runs" / run_id / "SECRET.HOLD.html").exists()
    assert not (site / "downloads").exists()
    assert "개인 계좌 자료는 공개하지 않습니다" in (
        site / "runs" / run_id / "portfolio.html"
    ).read_text(encoding="utf-8")
    sanitized_latest = json.loads((site / "latest" / "us" / "decision_bundle.json").read_text(encoding="utf-8"))
    assert [row["ticker"] for row in sanitized_latest["strategy_table"]] == ["AAPL"]
    assert "is_held" not in json.dumps(sanitized_latest)
    feed = json.loads((site / "feed.json").read_text(encoding="utf-8"))
    serialized_feed = json.dumps(feed, ensure_ascii=False)
    assert feed["runs"][0]["ticker_count"] == 1
    assert feed["runs"][0]["summary"]["total_tickers"] == 1
    assert "portfolio" not in feed["runs"][0]
    assert "FRESH.NEW.PRIVATE" not in serialized_feed
    assert "SNAPSHOT.HOLD.PRIVATE" not in serialized_feed
