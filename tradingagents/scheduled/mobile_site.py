from __future__ import annotations

import html
import json
import re
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

from tradingagents.agents.utils.instrument_resolver import (
    InstrumentResolutionError,
    resolve_instrument,
)
from tradingagents.work.packet import build_surface_packet
from tradingagents.work.runtime import WorkRuntimeError, validate_work_report


MOBILE_SCHEMA = "tradingagents.mobile-dashboard/v1"
STRATEGY_SCHEMA = "tradingagents.mobile-strategy/v1"
MARKETS = ("kr", "us")

_PUBLIC_ROW_FIELDS = (
    "ticker",
    "display_name",
    "last_price",
    "market_data_asof",
    "session_vwap",
    "vwap_distance_pct",
    "vwap_position_ko",
    "relative_volume",
    "trading_value",
    "price_change_pct",
    "spread_bps",
    "day_high",
    "day_low",
    "sync_summary_ko",
    "data_status_ko",
    "reason_codes_ko",
    "quality",
)

_PRIVATE_ROW_FIELDS = (
    "ticker",
    "display_name",
    "is_held",
    "sector",
    "strategy_code",
    "strategy_ko",
    "last_price",
    "market_data_asof",
    "session_vwap",
    "vwap_distance_pct",
    "vwap_position_ko",
    "relative_volume",
    "trading_value",
    "price_change_pct",
    "spread_bps",
    "day_high",
    "day_low",
    "sync_summary_ko",
    "execution_condition_ko",
    "risk_condition_ko",
    "data_status_ko",
    "decision_state_ko",
    "execution_timing_ko",
    "display_priority",
    "table_priority",
    "portfolio_priority",
    "universe_role",
    "candidate_source",
    "is_watchlist",
    "is_scanner_candidate",
    "reason_codes_ko",
    "quality",
)

_PRIVATE_ACTION_FIELDS = (
    "canonical_ticker",
    "confidence",
    "action_now",
    "delta_krw_now",
    "target_weight_now",
    "action_if_triggered",
    "trigger_conditions",
    "delta_krw_if_triggered",
    "target_weight_if_triggered",
    "strategy_state",
    "execution_feasibility_now",
    "portfolio_relative_action",
    "risk_action",
    "risk_action_level",
    "risk_condition",
    "invalidation_condition",
    "sell_side_category",
    "sell_intent",
    "sell_size_plan",
    "position_metrics",
    "profit_taking_plan",
    "priority",
    "rationale",
    "reason_codes",
    "gate_reasons",
)

_FORBIDDEN_PUBLIC_KEYS = {
    "is_held",
    "private_portfolio_overlay",
    "actions",
    "action_now",
    "action_if_triggered",
    "delta_krw_now",
    "delta_krw_if_triggered",
    "target_weight_now",
    "target_weight_if_triggered",
    "position_metrics",
    "account_id",
    "account_no",
    "broker_account_id",
    "quantity",
    "market_value",
    "average_price",
    "avg_price",
}

_FORBIDDEN_STRATEGY_IDENTIFIER_KEYS = {
    "account_id",
    "account_name",
    "account_no",
    "account_number",
    "access_token",
    "api_key",
    "broker_account_id",
    "broker_account_no",
    "cano",
    "acnt_prdt_cd",
    "client_id",
    "credentials",
    "customer_id",
    "custtype",
    "odno",
    "order_id",
    "order_no",
    "order_number",
    "order_reference",
    "password",
    "refresh_token",
    "secret",
    "token",
    "user_id",
    "username",
}

_INVESTOR_ROW_STATES = {
    "IMMEDIATE": ("READY", "실시간 조건 확인"),
    "CONDITIONAL": ("CONDITIONAL", "조건 확인 필요"),
    "BLOCKED_STALE": ("RECHECK", "주문 전 재확인"),
    "BLOCKED_INCOMPLETE": ("UNAVAILABLE", "데이터 재확인"),
    "MISSING": ("UNAVAILABLE", "데이터 재확인"),
}
_MOBILE_MACHINE_STATUS_REPLACEMENTS = {
    "BLOCKED_STALE": "RECHECK_REQUIRED",
    "BLOCKED_INCOMPLETE": "UNAVAILABLE",
}
_STRATEGY_SENSITIVE_TEXT_PATTERNS = (
    re.compile(
        r"(?i)(?:\baccount\s*(?:number|no\.?|id)|계좌\s*(?:번호|ID)|\bCANO|\bACNT_PRDT_CD|"
        r"\bODNO|\border[_\s-]?(?:id|no|number|reference)|\bclient[_\s-]?id|"
        r"\bcustomer[_\s-]?id|\bbroker[_\s-]?account[_\s-]?id)"
        r"(?:\s*[:=#]\s*|\s+)(?=[A-Z0-9._-]{2,}(?:\b|$))(?=[A-Z0-9._-]*\d)[A-Z0-9._-]+"
    ),
    re.compile(
        r"(?i)\b(?:(?:(?:access|refresh|bot)[_\s-]?)?token|"
        r"api[_\s-]?key|app[_\s-]?(?:key|secret)|password|authorization)"
        r"(?:\s*[:=#]\s*|\s+)[A-Z0-9._-]{3,}"
    ),
    re.compile(
        r"(?i)(?:[A-Z]:[\\/]+[^\r\n<>|\"']+|\\\\[^\\/\s]+[\\/]+[^\r\n<>|\"']+|"
        r"/(?:Users|home|var|tmp|opt|etc|mnt)/[^\s<>\"']+)"
    ),
)


def build_mobile_site(
    *,
    site_dir: Path,
    archive_dir: Path,
    public_base_url: str = "",
) -> dict[str, Any]:
    """Build the public research hub and a plaintext, action-only strategy view.

    The strategy artifact deliberately contains the investment actions requested
    for the mobile report, while raw broker/account identifiers are removed.
    """

    site_root = Path(site_dir)
    mobile_root = site_root / "mobile"
    mobile_root.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now().astimezone().isoformat()

    public_payload = {
        "schema": MOBILE_SCHEMA,
        "generated_at": generated_at,
        "privacy": "PUBLIC_RESEARCH_ONLY_NO_PORTFOLIO_MEMBERSHIP_OR_ACTIONS",
        "markets": {},
    }
    strategy_payload = {
        "schema": STRATEGY_SCHEMA,
        "generated_at": generated_at,
        "privacy": "PLAINTEXT_ACTION_DATA_NO_RAW_ACCOUNT_IDENTIFIERS",
        "markets": {},
    }

    for market in MARKETS:
        public_packet = _read_public_work_packet(site_root, market)
        if not public_packet:
            public_packet = build_surface_packet(market, archive_dir=archive_dir, public=True)
        private_packet = build_surface_packet(market, archive_dir=archive_dir, public=False)
        public_payload["markets"][market] = _public_market_payload(public_packet)
        market_payload = _private_market_payload(private_packet)
        integrated_report = _load_latest_work_report(
            Path(archive_dir),
            market,
            current_packet=private_packet,
        )
        current_integrated_report: dict[str, Any] = {}
        if integrated_report:
            lineage = integrated_report.get("lineage") if isinstance(integrated_report.get("lineage"), dict) else {}
            if lineage.get("status") in {"CURRENT_PACKET", "CURRENT_ANALYSIS_LINEAGE"}:
                market_payload["integrated_report"] = integrated_report
                current_integrated_report = integrated_report
            else:
                # A valid content-addressed report can remain useful as an
                # analysis-time reference, but it must not rank or enrich the
                # current run's action cards without a proved source lineage.
                market_payload["reference_report"] = integrated_report
        _annotate_market_roles(
            market_payload,
            archive_dir=Path(archive_dir),
            integrated_report=current_integrated_report,
        )
        strategy_payload["markets"][market] = market_payload

    public_payload = _normalize_mobile_machine_values(public_payload)
    strategy_payload = _normalize_mobile_machine_values(
        _strip_strategy_identifiers(strategy_payload)
    )
    assert_public_payload_safe(public_payload)
    assert_strategy_payload_safe(strategy_payload)
    _write_json(mobile_root / "public.json", public_payload)
    _write_json(mobile_root / "strategy.json", strategy_payload)
    _write_text(mobile_root / "index.html", _public_html(public_payload, public_base_url=public_base_url))
    _write_text(mobile_root / "mobile.css", _MOBILE_CSS)
    _write_text(mobile_root / "strategy.html", _private_html())
    # Keep the old URL as a public, plaintext compatibility alias for existing
    # Telegram messages and saved bookmarks.
    _write_text(mobile_root / "private.html", _private_html())
    _write_text(mobile_root / "private.js", _PRIVATE_JS)
    _write_text(site_root / "strategy.html", _private_html(desktop=True))
    _write_text(
        site_root / "robots.txt",
        "User-agent: *\nAllow: /\n",
    )
    _write_text(
        site_root / "llms.txt",
        _llms_text(public_base_url=public_base_url, generated_at=generated_at),
    )
    if str(public_base_url or "").strip():
        _write_text(site_root / "sitemap.xml", _sitemap_xml(public_base_url))
    # Delete artifacts produced by the retired encryption implementation even
    # when callers build into an existing directory without clearing it first.
    (mobile_root / "private.enc.json").unlink(missing_ok=True)
    (mobile_root / "private.json").unlink(missing_ok=True)

    status = {
        "schema": MOBILE_SCHEMA,
        "generated_at": generated_at,
        "public_url": _join_url(public_base_url, "mobile/"),
        "strategy_url": _join_url(public_base_url, "mobile/strategy.html"),
        "desktop_strategy_url": _join_url(public_base_url, "strategy.html"),
        "legacy_strategy_url": _join_url(public_base_url, "mobile/private.html"),
        "strategy_payload_url": _join_url(public_base_url, "mobile/strategy.json"),
        "private_dashboard": {
            "enabled": True,
            "storage": "PLAINTEXT_ACTION_DATA",
            "raw_account_identifiers_omitted": True,
        },
    }
    _write_json(mobile_root / "status.json", status)
    return status


def sanitize_public_decision_bundle(
    bundle: dict[str, Any],
    *,
    max_candidates: int | None = None,
    allowed_tickers: Iterable[Any] | None = None,
) -> dict[str, Any]:
    """Return a fail-closed public recovery bundle.

    With an explicit public watchlist/scanner allow-list, those research rows are
    retained regardless of ownership while all membership fields are removed.
    Without that contract, held rows fail closed. Portfolio-derived strategies
    and execution conditions are always excluded.
    """

    if not isinstance(bundle, dict) or not bundle:
        return {}
    allowed = (
        {identity for value in allowed_tickers for identity in _ticker_identity_keys(value)}
        if allowed_tickers is not None
        else None
    )
    candidate_limit = None if max_candidates is None else max(0, int(max_candidates))
    rows: list[dict[str, Any]] = []
    for source in bundle.get("strategy_table") or []:
        if candidate_limit is not None and len(rows) >= candidate_limit:
            break
        if not isinstance(source, dict):
            continue
        identities = set(_ticker_identity_keys(source.get("ticker")))
        if allowed is None:
            if source.get("is_held") is True:
                continue
        elif not identities.intersection(allowed):
            continue
        row = {key: source.get(key) for key in _PUBLIC_ROW_FIELDS if source.get(key) is not None}
        row["display_name"] = _display_name_for(row.get("ticker"), row.get("display_name"))
        row["quality"] = _public_quality(source.get("quality"))
        rows.append(row)
    quality = bundle.get("quality") if isinstance(bundle.get("quality"), dict) else {}
    result = {
        key: bundle.get(key)
        for key in (
            "artifact_type",
            "version",
            "run_id",
            "market",
            "generated_at",
            "analysis_source_run_id",
            "execution_source_run_id",
            "checkpoint",
            "checkpoint_timezone",
        )
        if bundle.get(key) is not None
    }
    result.update(
        {
            "quality": {
                key: quality.get(key)
                for key in (
                    "report_mode",
                    "decision_ready",
                    "conditional_strategy_ready",
                    "quality_label_ko",
                    "fresh_row_ratio",
                    "conditional_row_ratio",
                )
                if quality.get(key) is not None
            }
            | {"portfolio_membership_omitted": True},
            "strategy_table": rows,
            "transmission_scope": {
                "public_recovery_only": True,
                "portfolio_membership_omitted": True,
                "portfolio_actions_omitted": True,
                "transmitted_research_candidate_count": len(rows),
            },
        }
    )
    assert_public_payload_safe(result)
    return result


def assert_public_payload_safe(value: Any, *, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).strip().lower()
            if normalized in _FORBIDDEN_PUBLIC_KEYS:
                raise ValueError(f"Forbidden private key in public mobile payload at {path}.{key}")
            assert_public_payload_safe(item, path=f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            assert_public_payload_safe(item, path=f"{path}[{index}]")


def assert_strategy_payload_safe(value: Any, *, path: str = "$") -> None:
    """Reject raw identifiers if a future payload field bypasses the allow-lists."""

    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).strip().lower()
            if normalized in _FORBIDDEN_STRATEGY_IDENTIFIER_KEYS:
                raise ValueError(f"Forbidden account identifier in mobile strategy payload at {path}.{key}")
            assert_strategy_payload_safe(item, path=f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            assert_strategy_payload_safe(item, path=f"{path}[{index}]")
    elif isinstance(value, str) and _find_sensitive_strategy_text(value):
        raise ValueError(f"Forbidden identifier value in mobile strategy payload at {path}")


def _strip_strategy_identifiers(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_strategy_identifiers(item)
            for key, item in value.items()
            if str(key).strip().lower() not in _FORBIDDEN_STRATEGY_IDENTIFIER_KEYS
        }
    if isinstance(value, list):
        return [_strip_strategy_identifiers(item) for item in value]
    if isinstance(value, str):
        return _redact_account_identifiers(value)
    return value


def _redact_account_identifiers(value: str) -> str:
    """Redact labelled identifiers, credentials and local user paths."""

    text = str(value or "")
    text = _STRATEGY_SENSITIVE_TEXT_PATTERNS[0].sub("[식별정보 제외]", text)
    text = _STRATEGY_SENSITIVE_TEXT_PATTERNS[1].sub("[비밀정보 제외]", text)
    return _STRATEGY_SENSITIVE_TEXT_PATTERNS[2].sub("[로컬 경로 제외]", text)


def _find_sensitive_strategy_text(value: str) -> str | None:
    for pattern in _STRATEGY_SENSITIVE_TEXT_PATTERNS:
        if pattern.search(str(value or "")):
            return pattern.pattern
    return None


def _normalize_mobile_machine_values(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _normalize_mobile_machine_values(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_mobile_machine_values(item) for item in value]
    if isinstance(value, str):
        text = value
        for machine_value, investor_value in _MOBILE_MACHINE_STATUS_REPLACEMENTS.items():
            text = re.sub(
                re.escape(machine_value),
                investor_value,
                text,
                flags=re.IGNORECASE,
            )
        return text
    return value


def _read_public_work_packet(site_root: Path, market: str) -> dict[str, Any]:
    path = site_root / "work" / "v1" / market / "latest.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _public_market_payload(packet: dict[str, Any]) -> dict[str, Any]:
    body = packet.get("body") if isinstance(packet.get("body"), dict) else {}
    current = body.get("current") if isinstance(body.get("current"), dict) else {}
    bundle = current.get("bundle") if isinstance(current.get("bundle"), dict) else {}
    rows = []
    for source in bundle.get("strategy_table") or []:
        if not isinstance(source, dict) or source.get("is_held") is True:
            continue
        row = {key: source.get(key) for key in _PUBLIC_ROW_FIELDS if source.get(key) is not None}
        row["display_name"] = _display_name_for(row.get("ticker"), row.get("display_name"))
        row["quality"] = _public_quality(source.get("quality"))
        rows.append(row)
    result = {
        "market": str(body.get("market") or packet.get("surface") or "").upper(),
        "event_id": packet.get("event_id"),
        "source_health": body.get("source_health") or "MISSING",
        "report_mode": body.get("report_mode") or "RESEARCH",
        "run_id": current.get("run_id"),
        "started_at": current.get("started_at"),
        "source": _safe_mapping(body.get("source"), ("run_id", "last_run_at", "status")),
        "guardrails": _safe_mapping(
            body.get("guardrails"),
            ("valid_until", "expired_at_build", "decision_ready", "conditional_strategy_ready", "report_mode"),
        ),
        "quality": _safe_mapping(
            bundle.get("quality"),
            (
                "report_mode",
                "decision_ready",
                "conditional_strategy_ready",
                "quality_label_ko",
                "fresh_row_ratio",
                "conditional_row_ratio",
            ),
        ),
        "rows": rows,
        "coverage": {
            "research_candidate_count": len(rows),
            "portfolio_membership_omitted": True,
            "portfolio_actions_omitted": True,
        },
    }
    assert_public_payload_safe(result)
    return result


def _private_market_payload(packet: dict[str, Any]) -> dict[str, Any]:
    body = packet.get("body") if isinstance(packet.get("body"), dict) else {}
    current = body.get("current") if isinstance(body.get("current"), dict) else {}
    bundle = current.get("bundle") if isinstance(current.get("bundle"), dict) else {}
    quality = bundle.get("quality") if isinstance(bundle.get("quality"), dict) else {}
    source_metadata = body.get("source") if isinstance(body.get("source"), dict) else {}
    universe_coverage = (
        current.get("universe_coverage")
        if isinstance(current.get("universe_coverage"), dict)
        else {}
    )
    safe_universe_coverage = _safe_mapping(
        universe_coverage,
        (
            "status",
            "complete",
            "source_run_id",
            "ticker_universe_mode",
            "account_snapshot_status",
            "expected_holding_count",
            "missing_holding_count",
            "expected_watchlist_count",
            "missing_watchlist_count",
            "expected_analysis_count",
            "missing_analysis_count",
            "analysis_total_count",
            "analysis_successful_count",
            "analysis_failed_count",
        ),
    )
    safe_quality = _safe_mapping(
        quality,
        (
            "decision_ready",
            "conditional_strategy_ready",
            "quality_label_ko",
            "fresh_row_ratio",
            "conditional_row_ratio",
            "total_rows",
        ),
    )
    overlay = current.get("private_portfolio_overlay") if isinstance(current.get("private_portfolio_overlay"), dict) else {}
    actions = []
    for action_source in overlay.get("actions") or []:
        if isinstance(action_source, dict):
            actions.append(
                {
                    key: action_source.get(key)
                    for key in _PRIVATE_ACTION_FIELDS
                    if action_source.get(key) is not None
                }
            )
    action_by_ticker: dict[str, dict[str, Any]] = {}
    for item in actions:
        for identity in _ticker_identity_keys(item.get("canonical_ticker")):
            action_by_ticker.setdefault(identity, item)
    rows = []
    for row_source in bundle.get("strategy_table") or []:
        if not isinstance(row_source, dict):
            continue
        row = {
            key: row_source.get(key)
            for key in _PRIVATE_ROW_FIELDS
            if row_source.get(key) is not None
        }
        row["display_name"] = _display_name_for(row.get("ticker"), row.get("display_name"))
        row["quality"] = _public_quality(row_source.get("quality"))
        action = next(
            (action_by_ticker[key] for key in _ticker_identity_keys(row.get("ticker")) if key in action_by_ticker),
            None,
        )
        if action:
            row["portfolio_action"] = action
        rows.append(row)
    return {
        "market": str(body.get("market") or packet.get("surface") or "").upper(),
        "event_id": packet.get("event_id"),
        "source_health": body.get("source_health") or "MISSING",
        "report_mode": body.get("report_mode") or "RESEARCH",
        "run_id": current.get("run_id"),
        "started_at": current.get("started_at"),
        "manifest_status": source_metadata.get("status"),
        "decision_ready": quality.get("decision_ready"),
        "source": _safe_mapping(source_metadata, ("run_id", "last_run_at", "status")),
        "guardrails": _safe_mapping(
            body.get("guardrails"),
            ("valid_until", "expired_at_build", "decision_ready", "conditional_strategy_ready"),
        ),
        "quality": safe_quality,
        "universe_coverage": safe_universe_coverage,
        "provenance": {
            "surface_run_id": current.get("run_id"),
            "manifest_run_id": source_metadata.get("run_id"),
            "universe_source_run_id": safe_universe_coverage.get("source_run_id"),
            "decision_bundle_run_id": bundle.get("run_id"),
            "analysis_source_run_id": bundle.get("analysis_source_run_id"),
            "execution_source_run_id": bundle.get("execution_source_run_id"),
        },
        "portfolio_action_count": len(actions),
        "rows": rows,
        "coverage": safe_universe_coverage,
    }


def _load_latest_work_report(
    archive_dir: Path,
    market: str,
    *,
    current_packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Load a validated, content-addressed Work report and classify its lineage.

    A report is never allowed to influence current action cards merely because a
    file named ``latest.json`` exists.  The runtime report contract, immutable
    event bytes, ticker coverage, and current packet lineage are all checked
    before the caller decides whether it is current analysis or prior reference.
    Receipt hashes stay out of the mobile payload.
    """

    reports_root = Path(archive_dir) / "work-reports"
    normalized_market = str(market or "").strip().lower()
    candidates = [
        reports_root / normalized_market / "latest.json",
        reports_root / normalized_market.upper() / "latest.json",
        reports_root / f"latest-{normalized_market}.json",
        reports_root / f"latest_{normalized_market}.json",
    ]
    if reports_root.exists():
        try:
            discovered = sorted(
                reports_root.rglob("latest.json"),
                key=lambda path: path.stat().st_mtime,
                reverse=True,
            )
        except OSError:
            discovered = []
        candidates.extend(discovered)

    seen: set[Path] = set()
    for path in candidates:
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        surface = str(payload.get("surface") or payload.get("market") or path.parent.name).strip().lower()
        if surface and surface not in {normalized_market, normalized_market.upper().lower()}:
            continue
        try:
            validate_work_report(payload)
        except (WorkRuntimeError, TypeError, ValueError):
            continue
        if not _work_report_has_immutable_backing(
            payload,
            latest_path=path,
            reports_root=reports_root,
            market=normalized_market,
        ):
            continue
        sanitized = _sanitize_work_report(payload, market=normalized_market)
        if sanitized:
            lineage = _work_report_lineage(payload, current_packet)
            sanitized["lineage"] = lineage
            if lineage.get("status") != "CURRENT_PACKET":
                sanitized = _analysis_only_work_report(sanitized)
            return sanitized
    return {}


def _work_report_has_immutable_backing(
    payload: dict[str, Any],
    *,
    latest_path: Path,
    reports_root: Path,
    market: str,
) -> bool:
    report_sha = str(payload.get("report_sha256") or "").strip().lower()
    if len(report_sha) != 64 or any(character not in "0123456789abcdef" for character in report_sha):
        return False
    try:
        latest_bytes = latest_path.read_bytes()
    except OSError:
        return False
    surface = str(payload.get("surface") or market).strip().lower()
    candidates = (
        latest_path.parent / "events" / f"{report_sha}.json",
        reports_root / surface / "events" / f"{report_sha}.json",
        reports_root / market / "events" / f"{report_sha}.json",
    )
    seen: set[Path] = set()
    for event_path in candidates:
        if event_path in seen:
            continue
        seen.add(event_path)
        try:
            if event_path.is_file() and event_path.read_bytes() == latest_bytes:
                return True
        except OSError:
            continue
    return False


def _work_report_lineage(
    report: dict[str, Any],
    current_packet: dict[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(current_packet, dict) or not current_packet:
        return {
            "status": "UNVERIFIED_REFERENCE",
            "current_action_cards_enriched": False,
            "reason": "current_packet_unavailable",
        }

    body = current_packet.get("body") if isinstance(current_packet.get("body"), dict) else {}
    current = body.get("current") if isinstance(body.get("current"), dict) else {}
    bundle = current.get("bundle") if isinstance(current.get("bundle"), dict) else {}
    universe = current.get("universe_coverage") if isinstance(current.get("universe_coverage"), dict) else {}
    structured = report.get("structured_report") if isinstance(report.get("structured_report"), dict) else {}
    coverage = structured.get("coverage_receipt") if isinstance(structured.get("coverage_receipt"), dict) else {}

    current_tickers = _strategy_ticker_identities(bundle.get("strategy_table"))
    report_tickers = _strategy_ticker_identities(structured.get("strategies"))
    ticker_coverage_matches = bool(current_tickers) and current_tickers == report_tickers
    exact_packet = (
        str(report.get("event_id") or "") == str(current_packet.get("event_id") or "")
        and str(report.get("source_sha256") or "") == str(current_packet.get("source_sha256") or "")
    )
    contract_matches = (
        bool(str(report.get("workflow_contract_sha256") or ""))
        and str(report.get("workflow_contract_sha256"))
        == str(current_packet.get("workflow_contract_sha256") or "")
    )

    report_source_run_id = str(coverage.get("source_run_id") or "").strip()
    current_lineage_ids = {
        str(value).strip()
        for value in (
            current.get("run_id"),
            bundle.get("run_id"),
            bundle.get("analysis_source_run_id"),
            universe.get("source_run_id"),
        )
        if str(value or "").strip()
    }
    analysis_lineage_matches = bool(
        report_source_run_id and report_source_run_id in current_lineage_ids
    )

    if exact_packet and contract_matches and ticker_coverage_matches:
        status = "CURRENT_PACKET"
        reason = "event_source_and_ticker_coverage_match"
    elif contract_matches and analysis_lineage_matches and ticker_coverage_matches:
        status = "CURRENT_ANALYSIS_LINEAGE"
        reason = "analysis_source_run_and_ticker_coverage_match"
    else:
        status = "PAST_REFERENCE"
        if not contract_matches:
            reason = "workflow_contract_mismatch"
        elif not ticker_coverage_matches:
            reason = "ticker_coverage_mismatch"
        elif not analysis_lineage_matches:
            reason = "packet_source_lineage_mismatch"
        else:
            reason = "packet_binding_mismatch"
    return {
        "status": status,
        "current_action_cards_enriched": status in {"CURRENT_PACKET", "CURRENT_ANALYSIS_LINEAGE"},
        "reason": reason,
        "workflow_contract_matches": contract_matches,
        "ticker_coverage_matches": ticker_coverage_matches,
        "report_ticker_count": len(report_tickers),
        "current_ticker_count": len(current_tickers),
        "report_source_run_id": report_source_run_id or None,
        "current_analysis_source_run_id": bundle.get("analysis_source_run_id") or current.get("run_id"),
    }


def _analysis_only_work_report(report: dict[str, Any]) -> dict[str, Any]:
    """Keep the full analysis while preventing reuse of an older execution gate."""

    result = dict(report)
    structured = (
        dict(result.get("structured_report"))
        if isinstance(result.get("structured_report"), dict)
        else {}
    )
    strategies: list[dict[str, Any]] = []
    for item in structured.get("strategies") or []:
        if not isinstance(item, dict):
            continue
        strategy = dict(item)
        strategy.pop("execution", None)
        strategies.append(strategy)
    structured["strategies"] = strategies
    result["structured_report"] = structured
    # The report narrative and top actions are valuable analysis-time context.
    # Only per-ticker execution gates are removed; the UI labels the narrative
    # as reference material and keeps the current overlay authoritative.
    result["analysis_only"] = True
    return result


def _strategy_ticker_identities(rows: Any) -> set[str]:
    if not isinstance(rows, list):
        return set()
    identities: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        keys = _ticker_identity_keys(row.get("ticker"))
        if keys:
            # ``_ticker_identity_keys`` returns both broker and canonical aliases;
            # its last entry is the suffix-free identity used for equality.
            identities.add(keys[-1])
    return identities


def _sanitize_work_report(payload: dict[str, Any], *, market: str) -> dict[str, Any]:
    structured = payload.get("structured_report") if isinstance(payload.get("structured_report"), dict) else {}
    report_markdown = _sanitize_work_report_text(str(payload.get("report_markdown") or ""))
    allowed_structured = {
        key: structured.get(key)
        for key in (
            "title",
            "generated_at",
            "as_of",
            "source_health",
            "report_mode",
            "summary",
            "top_actions",
            "strategies",
            "coverage_receipt",
            "model_receipt",
            "source_summary",
            "next_checkpoint",
        )
        if structured.get(key) is not None
    }
    strategies = []
    for item in allowed_structured.get("strategies") or []:
        if not isinstance(item, dict):
            continue
        strategy = dict(item)
        strategy["display_name"] = _display_name_for(
            strategy.get("ticker"), strategy.get("display_name")
        )
        strategies.append(strategy)
    if strategies:
        allowed_structured["strategies"] = strategies
    if not report_markdown and not allowed_structured:
        return {}
    result = {
        "schema": "tradingagents.mobile-work-report/v1",
        "source_schema": payload.get("schema"),
        "market": market.upper(),
        "event_id": payload.get("event_id"),
        "report_id": payload.get("report_id"),
        "published_at": payload.get("published_at"),
        "report_markdown": report_markdown,
        "structured_report": allowed_structured,
    }
    return _sanitize_work_report_value(_strip_strategy_identifiers(result))


def _sanitize_work_report_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _sanitize_work_report_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize_work_report_value(item) for item in value]
    if isinstance(value, str):
        return _sanitize_work_report_text(value)
    return value


def _sanitize_work_report_text(value: str) -> str:
    text = str(value or "")
    empty_state_line = re.compile(
        r"(?im)^\s*(?:[-*]\s*)?(?:현재\s*조건부\s*실행\s*가능|현재\s*실행\s*가능|지금\s*실행\s*가능)"
        r"\s*[:：]\s*(?:없음|none|해당\s*없음|-+)\s*[.!。]?\s*$"
    )
    text = empty_state_line.sub("", text)
    replacements = {
        "BLOCKED_STALE": "주문 전 실시간 재확인",
        "BLOCKED_INCOMPLETE": "필수 데이터 재확인",
        "NEEDS_LIVE_RECHECK": "주문 전 실시간 재확인",
        "WAIT_FOR_TRIGGER": "조건 충족 대기",
        "READY_NOW": "현재 조건 확인됨",
        "MARKET_CLOSED": "개장 후 재확인",
        "DATA_OUTAGE": "데이터 복구 후 재확인",
        "RESEARCH_ONLY": "분석 참고 전용",
        "NO_ENTRY": "신규 진입 보류",
        "IMMEDIATE": "현재 조건 확인됨",
        "COMPLETE": "전체 분석 완료",
        "DEGRADED": "일부 데이터 재확인",
        "RESEARCH": "분석 참고",
        "AVOID": "매수 보류",
        "WATCH": "관찰",
        "HOLD": "보유",
    }
    for machine_value, investor_value in replacements.items():
        text = re.sub(
            rf"(?<![A-Z0-9_]){re.escape(machine_value)}(?![A-Z0-9_])",
            investor_value,
            text,
        )
    investor_terms = {
        "live recheck": "실시간 재확인",
        "confidence": "신뢰도",
        "execution": "실행 판단",
        "sizing": "비중 조절",
        "thesis": "투자 논지",
        "packet": "분석 자료",
        "RVOL": "상대거래량(RVOL)",
        "VWAP": "거래량가중평균가격(VWAP)",
    }
    for source, target in investor_terms.items():
        text = re.sub(rf"(?<![A-Za-z]){re.escape(source)}(?![A-Za-z])", target, text, flags=re.IGNORECASE)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _annotate_market_roles(
    market_payload: dict[str, Any],
    *,
    archive_dir: Path,
    integrated_report: dict[str, Any],
) -> None:
    rows = market_payload.get("rows") if isinstance(market_payload.get("rows"), list) else []
    active_universe = _load_active_universe(archive_dir, str(market_payload.get("run_id") or ""))
    holding_ids = _identity_set(active_universe.get("expected_holding_tickers"))
    watchlist_ids = _identity_set(active_universe.get("expected_watchlist_tickers"))
    scanner_ids = _identity_set(active_universe.get("scanner_candidates"))
    work_roles: dict[str, str] = {}
    structured = (
        integrated_report.get("structured_report")
        if isinstance(integrated_report.get("structured_report"), dict)
        else {}
    )
    for strategy in structured.get("strategies") or []:
        if not isinstance(strategy, dict):
            continue
        role = _normalize_universe_role(strategy.get("portfolio_role"))
        for identity in _ticker_identity_keys(strategy.get("ticker")):
            if role:
                work_roles[identity] = role

    counts = {"HOLDING": 0, "WATCHLIST": 0, "NEW_CANDIDATE": 0}
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            continue
        identities = set(_ticker_identity_keys(row.get("ticker")))
        explicit = _normalize_universe_role(row.get("universe_role") or row.get("candidate_source"))
        work_role = next((work_roles[key] for key in identities if key in work_roles), "")
        if row.get("is_held") is True or identities.intersection(holding_ids):
            role = "HOLDING"
        elif work_role:
            role = work_role
        elif row.get("is_scanner_candidate") is True or identities.intersection(scanner_ids):
            role = "NEW_CANDIDATE"
        elif row.get("is_watchlist") is True or identities.intersection(watchlist_ids):
            role = "WATCHLIST"
        elif explicit:
            role = explicit
        else:
            role = "WATCHLIST"
        row["universe_role"] = role
        row.setdefault("display_priority", index)
        counts[role] = counts.get(role, 0) + 1
    market_payload["role_counts"] = counts


def _load_active_universe(archive_dir: Path, run_id: str) -> dict[str, Any]:
    if not run_id:
        return {}
    runs_root = Path(archive_dir) / "runs"
    candidates = [runs_root / run_id / "run.json"]
    if runs_root.is_dir():
        try:
            candidates.extend(path / run_id / "run.json" for path in runs_root.iterdir() if path.is_dir())
        except OSError:
            pass
    for path in candidates:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        active = payload.get("active_universe") if isinstance(payload, dict) else None
        if isinstance(active, dict):
            return active
    return {}


def _identity_set(values: Any) -> set[str]:
    result: set[str] = set()
    for value in values or []:
        ticker = value
        if isinstance(value, dict):
            ticker = value.get("ticker") or value.get("canonical_ticker") or value.get("symbol")
        result.update(_ticker_identity_keys(ticker))
    return result


def _normalize_universe_role(value: Any) -> str:
    text = str(value or "").strip().upper()
    if not text:
        return ""
    if "HOLD" in text or "OWN" in text or "보유" in text:
        return "HOLDING"
    if "SCANNER" in text or "NEW" in text or "DISCOVERY" in text or "신규" in text:
        return "NEW_CANDIDATE"
    if "WATCH" in text or "관심" in text:
        return "WATCHLIST"
    return ""


def _public_quality(value: Any) -> dict[str, Any]:
    source = value if isinstance(value, dict) else {}
    result = _safe_mapping(
        value,
        (
            "execution_ready",
            "conditional_strategy_ready",
            "current_execution_promotion",
            "generated_in_current_run",
            "freshness_class",
            "execution_eligibility",
            "data_status",
            "provider_status",
            "row_valid_until",
            "expired_at_build",
        ),
    )
    machine_mode = str(source.get("row_mode") or "MISSING").strip().upper()
    investor_state, investor_label = _INVESTOR_ROW_STATES.get(
        machine_mode,
        ("RESEARCH", "분석 시점 참고"),
    )
    result["investor_state"] = investor_state
    result["investor_label"] = investor_label
    return result


def _safe_mapping(value: Any, keys: tuple[str, ...]) -> dict[str, Any]:
    source = value if isinstance(value, dict) else {}
    return {key: source.get(key) for key in keys if source.get(key) is not None}


def _ticker_identity_keys(value: Any) -> tuple[str, ...]:
    ticker = str(value or "").strip().upper()
    if not ticker:
        return ()
    keys = [ticker]
    for suffix in (".KS", ".KQ"):
        if ticker.endswith(suffix):
            keys.append(ticker[: -len(suffix)])
            break
    return tuple(dict.fromkeys(keys))


def _display_name_for(ticker: Any, candidate: Any) -> str:
    ticker_text = str(ticker or "").strip()
    candidate_text = str(candidate or "").strip()
    ticker_identities = {value.upper() for value in _ticker_identity_keys(ticker_text)}
    candidate_identity = re.sub(r"\.(?:KS|KQ)$", "", candidate_text.upper())
    candidate_is_ticker = not candidate_text or candidate_identity in ticker_identities
    if not candidate_is_ticker:
        return candidate_text
    try:
        resolved = resolve_instrument(ticker_text)
    except InstrumentResolutionError:
        return candidate_text or ticker_text
    resolved_name = str(resolved.display_name or "").strip()
    resolved_identity = re.sub(r"\.(?:KS|KQ)$", "", resolved_name.upper())
    return resolved_name if resolved_identity not in ticker_identities else (candidate_text or ticker_text)


def _public_html(payload: dict[str, Any], *, public_base_url: str) -> str:
    market_sections = []
    for market in MARKETS:
        item = payload["markets"].get(market) or {}
        rows = item.get("rows") or []
        cards = "".join(_public_card(row) for row in rows)
        if not cards:
            cards = "<p class='empty'>공개 가능한 신규 리서치 후보가 없습니다.</p>"
        market_sections.append(
            f"""
            <section class="market-panel" data-market="{market}" id="market-{market}">
              <div class="market-head">
                <div><p class="eyebrow">{market.upper()} MARKET</p><h2>{market.upper()} 리서치 후보</h2></div>
                <span class="health health-{_css_token(item.get('source_health'))}">{_escape(_source_health_label(item.get('source_health')))}</span>
              </div>
              <div class="source-meta">
                <span>Run {_escape(item.get('run_id') or '-')}</span>
                <span>{_escape(item.get('started_at') or '-')}</span>
                <span>{len(rows)}개 공개 후보</span>
              </div>
              <div class="cards">{cards}</div>
            </section>
            """
        )
    private_url = _join_url(public_base_url, "mobile/strategy.html") or "strategy.html"
    embedded = html.escape(json.dumps(payload, ensure_ascii=False), quote=False)
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#081a2b">
  <meta name="referrer" content="no-referrer">
  <title>TradingAgents 모바일 리서치</title>
  <link rel="stylesheet" href="mobile.css">
</head>
<body>
  <header class="topbar"><a href="../index.html">TradingAgents</a><span>공개 리서치</span></header>
  <main>
    <section class="hero-mobile">
      <p class="eyebrow">MOBILE INVESTMENT HUB</p>
      <h1>장중 리서치 한눈에 보기</h1>
      <p>공개 리서치 후보의 분석 시점 근거를 보여 줍니다. 주문 전에는 현재가와 진입·무효화 조건을 다시 확인하세요.</p>
      <div class="privacy-banner">공개 안전 모드 · 개인 계좌 정보 없음</div>
      <a class="private-link" href="{_escape(private_url)}">통합 투자 전략 열기</a>
    </section>
    <nav class="market-tabs" aria-label="시장 선택">
      <button type="button" data-target="kr" aria-pressed="true">KR</button>
      <button type="button" data-target="us" aria-pressed="false">US</button>
    </nav>
    {''.join(market_sections)}
    <p class="footer-note">자동 주문 지시가 아닙니다. 오래되거나 불완전한 데이터는 실행에 사용하지 마세요.</p>
  </main>
  <script id="mobile-data" type="application/json">{embedded}</script>
  <script>
  (() => {{
    const tabs = [...document.querySelectorAll('[data-target]')];
    const panels = [...document.querySelectorAll('[data-market]')];
    function select(market) {{
      tabs.forEach((tab) => tab.setAttribute('aria-pressed', String(tab.dataset.target === market)));
      panels.forEach((panel) => panel.hidden = panel.dataset.market !== market);
    }}
    tabs.forEach((tab) => tab.addEventListener('click', () => select(tab.dataset.target)));
    const requestedMarket = new URLSearchParams(location.search).get('market');
    select(requestedMarket === 'us' ? 'us' : 'kr');
    function refreshExpiry() {{
      const now = Date.now();
      let nextDeadline = Number.POSITIVE_INFINITY;
      document.querySelectorAll('[data-valid-until]').forEach((card) => {{
        const deadline = Date.parse(card.dataset.validUntil || '');
        if (!Number.isFinite(deadline)) return;
        if (deadline <= now) {{
          card.dataset.rowMode = 'REFERENCE';
          const badge = card.querySelector('.row-mode');
          if (badge) badge.textContent = '주문 전 재확인';
          const warning = card.querySelector('.expiry-warning');
          if (warning) warning.hidden = false;
        }} else {{
          nextDeadline = Math.min(nextDeadline, deadline);
        }}
      }});
      if (Number.isFinite(nextDeadline)) setTimeout(refreshExpiry, Math.max(50, nextDeadline - now + 50));
    }}
    refreshExpiry();
  }})();
  </script>
</body>
</html>
"""


def _public_card(row: dict[str, Any]) -> str:
    quality = row.get("quality") if isinstance(row.get("quality"), dict) else {}
    mode = str(quality.get("investor_state") or "UNAVAILABLE")
    mode_label = str(quality.get("investor_label") or "데이터 재확인")
    valid_until = str(quality.get("row_valid_until") or "")
    return f"""
    <article class="action-card" data-row-mode="{_escape(mode)}" data-valid-until="{_escape(valid_until)}">
      <div class="card-title"><div><strong>{_escape(row.get('display_name') or row.get('ticker') or '-')}</strong><span class="ticker-code">{_escape(row.get('ticker') or '-')}</span></div><span class="row-mode mode-{_css_token(mode)}">{_escape(mode_label)}</span></div>
      <p class="expiry-warning" hidden>분석 시점 이후 데이터입니다. 주문 전 현재가와 조건을 다시 확인하세요.</p>
      <div class="price-line"><strong>{_fmt_price(row.get('last_price'))}</strong><span>{_escape(row.get('market_data_asof') or '-')}</span></div>
      <dl>
        <div><dt>VWAP</dt><dd>{_escape(row.get('vwap_position_ko') or '-')}</dd></div>
        <div><dt>상대 거래량</dt><dd>{_fmt_ratio(row.get('relative_volume'))}</dd></div>
        <div><dt>섹터·지수</dt><dd>{_escape(row.get('sync_summary_ko') or '-')}</dd></div>
        <div><dt>데이터</dt><dd>{_escape(row.get('data_status_ko') or quality.get('freshness_class') or '-')}</dd></div>
      </dl>
    </article>
    """


def _private_html(*, desktop: bool = False) -> str:
    asset_prefix = "mobile/" if desktop else ""
    report_prefix = "" if desktop else "../"
    public_href = "index.html" if desktop else "../index.html"
    body_class = "private-body desktop-body" if desktop else "private-body"
    device_label = "PC 투자 전략" if desktop else "모바일 투자 전략"
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#081a2b">
  <meta name="referrer" content="no-referrer">
  <meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'">
  <title>TradingAgents 통합 투자 전략</title>
  <link rel="stylesheet" href="{asset_prefix}mobile.css">
</head>
<body class="{body_class}" data-strategy-url="{asset_prefix}strategy.json">
  <header class="topbar"><a href="{public_href}">TradingAgents 홈</a><span>{device_label}</span></header>
  <main>
    <section class="hero-mobile">
      <p class="eyebrow">KR · US · YOUTUBE · PRISM · WORK</p>
      <h1>한눈에 보는 투자 전략</h1>
      <p>분석 시점의 전략과 주문 직전 실시간 확인 상태를 분리했습니다. 보유·관심·신규 후보별로 조건, 실행 행동, 무효화 기준을 확인하세요.</p>
      <div class="privacy-banner">링크에서 바로 열립니다 · 계좌번호와 고객 식별정보는 제외합니다.</div>
      <nav class="report-nav" aria-label="전체 분석 리포트">
        <a href="{report_prefix}youtube/">YouTube 분석</a>
        <a href="{report_prefix}prism-telegram/">PRISM 분석</a>
        <a href="{report_prefix}work/">Work 원문</a>
      </nav>
    </section>
    <details class="pipeline-explainer" open>
      <summary><span class="eyebrow">HOW IT IS MADE</span><strong id="pipeline-title">이 전략이 만들어지는 과정</strong></summary>
      <ol>
        <li><strong>종목 분석</strong><span>KIS·시장 데이터로 보유/관심/신규 후보의 가격·거래량·수급·위험을 분석</span></li>
        <li><strong>외부 관점</strong><span>YouTube·PRISM의 주장, 종목, 주요 이슈를 일일 단위로 구조화</span></li>
        <li><strong>ChatGPT Work 종합</strong><span>KR/US별로 모든 근거를 다시 비교해 순위·매수/보유/축소 조건과 무효화 행동을 결정</span></li>
        <li><strong>안전한 공개</strong><span>계좌 식별정보를 제거한 동일 전략을 PC·모바일·JSON으로 게시</span></li>
      </ol>
      <p class="trusted-note"><strong>우선 신뢰 채널:</strong> @kpunch와 @sosumonkey 영상은 사용자 검증 최우선 근거로 취급하되, 실제 주문 직전 시세·계좌·위험 확인은 별도로 유지합니다.</p>
    </details>
    <div id="private-status" class="privacy-banner" role="status">통합 전략 데이터를 불러오는 중입니다.</div>
    <nav id="private-tabs" class="market-tabs" aria-label="시장 선택" hidden></nav>
    <div id="private-root"></div>
  </main>
  <script src="{asset_prefix}private.js" defer></script>
</body>
</html>
"""


_MOBILE_CSS = r"""
:root {
  color-scheme: dark;
  --bg: #06111d;
  --panel: #0c2033;
  --panel-2: #102b43;
  --text: #f6f8fb;
  --muted: #a9bacb;
  --line: rgba(255,255,255,.12);
  --accent: #59d6c7;
  --warn: #ffc45b;
  --danger: #ff7c83;
  --ok: #75dfa0;
}
* { box-sizing: border-box; }
html { background: var(--bg); }
body { min-width: 0; margin: 0; background: radial-gradient(circle at top right, #12395a 0, var(--bg) 34rem); color: var(--text); font: 16px/1.55 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans KR", sans-serif; }
a { color: inherit; }
.topbar { position: sticky; top: 0; z-index: 20; display: flex; justify-content: space-between; gap: 12px; min-height: 52px; padding: max(10px, env(safe-area-inset-top)) 16px 10px; border-bottom: 1px solid var(--line); background: rgba(6,17,29,.94); backdrop-filter: blur(14px); font-size: .88rem; color: var(--muted); }
.topbar a { color: var(--text); font-weight: 750; text-decoration: none; }
main { width: 100%; max-width: 760px; min-width: 0; margin: 0 auto; padding: 22px 14px calc(42px + env(safe-area-inset-bottom)); }
.hero-mobile { padding: 12px 2px 20px; }
.eyebrow { margin: 0 0 7px; color: var(--accent); font-size: .72rem; font-weight: 800; letter-spacing: .12em; }
h1, h2, p { overflow-wrap: anywhere; }
h1 { margin: 0; font-size: clamp(1.8rem, 8vw, 2.55rem); line-height: 1.08; letter-spacing: -.04em; }
h2 { margin: 0; font-size: 1.25rem; }
.hero-mobile > p:not(.eyebrow) { margin: 12px 0; color: var(--muted); }
.privacy-banner { min-width: 0; max-width: 100%; margin: 14px 0; padding: 11px 13px; border: 1px solid rgba(89,214,199,.35); border-radius: 12px; background: rgba(89,214,199,.09); color: #c9fff8; overflow-wrap: anywhere; font-size: .9rem; }
.privacy-banner.error { border-color: rgba(255,124,131,.45); background: rgba(255,124,131,.10); color: #ffd8da; }
.private-link { display: inline-flex; align-items: center; min-height: 44px; padding: 10px 15px; border-radius: 12px; background: var(--accent); color: #04201f; font-weight: 800; text-decoration: none; }
.report-nav { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.report-nav a { padding: 8px 11px; border: 1px solid var(--line); border-radius: 999px; color: #d9eef4; font-size: .78rem; font-weight: 760; text-decoration: none; }
.pipeline-explainer { margin: 0 0 20px; padding: 16px; border: 1px solid var(--line); border-radius: 17px; background: rgba(12,32,51,.78); }
.pipeline-explainer > summary { display: flex; align-items: center; justify-content: space-between; gap: 12px; min-height: 34px; padding: 0; color: var(--text); }
.pipeline-explainer > summary .eyebrow { margin: 0; }
.pipeline-explainer > summary strong { font-size: 1rem; }
.pipeline-explainer ol { display: grid; gap: 8px; margin: 13px 0 0; padding: 0; list-style: none; counter-reset: pipeline; }
.pipeline-explainer li { display: grid; grid-template-columns: 1.1rem minmax(0,1fr); gap: 4px 9px; counter-increment: pipeline; }
.pipeline-explainer li::before { grid-row: 1 / span 2; content: counter(pipeline); display: grid; width: 1.1rem; height: 1.1rem; place-items: center; margin-top: 3px; border-radius: 50%; background: var(--accent); color: #04201f; font-size: .68rem; font-weight: 900; }
.pipeline-explainer li span, .trusted-note { color: var(--muted); font-size: .82rem; }
.trusted-note { margin: 13px 0 0; padding-top: 11px; border-top: 1px solid var(--line); }
.market-tabs { position: sticky; top: calc(53px + max(0px, env(safe-area-inset-top) - 10px)); z-index: 15; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; min-width: 0; max-width: 100%; margin: 0 -2px 18px; padding: 9px 2px; background: rgba(6,17,29,.94); backdrop-filter: blur(14px); }
.market-tabs button { min-width: 0; min-height: 44px; border: 1px solid var(--line); border-radius: 12px; background: var(--panel); color: var(--muted); overflow-wrap: anywhere; font: inherit; font-weight: 800; }
.market-tabs button[aria-pressed="true"] { border-color: var(--accent); background: rgba(89,214,199,.14); color: var(--text); }
.market-panel, #private-root { min-width: 0; max-width: 100%; }
.market-head { display: flex; flex-direction: column; align-items: stretch; gap: 8px; margin: 8px 0; }
.market-head > div:first-child { min-width: 0; }
.market-head > div:last-child { display: flex; flex-wrap: wrap; gap: 6px; justify-content: flex-start; }
.health, .row-mode, .held-badge, .role-badge { display: inline-flex; align-items: center; flex: 0 0 auto; min-height: 28px; padding: 4px 8px; border-radius: 999px; background: var(--panel-2); color: var(--muted); font-size: .7rem; font-weight: 850; letter-spacing: .03em; }
.health-ok, .mode-immediate { color: var(--ok); }
.health-degraded, .mode-conditional { color: var(--warn); }
.health-missing, .health-unavailable { color: var(--danger); }
.health-neutral { color: var(--muted); }
.health-failed, .health-stale, .mode-missing, .mode-recheck { color: var(--danger); }
.source-meta { display: flex; flex-wrap: wrap; gap: 6px 12px; margin-bottom: 12px; color: var(--muted); font-size: .78rem; }
.source-meta span, .card-title strong, .card-title div > span, .price-line strong, .price-line span { min-width: 0; overflow-wrap: anywhere; }
.cards { display: grid; grid-template-columns: minmax(0, 1fr); gap: 12px; }
.action-card { min-width: 0; padding: 15px; border: 1px solid var(--line); border-radius: 17px; background: linear-gradient(145deg, rgba(16,43,67,.96), rgba(10,29,47,.96)); box-shadow: 0 12px 28px rgba(0,0,0,.18); }
.action-card[data-readiness="RECHECK"], .action-card[data-readiness="RESEARCH"] { border-color: rgba(255,196,91,.28); }
.action-card[hidden] { display: none; }
.card-title { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }
.card-title div { min-width: 0; }
.card-title strong { display: block; font-size: 1.2rem; }
.card-title .ticker-code { display: block; margin-top: 2px; color: var(--muted); font-size: .76rem; font-weight: 720; letter-spacing: .04em; }
.price-line { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; margin: 15px 0; }
.price-line strong { font-size: 1.5rem; letter-spacing: -.025em; }
.price-line span { color: var(--muted); font-size: .74rem; text-align: right; }
.expiry-warning { margin: 10px 0 0; padding: 8px 10px; border-radius: 9px; background: rgba(255,124,131,.13); color: #ffc1c5; font-size: .82rem; font-weight: 750; }
dl { display: grid; gap: 0; margin: 0; }
dl div { display: grid; grid-template-columns: minmax(86px, .65fr) minmax(0, 1.35fr); gap: 10px; padding: 9px 0; border-top: 1px solid var(--line); }
dt { color: var(--muted); font-size: .8rem; }
dd { margin: 0; text-align: right; overflow-wrap: anywhere; font-size: .88rem; }
.private-action { margin: 12px 0; padding: 12px; border-radius: 12px; background: rgba(89,214,199,.08); }
.private-action strong { display: block; margin-bottom: 4px; color: var(--accent); }
.readiness-note { margin: 10px 0 0; color: var(--muted); font-size: .8rem; }
.condition-grid { display: grid; gap: 9px; margin: 12px 0; }
.condition-block { padding: 11px 12px; border: 1px solid var(--line); border-radius: 12px; background: rgba(255,255,255,.025); }
.condition-block strong { display: block; margin-bottom: 4px; color: var(--muted); font-size: .76rem; }
.condition-block p { margin: 0; font-size: .9rem; }
.condition-block.risk { border-color: rgba(255,124,131,.26); }
.signal-strip { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 7px; margin: 12px 0; }
.signal { min-width: 0; padding: 8px; border-radius: 10px; background: rgba(255,255,255,.045); }
.signal span, .signal strong { display: block; overflow-wrap: anywhere; }
.signal span { color: var(--muted); font-size: .68rem; }
.signal strong { margin-top: 2px; font-size: .82rem; }
.confidence-track { height: 5px; margin-top: 6px; overflow: hidden; border-radius: 99px; background: rgba(255,255,255,.1); }
.confidence-track i { display: block; height: 100%; border-radius: inherit; background: var(--accent); }
.role-badge { margin-left: 6px; color: var(--accent); }
.strategy-filters { display: flex; flex-wrap: wrap; gap: 7px; max-width: 100%; margin: 10px 0 14px; padding-bottom: 3px; }
.strategy-filters button { flex: 1 1 calc(33.333% - 7px); min-height: 40px; padding: 8px 10px; border: 1px solid var(--line); border-radius: 999px; background: var(--panel); color: var(--muted); font: inherit; font-size: .8rem; font-weight: 800; }
.strategy-filters button[aria-pressed="true"] { border-color: var(--accent); background: rgba(89,214,199,.14); color: var(--text); }
.integrated-report { margin: 14px 0 18px; padding: 16px; border: 1px solid rgba(89,214,199,.3); border-radius: 17px; background: linear-gradient(145deg, rgba(13,46,61,.98), rgba(10,29,47,.98)); }
.integrated-report h3 { margin: 0; font-size: 1.08rem; }
.integrated-report .summary { margin: 9px 0; color: #dbeaf3; }
.report-audit-grid { display: grid; gap: 7px; margin: 9px 0; }
.report-audit-grid p { display: flex; justify-content: space-between; gap: 12px; margin: 0; padding: 8px 10px; border-radius: 10px; background: rgba(255,255,255,.055); }
.report-audit-grid strong { color: #effcff; }
.report-audit-grid span { color: #bcd1dc; text-align: right; }
.work-top-actions { display: grid; gap: 8px; margin: 12px 0; }
.work-action { padding: 10px 11px; border-left: 3px solid var(--accent); border-radius: 8px; background: rgba(89,214,199,.07); }
.work-action strong { display: block; font-size: .86rem; }
.work-action span { color: var(--muted); font-size: .8rem; }
.source-chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 10px 0; }
.source-chip { padding: 5px 8px; border-radius: 999px; background: rgba(255,255,255,.07); color: var(--muted); font-size: .72rem; }
.evidence-list { display: grid; gap: 7px; margin: 10px 0 0; padding: 0; list-style: none; }
.evidence-list li { padding: 9px 10px; border-left: 3px solid var(--line); border-radius: 8px; background: rgba(255,255,255,.035); color: #dce8f0; font-size: .82rem; }
.evidence-list li.bullish { border-left-color: var(--ok); }
.evidence-list li.bearish { border-left-color: var(--danger); }
.evidence-list li.mixed { border-left-color: var(--warn); }
.evidence-list small { display: block; margin-top: 3px; color: var(--muted); }
.market-overview { display: grid; grid-template-columns: repeat(5,minmax(0,1fr)); gap: 6px; margin: 12px 0 16px; }
.overview-stat { padding: 11px; border: 1px solid var(--line); border-radius: 12px; background: rgba(255,255,255,.03); }
.overview-stat strong { display: block; font-size: 1.18rem; }
.overview-stat span { color: var(--muted); font-size: .66rem; line-height: 1.25; }
.markdown-report { max-height: 32rem; margin: 4px 0 0; padding: 12px; overflow: auto; border: 1px solid var(--line); border-radius: 10px; background: rgba(0,0,0,.18); color: #dce8f0; white-space: pre-wrap; overflow-wrap: anywhere; font: .78rem/1.55 ui-monospace, SFMono-Regular, Consolas, monospace; }
.card-rationale { margin: 10px 0 0; padding-top: 10px; border-top: 1px solid var(--line); color: var(--muted); font-size: .82rem; }
.held-badge { margin-left: 6px; color: var(--accent); }
.empty, .footer-note { color: var(--muted); }
.footer-note { margin: 24px 2px 0; font-size: .78rem; }
details { margin-top: 10px; }
summary { min-height: 44px; padding: 11px 0; color: var(--muted); cursor: pointer; }
@media (min-width: 660px) {
  main { padding-left: 20px; padding-right: 20px; }
  .market-head { flex-direction: row; align-items: flex-start; justify-content: space-between; gap: 12px; }
  .market-head > div:first-child { flex: 1 1 auto; }
  .market-head > div:last-child { flex: 0 1 auto; justify-content: flex-end; }
  .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (min-width: 1000px) {
  .desktop-body main { max-width: 1480px; padding-left: 28px; padding-right: 28px; }
  .desktop-body .hero-mobile { display: grid; grid-template-columns: 1.5fr 1fr; column-gap: 28px; }
  .desktop-body .hero-mobile .eyebrow, .desktop-body .hero-mobile h1 { grid-column: 1; }
  .desktop-body .hero-mobile > p { grid-column: 1; }
  .desktop-body .hero-mobile .privacy-banner, .desktop-body .hero-mobile .report-nav { grid-column: 2; }
  .desktop-body .pipeline-explainer ol { grid-template-columns: repeat(4,minmax(0,1fr)); }
  .desktop-body .cards { grid-template-columns: repeat(3,minmax(0,1fr)); }
  .desktop-body .integrated-report { padding: 22px; }
  .desktop-body .market-overview { grid-template-columns: repeat(5,minmax(0,1fr)); }
}
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { scroll-behavior: auto !important; } }
""".strip()


_PRIVATE_JS = r"""
(() => {
  'use strict';
  const status = document.getElementById('private-status');
  const root = document.getElementById('private-root');
  const tabs = document.getElementById('private-tabs');
  const pipelineExplainer = document.querySelector('.pipeline-explainer');
  if (pipelineExplainer && matchMedia('(max-width: 659px)').matches) pipelineExplainer.open = false;
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (ch) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const fmt = (value) => Number.isFinite(Number(value)) ? Number(value).toLocaleString(undefined, {maximumFractionDigits: 2}) : '-';
  const dateTime = (value) => {
    const parsed = new Date(value || '');
    if (!Number.isFinite(parsed.getTime())) return '-';
    return new Intl.DateTimeFormat('ko-KR', {year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', timeZoneName: 'short'}).format(parsed);
  };
  const actionLabels = {
    NONE: '추가 행동 없음', NO_ACTION: '분석 결론 유지', HOLD: '보유 유지', WATCH: '관심 종목으로 관찰',
    WATCH_TRIGGER: '조건 충족 여부 관찰', WATCH_RISK: '위험 조건 관찰', WAIT: '조건 확인 전 대기', AVOID: '신규 매수 회피',
    BULLISH: '긍정적 관점', NEUTRAL: '중립적 관점', BEARISH: '보수적 관점',
    STARTER: '초기 분할매수', STARTER_NOW: '초기 분할매수 검토',
    STARTER_IF_TRIGGERED: '조건 충족 시 신규 분할매수',
    ADD: '분할 추가매수', ADD_NOW: '분할 추가매수 검토', BUY: '매수 검토', BUY_NOW: '매수 검토',
    ADD_IF_TRIGGERED: '조건 충족 시 추가 매수',
    REDUCE: '비중 축소', REDUCE_NOW: '비중 축소 검토', TRIM_NOW: '일부 축소 검토',
    TRIM_TO_FUND: '강한 후보로 자금 이동을 위한 일부 축소',
    REDUCE_RISK: '리스크 축소', REDUCE_IF_TRIGGERED: '조건 충족 시 비중 축소',
    TAKE_PROFIT: '이익 실현', TAKE_PROFIT_NOW: '이익 실현 검토', TAKE_PROFIT_IF_TRIGGERED: '조건 충족 시 이익 실현',
    STOP_LOSS: '손절 검토', STOP_LOSS_NOW: '손절 검토', STOP_LOSS_IF_TRIGGERED: '조건 충족 시 손절',
    EXIT: '청산 검토', EXIT_NOW: '청산 검토', EXIT_IF_TRIGGERED: '조건 충족 시 청산', SELL: '매도 검토',
    FULL_EXIT: '전량 정리', PARTIAL_20: '20% 분할 매도', PARTIAL_35: '35% 분할 매도',
    CUSTOM: '세부 실행 계획 확인'
  };
  const internalCode = (value) => /^[A-Z][A-Z0-9_]*$/.test(String(value || '').trim());
  const actionLabel = (value) => {
    const text = String(value || '').trim();
    if (!text) return '';
    return actionLabels[text.toUpperCase()] || (internalCode(text) ? '세부 실행 계획 확인' : text);
  };
  const won = (value) => {
    if (!Number.isFinite(Number(value))) return '-';
    return new Intl.NumberFormat('ko-KR', {style: 'currency', currency: 'KRW', maximumFractionDigits: 0, signDisplay: 'always'}).format(Number(value));
  };
  const percent = (value) => Number.isFinite(Number(value)) ? new Intl.NumberFormat('ko-KR', {style: 'percent', maximumFractionDigits: 1}).format(Number(value)) : '-';
  const sizingText = (delta, target) => combineDistinct(
    Number.isFinite(Number(delta)) && Number(delta) !== 0 ? `조정 금액 ${won(delta)}` : '',
    Number.isFinite(Number(target)) && Number(target) >= 0 && Number(target) <= 1 ? `목표 비중 ${percent(target)}` : '',
  );
  const query = new URLSearchParams(location.search);
  const requestedMarket = query.get('market') === 'us' ? 'us' : 'kr';
  const requestedRun = query.get('run') || '';
  let expiryTimer;

  function valueText(value) {
    if (value == null || value === '') return '';
    if (Array.isArray(value)) return value.map(valueText).filter(Boolean).join(' · ');
    if (typeof value === 'object') {
      for (const field of ['text', 'label', 'summary', 'condition', 'action', 'description', 'stance']) {
        if (value[field]) return valueText(value[field]);
      }
      return '';
    }
    return String(value);
  }
  function combineDistinct(...values) {
    const parts = values.map(valueText).map((value) => value.trim()).filter(Boolean);
    return [...new Set(parts)].join(' · ');
  }
  function conditionItems(value) {
    if (value == null || value === '') return [];
    if (Array.isArray(value)) return value.flatMap(conditionItems);
    if (typeof value === 'object') {
      for (const field of ['condition', 'text', 'label', 'summary', 'description']) {
        if (value[field]) return conditionItems(value[field]);
      }
      return [];
    }
    const text = String(value).trim();
    if (!text || /^(?:none|n\/a|custom|unknown|-+)$/i.test(text)) return [];
    return text.split(/\s+(?:\/|\||·)\s+|\n+/).map((item) => item.trim()).filter(Boolean);
  }
  function distinctConditions(...values) {
    const seen = new Set();
    const result = [];
    values.flatMap(conditionItems).forEach((item) => {
      const key = item.replace(/\s+/g, ' ').trim().toLocaleLowerCase();
      if (!seen.has(key)) { seen.add(key); result.push(item); }
    });
    return result;
  }
  function conciseConditions(...values) {
    return distinctConditions(...values).slice(0, 3).map((item) => item.length > 180 ? `${item.slice(0, 177)}…` : item).join(' · ');
  }
  function fullConditions(...values) { return distinctConditions(...values).join(' · '); }
  function humanPlan(value) {
    if (value == null || value === '') return '';
    if (typeof value === 'string') {
      const text = value.trim();
      if (!text || /^CUSTOM$/i.test(text)) return '';
      return internalCode(text) ? actionLabel(text) : text;
    }
    if (Array.isArray(value)) return combineDistinct(...value.map(humanPlan));
    if (typeof value === 'object') {
      for (const field of ['text', 'summary', 'plan', 'description', 'action', 'label']) {
        if (value[field]) return humanPlan(value[field]);
      }
      if (value.enabled === false) return '';
      const stages = [1, 2, 3].map((stage) => {
        const fraction = value[`stage_${stage}_fraction`];
        return Number.isFinite(Number(fraction)) ? `${stage}차 ${percent(fraction)}` : '';
      }).filter(Boolean);
      return stages.length ? `단계 실행 비중 ${stages.join(' · ')}` : '';
    }
    return '';
  }
  function tickerKeys(value) {
    const ticker = String(value || '').trim().toUpperCase();
    const result = ticker ? [ticker] : [];
    if (ticker.endsWith('.KS') || ticker.endsWith('.KQ')) result.push(ticker.slice(0, -3));
    return result;
  }
  function workStrategy(item, ticker) {
    const wanted = new Set(tickerKeys(ticker));
    for (const field of ['integrated_report', 'reference_report']) {
      const structured = (((item || {})[field] || {}).structured_report || {});
      const strategy = (structured.strategies || []).find((candidate) => tickerKeys(candidate.ticker).some((value) => wanted.has(value)));
      if (strategy) return strategy;
    }
    return {};
  }
  function normalizeRole(value, held) {
    if (held) return 'HOLDING';
    const role = String(value || '').toUpperCase();
    if (role.includes('HOLD') || role.includes('OWN') || role.includes('보유')) return 'HOLDING';
    if (role.includes('NEW') || role.includes('SCANNER') || role.includes('DISCOVERY') || role.includes('신규')) return 'NEW_CANDIDATE';
    return 'WATCHLIST';
  }
  const roleLabel = (role) => ({HOLDING: '보유', WATCHLIST: '관심', NEW_CANDIDATE: '신규 후보'}[role] || '관심');

  function immediateContractComplete(market) {
    const coverage = (market || {}).universe_coverage || {};
    const provenance = (market || {}).provenance || {};
    const source = (market || {}).source || {};
    const quality = (market || {}).quality || {};
    const guardrails = (market || {}).guardrails || {};
    const expected = Number(coverage.expected_analysis_count);
    const total = Number(coverage.analysis_total_count);
    const successful = Number(coverage.analysis_successful_count);
    const zeroCounts = [
      coverage.missing_holding_count,
      coverage.missing_watchlist_count,
      coverage.missing_analysis_count,
      coverage.analysis_failed_count,
    ].every((value) => Number.isInteger(Number(value)) && Number(value) === 0);
    const runId = String((market || {}).run_id || '');
    const universeMode = String(coverage.ticker_universe_mode || '').toLowerCase();
    const accountReady = !['config_plus_account', 'account_only'].includes(universeMode)
      || String(coverage.account_snapshot_status || '').toLowerCase() === 'loaded';
    const boundRunIds = [
      provenance.surface_run_id,
      provenance.manifest_run_id,
      provenance.universe_source_run_id,
      provenance.decision_bundle_run_id,
    ].map((value) => String(value || ''));
    return coverage.status === 'COMPLETE'
      && coverage.complete === true
      && Number.isInteger(expected) && expected > 0
      && Number.isInteger(total) && total === expected
      && Number.isInteger(successful) && successful === expected
      && zeroCounts
      && accountReady
      && String((market || {}).manifest_status || '').toLowerCase() === 'success'
      && String(source.status || '').toLowerCase() === 'success'
      && (market || {}).decision_ready === true
      && quality.decision_ready === true
      && guardrails.decision_ready === true
      && runId !== ''
      && boundRunIds.every((value) => value === runId);
  }
  function baseLiveReadiness(row, market) {
    const quality = row.quality || {};
    const sourceHealth = String((market || {}).source_health || 'MISSING').toUpperCase();
    const guardrails = (market || {}).guardrails || {};
    const marketValid = Date.parse(guardrails.valid_until || '');
    if (sourceHealth !== 'OK') return {code: 'RECHECK', label: '주문 전 실시간 확인', note: '원천 데이터 상태를 다시 확인하세요.'};
    if (guardrails.expired_at_build === true || !Number.isFinite(marketValid) || marketValid <= Date.now()) {
      return {code: 'RECHECK', label: '주문 전 실시간 확인', note: '분석 시점 이후 가격이 변했을 수 있습니다.'};
    }
    const valid = Date.parse(quality.row_valid_until || '');
    if (quality.expired_at_build === true || !Number.isFinite(valid) || valid <= Date.now()) {
      return {code: 'RECHECK', label: '주문 전 실시간 확인', note: '이 종목의 실시간 조건을 다시 확인하세요.'};
    }
    const declared = String(quality.investor_state || 'UNAVAILABLE').toUpperCase();
    if (declared === 'READY' && (
      !immediateContractComplete(market)
      || quality.execution_ready !== true
      || quality.generated_in_current_run !== true
    )) return {code: 'RECHECK', label: '주문 전 실시간 확인', note: '분석 커버리지와 주문 조건을 한 번 더 확인하세요.'};
    if (declared === 'READY') return {code: 'READY', label: '실시간 조건 확인됨', note: '표시된 조건과 주문 수량을 최종 확인하세요.'};
    if (declared === 'CONDITIONAL') return {code: 'CONDITIONAL', label: '조건 확인 후 실행', note: '아래 진입·축소 조건이 실제로 충족됐는지 확인하세요.'};
    if (declared === 'RECHECK') return {code: 'RECHECK', label: '주문 전 실시간 확인', note: '분석 시점 이후 가격과 주문 조건을 다시 확인하세요.'};
    return {code: 'RESEARCH', label: '분석 시점 참고', note: '실시간 데이터 확인 후 전략을 적용하세요.'};
  }
  const workReadinessPolicy = {
    READY_NOW: {code: 'READY', label: '실시간 조건 확인됨', note: 'Work 분석은 현재 실행 가능으로 분류했습니다. 표시된 조건과 주문 수량을 최종 확인하세요.'},
    WAIT_FOR_TRIGGER: {code: 'CONDITIONAL', label: '조건 확인 후 실행', note: 'Work 분석의 진입·축소 조건이 실제로 충족되기 전에는 실행하지 마세요.'},
    NEEDS_LIVE_RECHECK: {code: 'RECHECK', label: '주문 전 실시간 확인', note: '분석 결론은 유지하되 현재가·거래량·호가를 다시 확인하세요.'},
    MARKET_CLOSED: {code: 'RECHECK', label: '개장 후 다시 확인', note: '시장 폐장 중 생성된 판단입니다. 개장 후 가격과 주문 가능 상태를 다시 확인하세요.'},
    DATA_OUTAGE: {code: 'RECHECK', label: '데이터 복구 후 확인', note: '필수 데이터가 중단됐습니다. 데이터 복구와 최신 시세를 확인하기 전에는 실행하지 마세요.'},
    RESEARCH_ONLY: {code: 'RESEARCH', label: '분석 참고 전용', note: '리서치 전용 판단이며 현재 주문 행동으로 사용하지 마세요.'},
  };
  const readinessSeverity = (code) => ({READY: 0, CONDITIONAL: 1, RECHECK: 2, RESEARCH: 3}[code] ?? 3);
  function liveReadiness(row, market, strategy) {
    const base = baseLiveReadiness(row, market);
    const workExecution = strategy.execution || {};
    const declared = String(workExecution.readiness || '').trim().toUpperCase();
    if (!declared) return base;
    const configured = workReadinessPolicy[declared];
    const workGate = configured
      ? {...configured}
      : {code: 'RECHECK', label: 'Work 상태 재확인', note: `알 수 없는 Work 준비 상태(${declared})입니다. 주문 전에 원본 분석을 다시 확인하세요.`};
    const explicitRechecks = valueText(workExecution.required_rechecks);
    if (explicitRechecks && workGate.code !== 'READY') workGate.note = explicitRechecks;
    return readinessSeverity(workGate.code) >= readinessSeverity(base.code) ? workGate : base;
  }
  function sourceChips(value) {
    const entries = Array.isArray(value)
      ? value
      : value && typeof value === 'object'
        ? Object.entries(value).map(([source, detail]) => ({source, detail}))
        : [];
    return entries.map((item) => {
      const source = valueText(item.source || item.name || item.label || item.channel || '출처');
      const detail = valueText(item.detail || item.summary || item.contribution || item.weight || item.confidence || '반영');
      return `<span class="source-chip">${esc(source)} · ${esc(detail)}</span>`;
    }).join('');
  }
  function companyName(row, strategy) {
    const ticker = String(row.ticker || strategy.ticker || '').trim();
    const identities = new Set(tickerKeys(ticker));
    for (const candidate of [row.display_name, strategy.display_name]) {
      const text = String(candidate || '').trim();
      if (text && !identities.has(text.toUpperCase())) return text;
    }
    return ticker || '종목명 확인 필요';
  }
  function evidenceItems(thesis, strategy) {
    const result = [];
    const add = (value, impact = 'mixed', meta = '') => {
      const text = valueText(value).trim();
      if (!text || result.some((item) => item.text === text)) return;
      result.push({text, impact: String(impact || 'mixed').toLowerCase(), meta});
    };
    for (const item of thesis.major_news_issues || []) {
      if (typeof item === 'string') add(item);
      else if (item && typeof item === 'object') add(
        combineDistinct(item.title, item.reason, item.investor_implication),
        item.impact,
        combineDistinct(item.source, item.occurred_at ? dateTime(item.occurred_at) : ''),
      );
    }
    for (const item of thesis.bullish_drivers || thesis.strength_drivers || []) add(item, 'bullish');
    for (const item of thesis.bearish_drivers || thesis.weakness_drivers || []) add(item, 'bearish');
    for (const item of strategy.source_contributions || []) {
      if (!item || typeof item !== 'object') continue;
      add(
        combineDistinct(item.reason, item.summary, item.contribution),
        item.direction || item.impact,
        combineDistinct(item.source, item.event_key),
      );
    }
    if (!result.length) for (const item of thesis.rationale || []) add(item, 'mixed');
    return result.slice(0, 8);
  }
  function evidenceList(thesis, strategy) {
    const items = evidenceItems(thesis, strategy);
    if (!items.length) return '';
    return `<div class="card-rationale"><strong>주요 뉴스·이슈와 강약 이유</strong><ul class="evidence-list">${items.map((item) => `<li class="${['bullish','bearish'].includes(item.impact) ? item.impact : 'mixed'}">${esc(item.text)}${item.meta ? `<small>${esc(item.meta)}</small>` : ''}</li>`).join('')}</ul></div>`;
  }
  function signalStrip(row, confidence) {
    const numericConfidence = Number(confidence);
    const confidenceWidth = Number.isFinite(numericConfidence) ? Math.max(0, Math.min(100, numericConfidence * 100)) : 0;
    const change = Number(row.price_change_pct);
    const changeText = Number.isFinite(change) ? `${change > 0 ? '+' : ''}${change.toFixed(2)}%` : '-';
    return `<div class="signal-strip" aria-label="핵심 신호 요약">
      <div class="signal"><span>분석 신뢰도</span><strong>${Number.isFinite(numericConfidence) ? percent(numericConfidence) : '-'}</strong><div class="confidence-track"><i style="width:${confidenceWidth}%"></i></div></div>
      <div class="signal"><span>당일 등락</span><strong>${esc(changeText)}</strong></div>
      <div class="signal"><span>상대 거래량</span><strong>${fmt(row.relative_volume)}배</strong></div>
    </div>`;
  }
  function rowPriority(row, strategy) {
    const action = row.portfolio_action || {};
    const code = `${action.action_now || ''} ${action.action_if_triggered || ''} ${(strategy.execution || {}).action_now || ''} ${(strategy.thesis || {}).stance || ''}`.toUpperCase();
    let score = /EXIT|STOP|SELL|REDUCE|TRIM|TAKE_PROFIT/.test(code) ? 100 : /BUY|ADD|STARTER/.test(code) ? 80 : row.is_held ? 50 : 20;
    const rank = Number(strategy.rank ?? row.portfolio_priority ?? row.table_priority ?? row.display_priority);
    if (Number.isFinite(rank)) score += Math.max(0, 20 - rank);
    return score;
  }
  function card(row, market, topTickers) {
    const strategy = workStrategy(market, row.ticker);
    const hasWork = Object.keys(strategy).length > 0;
    const thesis = strategy.thesis || {};
    const workExecution = strategy.execution || {};
    const readiness = liveReadiness(row, market, strategy);
    const action = row.portfolio_action || {};
    const role = normalizeRole(strategy.portfolio_role || row.universe_role, row.is_held === true);
    const workConclusion = combineDistinct(thesis.stance ? actionLabel(thesis.stance) : '', workExecution.action_now ? actionLabel(workExecution.action_now) : '');
    const baseConclusion = action.action_now ? actionLabel(action.action_now) : valueText(row.strategy_ko);
    const analysisAction = (hasWork ? workConclusion : baseConclusion) || '결론 정보 없음';
    const workEntryConditions = conciseConditions(thesis.entry_conditions);
    const baseEntryConditions = conciseConditions(row.execution_condition_ko, action.trigger_conditions);
    const entryCondition = (hasWork ? workEntryConditions : baseEntryConditions) || '조건 정보 없음';
    const workTriggeredAction = combineDistinct(
      workExecution.action_if_triggered ? actionLabel(workExecution.action_if_triggered) : '',
      humanPlan(thesis.position_sizing),
    );
    const baseTriggeredAction = combineDistinct(
      action.action_if_triggered ? actionLabel(action.action_if_triggered) : '',
      sizingText(action.delta_krw_if_triggered, action.target_weight_if_triggered),
      humanPlan(action.sell_size_plan),
    );
    const triggeredAction = (hasWork ? workTriggeredAction : baseTriggeredAction) || '행동 계획 정보 없음';
    const workInvalidation = conciseConditions(thesis.invalidation_conditions);
    const baseInvalidation = conciseConditions(row.risk_condition_ko, action.invalidation_condition, action.risk_condition);
    const invalidation = (hasWork ? workInvalidation : baseInvalidation) || '무효화 조건 정보 없음';
    const baseRiskAction = combineDistinct(
      action.risk_action ? actionLabel(action.risk_action) : '',
      humanPlan(action.risk_action_level),
      humanPlan(action.profit_taking_plan),
    );
    const workRiskAction = humanPlan(thesis.invalidation_action || workExecution.risk_action);
    const riskAction = (hasWork ? workRiskAction : baseRiskAction) || '무효화 시 행동 정보 없음';
    const confidence = hasWork ? thesis.confidence : action.confidence;
    const confidenceText = Number.isFinite(Number(confidence)) && Number(confidence) >= 0 && Number(confidence) <= 1 ? percent(confidence) : valueText(confidence);
    const displayName = companyName(row, strategy);
    const tickerIdentity = tickerKeys(row.ticker)[0];
    const fullWorkEntry = fullConditions(thesis.entry_conditions);
    const fullWorkInvalidation = fullConditions(thesis.invalidation_conditions);
    const fullBaseEntry = fullConditions(row.execution_condition_ko, action.trigger_conditions);
    const fullBaseInvalidation = fullConditions(row.risk_condition_ko, action.invalidation_condition, action.risk_condition);
    const supportingDetail = `<details><summary>${hasWork ? '기본 분석·전체 조건 보기' : '전체 조건 보기'}</summary>
      ${hasWork ? `<p><strong>기본 분석 결론</strong><br>${esc(baseConclusion || '정보 없음')}</p>` : ''}
      ${fullWorkEntry ? `<p><strong>Work 전체 진입·축소 조건</strong><br>${esc(fullWorkEntry)}</p>` : ''}
      ${fullWorkInvalidation ? `<p><strong>Work 전체 무효화 조건</strong><br>${esc(fullWorkInvalidation)}</p>` : ''}
      ${fullBaseEntry ? `<p><strong>기본 분석 전체 조건</strong><br>${esc(fullBaseEntry)}</p>` : ''}
      ${fullBaseInvalidation ? `<p><strong>기본 분석 전체 무효화 조건</strong><br>${esc(fullBaseInvalidation)}</p>` : ''}
      ${action.rationale ? `<p><strong>기본 분석 근거</strong><br>${esc(valueText(action.rationale))}</p>` : ''}
    </details>`;
    return `<article class="action-card" data-readiness="${esc(readiness.code)}" data-group="${esc(role)}" data-top="${topTickers.has(tickerIdentity) ? 'true' : 'false'}">
      <div class="card-title"><div><strong>${esc(displayName)} <span class="role-badge">${esc(roleLabel(role))}</span></strong><span class="ticker-code">${esc(row.ticker || '-')}</span></div><span class="row-mode mode-${esc(readiness.code.toLowerCase())}">${esc(readiness.label)}</span></div>
      <div class="price-line"><strong>${fmt(row.last_price)}</strong><span>시세 ${esc(dateTime(row.market_data_asof || workExecution.as_of))}</span></div>
      <div class="private-action"><strong>분석 시점 결론</strong>${esc(analysisAction)}<p class="readiness-note">${esc(readiness.note)}</p></div>
      ${signalStrip(row, confidence)}
      <div class="condition-grid">
        <div class="condition-block"><strong>확인할 진입·축소 조건</strong><p>${esc(entryCondition)}</p></div>
        <div class="condition-block"><strong>조건 충족 후 행동</strong><p>${esc(triggeredAction)}</p></div>
        <div class="condition-block risk"><strong>무효화·손실 제한 조건</strong><p>${esc(invalidation)}</p></div>
        <div class="condition-block risk"><strong>무효화 시 행동</strong><p>${esc(riskAction)}</p></div>
      </div>
      <dl>
        <div><dt>VWAP</dt><dd>${esc(row.vwap_position_ko || '-')}</dd></div>
        <div><dt>상대 거래량</dt><dd>${fmt(row.relative_volume)}배</dd></div>
        <div><dt>분석 신뢰도</dt><dd>${esc(confidenceText || '-')}</dd></div>
      </dl>
      ${evidenceList(thesis, strategy)}
      ${(hasWork ? thesis.rationale : action.rationale) ? `<p class="card-rationale"><strong>종합 판단 근거</strong><br>${esc(valueText(hasWork ? thesis.rationale : action.rationale))}</p>` : ''}
      ${supportingDetail}
      <details><summary>금액·비중·출처 세부 보기</summary><dl>
        <div><dt>현재 증감</dt><dd>${esc(won(action.delta_krw_now))}</dd></div>
        <div><dt>조건부 증감</dt><dd>${esc(won(action.delta_krw_if_triggered))}</dd></div>
        <div><dt>목표 비중</dt><dd>${esc(percent(action.target_weight_now ?? action.target_weight_if_triggered))}</dd></div>
        <div><dt>이익 실현 계획</dt><dd>${esc(humanPlan(action.profit_taking_plan) || '-')}</dd></div>
      </dl><div class="source-chips">${sourceChips(strategy.source_contributions)}</div></details>
    </article>`;
  }
  function workTopAction(item) {
    if (typeof item === 'string') return `<div class="work-action"><strong>${esc(internalCode(item) ? actionLabel(item) : item)}</strong></div>`;
    const title = combineDistinct(item.ticker, item.display_name, item.title) || '핵심 액션';
    const detail = combineDistinct(
      item.action ? actionLabel(item.action) : '',
      item.action_now ? actionLabel(item.action_now) : '',
      item.action_if_triggered ? actionLabel(item.action_if_triggered) : '',
      item.summary,
      item.rationale,
      item.condition,
    );
    return `<div class="work-action"><strong>${esc(title)}</strong>${detail ? `<span>${esc(detail)}</span>` : ''}</div>`;
  }
  function marketOverview(rows, item) {
    const buckets = {BUY: 0, HOLD: 0, REDUCE: 0, SELL: 0, RESEARCH: 0};
    rows.forEach((row) => {
      const strategy = workStrategy(item, row.ticker);
      const stance = String(((strategy.thesis || {}).stance) || '').toUpperCase();
      const action = String(((row.portfolio_action || {}).action_now) || row.strategy_code || '').toUpperCase();
      const combined = `${stance} ${action}`;
      if (/SELL|EXIT|STOP_LOSS/.test(combined)) buckets.SELL += 1;
      else if (/REDUCE|TRIM|TAKE_PROFIT/.test(combined)) buckets.REDUCE += 1;
      else if (/BUY|ADD|STARTER/.test(combined)) buckets.BUY += 1;
      else if (/HOLD|WATCH|WAIT/.test(combined)) buckets.HOLD += 1;
      else buckets.RESEARCH += 1;
    });
    const labels = {BUY: '매수·추가 검토', HOLD: '보유·관찰', REDUCE: '축소·익절', SELL: '매도·청산', RESEARCH: '추가 조사'};
    return `<div class="market-overview" aria-label="전략 분포">${Object.entries(buckets).map(([key, count]) => `<div class="overview-stat"><strong>${count}</strong><span>${labels[key]}</span></div>`).join('')}</div>`;
  }
  function evidenceAudit(sourceSummary) {
    const receipt = ((sourceSummary || {}).external_evidence_receipt || {});
    const sources = receipt.sources || {};
    const rows = ['youtube', 'prism'].map((source) => {
      const payload = sources[source] || {};
      const coverage = payload.coverage || {};
      const transmitted = Number(coverage.transmitted_events ?? (payload.event_keys || []).length ?? 0);
      const windowEvents = Number(coverage.window_events ?? transmitted);
      const omitted = Number(coverage.omitted_events ?? Math.max(0, windowEvents - transmitted));
      const health = String(payload.source_health || 'MISSING').toUpperCase();
      return `<p><strong>${source === 'youtube' ? 'YouTube' : 'PRISM'} · ${esc(health)}</strong><span>전달 ${transmitted} / 검토창 ${windowEvents} · 미전달 ${omitted}</span></p>`;
    }).join('');
    if (!rows || !receipt.schema) return '';
    return `<details class="evidence-audit"><summary>외부 근거 포함·누락 영수증</summary><div class="report-audit-grid">${rows}</div><p class="readiness-note">관련 근거는 순위·신뢰도·위험 한도 안의 비중·조사 우선순위에 반영하되 주문 실행 gate는 우회하지 않습니다.</p></details>`;
  }
  function modelAudit(receipt) {
    if (!receipt || !receipt.schema) return '';
    const analysis = receipt.market_analysis || {};
    const work = receipt.work_synthesis || {};
    const observed = Object.keys(analysis.observed_models || {});
    const analysisModels = observed.length ? observed.join(', ') : Object.values(analysis.requested_models || {}).filter(Boolean).join(', ');
    const analysisStatus = analysis.verification_status === 'RUNTIME_USAGE_OBSERVED' ? '실행 사용량 관측' : '설정만 확인';
    const workStatus = work.verification_status === 'RUNTIME_VERIFIED' ? '런타임 검증' : '설정만 확인 · Chat/Pro 모드 미증명';
    return `<details class="model-audit"><summary>모델 실행 영수증</summary><div class="report-audit-grid">
      <p><strong>종목 분석 · ${esc(analysisStatus)}</strong><span>${esc(analysisModels || '-')} · 호출 ${Number(analysis.observed_calls || 0)}</span></p>
      <p><strong>Work 종합 · ${esc(workStatus)}</strong><span>${esc(work.requested_model || '-')} · reasoning ${esc(work.requested_reasoning_effort || '-')}</span></p>
    </div></details>`;
  }
  function integratedReport(item, field = 'integrated_report') {
    const report = item[field] || {};
    const isReference = field === 'reference_report';
    const analysisOnly = report.analysis_only === true;
    const structured = report.structured_report || {};
    if (!report.report_markdown && !Object.keys(structured).length) return '';
    const title = structured.title || `${item.market || ''} ChatGPT Work 통합 전략`;
    const summary = valueText(structured.summary);
    const topActions = Array.isArray(structured.top_actions) ? structured.top_actions : [];
    const contributions = sourceChips(structured.source_summary);
    return `<section class="integrated-report${isReference ? ' reference-report' : ''}">
      <p class="eyebrow">${isReference ? 'CHATGPT WORK · 분석 시점 참고 전략' : 'CHATGPT WORK · 통합 전략'}</p>
      <h3>${esc(title)}</h3>
      ${isReference ? '<p class="expiry-warning">이 Work 내용은 표시된 분석 시점의 전략입니다. 카드의 투자 논지·근거에는 활용했으며, 실제 실행 준비 상태는 현재 시세 기반 카드 안내를 우선합니다.</p>' : ''}
      ${analysisOnly ? '<p class="readiness-note">Work 종합 전략 전문과 투자 논지·순위·출처를 유지했습니다. 핵심 액션은 분석 시점 참고이며, 카드의 실행 행동과 준비 상태는 현재 장중 갱신 분석을 사용합니다.</p>' : ''}
      <div class="source-meta"><span>분석 기준 ${esc(dateTime(structured.as_of))}</span><span>Work 게시 ${esc(dateTime(report.published_at || structured.generated_at))}</span></div>
      ${summary ? `<p class="summary">${esc(summary)}</p>` : ''}
      ${analysisOnly && topActions.length ? '<p class="readiness-note"><strong>분석 시점 핵심 액션 참고:</strong> 현재 주문 가능 여부가 아니라 Work 분석 당시 제안입니다.</p>' : ''}
      ${topActions.length ? `<div class="work-top-actions">${topActions.slice(0, 3).map(workTopAction).join('')}</div>` : ''}
      ${topActions.length > 3 ? `<details><summary>통합 핵심 액션 전체 보기</summary><div class="work-top-actions">${topActions.map(workTopAction).join('')}</div></details>` : ''}
      ${contributions ? `<div class="source-chips">${contributions}</div>` : ''}
      ${evidenceAudit(structured.source_summary)}
      ${modelAudit(structured.model_receipt)}
      ${structured.next_checkpoint ? `<p class="readiness-note"><strong>다음 확인:</strong> ${esc(valueText(structured.next_checkpoint))}</p>` : ''}
      ${report.report_markdown ? `<details><summary>통합 리포트 전체 보기</summary><pre class="markdown-report">${esc(report.report_markdown)}</pre></details>` : ''}
    </section>`;
  }
  function marketHealth(item, rows) {
    const sourceHealth = String((item || {}).source_health || 'MISSING').toUpperCase();
    const sourceStatus = String(((item || {}).source || {}).status || (item || {}).manifest_status || '').toLowerCase();
    const coverage = (item || {}).universe_coverage || (item || {}).coverage || {};
    const validUntil = Date.parse(((item || {}).guardrails || {}).valid_until || '');
    const expired = ((item || {}).guardrails || {}).expired_at_build === true || !Number.isFinite(validUntil) || validUntil <= Date.now();
    if (!rows.length) return {className: 'missing', label: '전략 행 없음', empty: '현재 확인 가능한 전략 행이 없습니다. 분석 커버리지가 복구된 뒤 다시 확인하세요.'};
    if (sourceHealth === 'MISSING' || sourceHealth === 'FAILED' || ['failed', 'error'].includes(sourceStatus)) {
      return {className: 'missing', label: '원천 분석 사용 불가', empty: '원천 분석을 사용할 수 없어 현재 전략을 실행 판단에 쓰지 마세요.'};
    }
    if (coverage.status !== 'COMPLETE' || coverage.complete !== true) {
      return {className: 'missing', label: '커버리지 불완전', empty: '필수 종목 분석이 불완전합니다. 누락 분석이 복구될 때까지 기다리세요.'};
    }
    if (sourceHealth !== 'OK' || expired) {
      return {className: 'degraded', label: expired ? '주문 전 실시간 확인' : '원천 상태 재확인', empty: ''};
    }
    if (immediateContractComplete(item)) return {className: 'ok', label: '실행 데이터 확인됨', empty: ''};
    return {className: 'degraded', label: '전략 제공 · 주문 전 확인', empty: ''};
  }
  function render(payload) {
    const markets = payload.markets || {};
    if (requestedRun && String((markets[requestedMarket] || {}).run_id || '') !== requestedRun) {
      throw new Error('Telegram 링크의 분석 run과 현재 개인 대시보드 run이 일치하지 않습니다. 최신 알림을 사용하세요.');
    }
    tabs.hidden = false;
    tabs.innerHTML = ['kr', 'us'].map((market, index) => `<button type="button" data-target="${market}" aria-pressed="${index === 0}">${market.toUpperCase()}</button>`).join('');
    root.innerHTML = ['kr', 'us'].map((market) => {
      const item = markets[market] || {};
      const rows = Array.isArray(item.rows) ? item.rows : [];
      const ranked = [...rows].sort((left, right) => rowPriority(right, workStrategy(item, right.ticker)) - rowPriority(left, workStrategy(item, left.ticker)));
      const topTickers = new Set(ranked.slice(0, Math.min(3, ranked.length)).map((row) => tickerKeys(row.ticker)[0]));
      const counts = item.role_counts || {};
      const sourceLabel = item.integrated_report
        ? item.integrated_report.analysis_only === true ? 'Work 분석 결합 · 현재 실행 우선' : '현재 Work 종합 완료'
        : item.reference_report ? '기본 전략 · 분석 시점 Work 참고' : '기본 전략';
      const health = marketHealth(item, rows);
      const cards = ranked.map((row) => card(row, item, topTickers)).join('');
      const empty = health.empty || '현재 표시할 전략 데이터가 없습니다. 원천 상태와 분석 커버리지를 확인하세요.';
      return `<section class="market-panel" data-market="${market}"><div class="market-head"><div><p class="eyebrow">${market.toUpperCase()} STRATEGY</p><h2>${market.toUpperCase()} 투자 액션</h2></div><div><span class="health health-neutral">${esc(sourceLabel)}</span><span class="health health-${esc(health.className)}">${esc(health.label)}</span></div></div><div class="source-meta"><span>분석 시작 ${esc(dateTime(item.started_at))}</span><span>분석 run ${esc(item.run_id || '-')}</span><span>${rows.length}개 종목</span></div>${marketOverview(rows, item)}<nav class="strategy-filters" aria-label="종목 유형"><button type="button" data-group-target="TOP" aria-pressed="true">핵심 ${topTickers.size}</button><button type="button" data-group-target="HOLDING" aria-pressed="false">보유 ${counts.HOLDING || 0}</button><button type="button" data-group-target="WATCHLIST" aria-pressed="false">관심 ${counts.WATCHLIST || 0}</button><button type="button" data-group-target="NEW_CANDIDATE" aria-pressed="false">신규 ${counts.NEW_CANDIDATE || 0}</button><button type="button" data-group-target="ALL" aria-pressed="false">전체 ${rows.length}</button></nav><div class="cards">${cards || `<p class="empty">${esc(empty)}</p>`}</div>${integratedReport(item)}${integratedReport(item, 'reference_report')}</section>`;
    }).join('');
    const buttons = [...tabs.querySelectorAll('button')];
    const panels = [...root.querySelectorAll('[data-market]')];
    const select = (market) => { buttons.forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.target === market))); panels.forEach((panel) => panel.hidden = panel.dataset.market !== market); };
    buttons.forEach((button) => button.addEventListener('click', () => select(button.dataset.target)));
    panels.forEach((panel) => {
      const filters = [...panel.querySelectorAll('[data-group-target]')];
      const cards = [...panel.querySelectorAll('.action-card')];
      const selectGroup = (group) => {
        filters.forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.groupTarget === group)));
        cards.forEach((entry) => { entry.hidden = group === 'TOP' ? entry.dataset.top !== 'true' : group !== 'ALL' && entry.dataset.group !== group; });
      };
      filters.forEach((button) => button.addEventListener('click', () => selectGroup(button.dataset.groupTarget)));
      selectGroup('TOP');
    });
    select(requestedMarket);
    status.textContent = `페이지 생성 ${dateTime(payload.generated_at)} · 계좌 식별정보 제외 · PC/모바일/JSON 공개`;
    clearTimeout(expiryTimer);
    const now = Date.now();
    const deadlines = Object.values(markets).flatMap((item) => [
      Date.parse((item.guardrails || {}).valid_until || ''),
      ...(item.rows || []).map((row) => Date.parse((row.quality || {}).row_valid_until || '')),
    ]).filter((deadline) => Number.isFinite(deadline) && deadline > now);
    if (deadlines.length) expiryTimer = setTimeout(() => render(payload), Math.max(50, Math.min(...deadlines) - now + 50));
  }
  async function start() {
    const response = await fetch(document.body.dataset.strategyUrl || 'strategy.json', {cache: 'no-store', credentials: 'omit'});
    if (!response.ok) throw new Error('통합 투자 전략이 아직 게시되지 않았습니다.');
    const payload = await response.json();
    if (payload.schema !== 'tradingagents.mobile-strategy/v1') throw new Error('통합 전략 데이터 형식이 올바르지 않습니다.');
    render(payload);
  }
  start().catch((error) => { status.classList.add('error'); status.textContent = error.message || '통합 투자 전략을 열 수 없습니다.'; root.replaceChildren(); });
})();
""".strip()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def _join_url(base: str, suffix: str) -> str:
    root = str(base or "").strip().rstrip("/")
    return f"{root}/{suffix.lstrip('/')}" if root else suffix


def _llms_text(*, public_base_url: str, generated_at: str) -> str:
    base = str(public_base_url or "").strip().rstrip("/")
    links = (
        ("PC 종합 투자 전략", "strategy.html"),
        ("모바일 종합 투자 전략", "mobile/strategy.html"),
        ("기계 판독용 KR/US 종합 전략 JSON", "mobile/strategy.json"),
        ("KR/US 공개 리서치 JSON", "mobile/public.json"),
        ("YouTube 검증 리포트와 JSON feed", "youtube/"),
        ("PRISM 리포트", "prism-telegram/"),
        ("ChatGPT Work 공개 원문", "work/"),
    )
    rendered = "\n".join(
        f"- {label}: {_join_url(base, path)}" for label, path in links
    )
    return (
        "# TradingAgents public investment research\n\n"
        "This site intentionally exposes account-identifier-free KR/US investment "
        "research for browsers, search engines, ChatGPT, and other AI agents.\n"
        f"Site build time: {generated_at}\n\n"
        "The HTML is a human-readable view of the same public JSON. `as_of` is the "
        "analysis time, while `generated_at`/`published_at` identify report publication. "
        "Do not infer current order eligibility from an old analysis timestamp.\n\n"
        f"{rendered}\n"
    )


def _sitemap_xml(public_base_url: str) -> str:
    base = str(public_base_url or "").strip().rstrip("/")
    urls = (
        "",
        "strategy.html",
        "mobile/",
        "mobile/strategy.html",
        "youtube/",
        "prism-telegram/",
        "work/",
    )
    entries = "\n".join(
        f"  <url><loc>{html.escape(_join_url(base, suffix))}</loc></url>"
        for suffix in urls
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n"
    )


def _escape(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def _css_token(value: Any) -> str:
    return "".join(character.lower() if character.isalnum() else "_" for character in str(value or "missing")).strip("_") or "missing"


def _source_health_label(value: Any) -> str:
    return {
        "OK": "데이터 수집 완료",
        "DEGRADED": "일부 데이터 재확인",
        "STALE": "주문 전 실시간 재확인",
        "FAILED": "데이터 확인 필요",
        "MISSING": "데이터 확인 필요",
    }.get(str(value or "MISSING").strip().upper(), "데이터 확인 필요")


def _fmt_price(value: Any) -> str:
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return "-"


def _fmt_ratio(value: Any) -> str:
    try:
        return f"{float(value):.2f}배"
    except (TypeError, ValueError):
        return "-"
