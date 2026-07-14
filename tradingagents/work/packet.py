from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable


WORK_SCHEMA = "tradingagents.work-context/v1"
WORK_STATE_SCHEMA = "tradingagents.work-state/v1"
SURFACES = ("kr", "us", "youtube", "prism")
PROMPT_CONTRACTS = {
    "kr": "market-work-v4-kr",
    "us": "market-work-v4-us",
    "youtube": "youtube-work-v3",
    "prism": "prism-work-v3",
}
PROMPT_FILENAMES = {
    "kr": "market_kr.md",
    "us": "market_us.md",
    "youtube": "youtube.md",
    "prism": "prism.md",
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_json(payload: Any) -> str:
    return sha256_text(canonical_json(payload))


def prompt_path(surface: str) -> Path:
    key = _surface(surface)
    return Path(__file__).with_name("prompts") / PROMPT_FILENAMES[key]


def prompt_text(surface: str) -> str:
    return prompt_path(surface).read_text(encoding="utf-8")


def workflow_contract_hashes(surface: str) -> dict[str, str]:
    key = _surface(surface)
    repo_root = Path(__file__).resolve().parents[2]
    skill = repo_root / ".agents" / "skills" / "tradingagents-daily-investment-work" / "SKILL.md"
    task_manifest = repo_root / "config" / "chatgpt_work_tasks.json"
    return {
        "prompt_sha256": sha256_bytes(prompt_path(key).read_bytes()),
        "skill_sha256": sha256_bytes(skill.read_bytes()) if skill.is_file() else sha256_text("skill-unavailable"),
        "task_manifest_sha256": (
            sha256_bytes(task_manifest.read_bytes()) if task_manifest.is_file() else sha256_text("task-manifest-unavailable")
        ),
    }


def compact_decision_bundle(
    bundle: dict[str, Any],
    *,
    max_new_candidates: int = 5,
) -> dict[str, Any]:
    if not bundle:
        return {}
    rows = [row for row in (bundle.get("strategy_table") or []) if isinstance(row, dict)]
    held = [row for row in rows if row.get("is_held") is True]
    nonheld = [row for row in rows if row.get("is_held") is not True]
    selected = [*held, *nonheld[: max(0, int(max_new_candidates))]]
    compact_rows = [_compact_market_row(row, index) for index, row in enumerate(selected, start=1)]
    selected_benchmarks = {
        str(sync.get("benchmark") or "")
        for row in compact_rows
        for sync in (row.get("sector_sync") or {}, row.get("index_sync") or {})
        if isinstance(sync, dict) and str(sync.get("benchmark") or "")
    }
    benchmark_context = bundle.get("benchmark_context") if isinstance(bundle.get("benchmark_context"), dict) else {}
    return {
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
            "quality",
            "summary",
        )
        if bundle.get(key) is not None
    } | {
        "strategy_table": compact_rows,
        "benchmark_context": {
            str(key): value
            for key, value in benchmark_context.items()
            if str(key) in selected_benchmarks
        },
        "transmission_scope": {
            "source_ticker_count": len(rows),
            "transmitted_ticker_count": len(compact_rows),
            "held_ticker_count": len(held),
            "new_candidate_limit": int(max_new_candidates),
            "omitted_nonheld_ticker_count": max(0, len(nonheld) - int(max_new_candidates)),
            "all_holdings_included": len([row for row in compact_rows if row.get("is_held")]) == len(held),
            "raw_codes_omitted": True,
        },
    }


def _compact_market_row(row: dict[str, Any], display_priority: int) -> dict[str, Any]:
    fields = (
        "table_priority",
        "portfolio_priority",
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
        "staleness_seconds",
        "orderbook_imbalance",
        "execution_strength",
        "investor_flow_status",
        "program_flow_status",
        "vi_status",
        "market_alert_status",
        "halt_status",
        "luld_status",
        "reg_sho_status",
        "news_halt_status",
        "provider",
        "market_session",
        "quote_delay_seconds",
        "source_latency_seconds",
        "confidence",
        "sector_sync",
        "index_sync",
        "sync_summary_ko",
        "execution_condition_ko",
        "risk_condition_ko",
        "data_status_ko",
        "decision_state_ko",
        "execution_timing_ko",
        "reason_codes_ko",
        "quality",
    )
    compact = {key: row.get(key) for key in fields if row.get(key) is not None}
    quality = dict(compact.get("quality") or {})
    if not quality.get("row_mode"):
        if quality.get("execution_ready") is True:
            quality["row_mode"] = "IMMEDIATE"
        elif quality.get("conditional_strategy_ready") is True:
            quality["row_mode"] = "CONDITIONAL"
        elif (
            quality.get("generated_in_current_run") is not True
            or "PRIOR" in str(quality.get("freshness_class") or "").upper()
            or "STALE" in str(quality.get("freshness_class") or "").upper()
            or "HISTORICAL" in str(quality.get("execution_eligibility") or "").upper()
        ):
            quality["row_mode"] = "BLOCKED_STALE"
        else:
            quality["row_mode"] = "MISSING"
    compact["quality"] = quality
    compact["display_priority"] = display_priority
    return compact


def build_surface_packet(
    surface: str,
    *,
    archive_dir: Path | None = None,
    youtube_archive_dir: Path | None = None,
    prism_archive_dir: Path | None = None,
    now: datetime | None = None,
    public: bool = False,
) -> dict[str, Any]:
    key = _surface(surface)
    now = now or datetime.now().astimezone()
    roots = resolve_archive_roots(
        archive_dir=archive_dir,
        youtube_archive_dir=youtube_archive_dir,
        prism_archive_dir=prism_archive_dir,
    )
    if key in {"kr", "us"}:
        body = _market_body(key, roots=roots, now=now, public=public)
    elif key == "youtube":
        body = _youtube_body(roots["youtube"], now=now)
    else:
        body = _prism_body(roots["prism"], now=now)
    return _seal_packet(key, body=body)


def resolve_archive_roots(
    *,
    archive_dir: Path | None = None,
    youtube_archive_dir: Path | None = None,
    prism_archive_dir: Path | None = None,
) -> dict[str, Path]:
    explicit_primary = archive_dir is not None
    primary = Path(
        archive_dir
        or os.getenv("TRADINGAGENTS_ARCHIVE_DIR", "").strip()
        or _first_existing(Path("C:/TradingAgentsData/archive"), Path(".runtime/tradingagents-archive"))
    )
    youtube = Path(
        youtube_archive_dir
        or os.getenv("TRADINGAGENTS_YOUTUBE_ARCHIVE_DIR", "").strip()
        or (
            primary / "youtube-archive"
            if explicit_primary
            else _first_existing(primary / "youtube-archive", Path(".runtime/youtube-archive"))
        )
    )
    prism = Path(
        prism_archive_dir
        or os.getenv("TRADINGAGENTS_PRISM_TELEGRAM_ARCHIVE_DIR", "").strip()
        or (
            primary / "prism-telegram-archive"
            if explicit_primary
            else _first_existing(Path("C:/TradingAgentsData/prism-telegram-archive"), primary / "prism-telegram-archive", Path(".runtime/prism-telegram-archive"))
        )
    )
    return {"market": primary, "youtube": youtube, "prism": prism}


def _market_body(surface: str, *, roots: dict[str, Path], now: datetime, public: bool) -> dict[str, Any]:
    sources = _market_sources(roots["market"], surface)
    if not sources:
        return {
            "kind": "market",
            "market": surface.upper(),
            "source_health": "MISSING",
            "report_mode": "RESEARCH",
            "current": {},
            "last_ready": {},
            "supporting_context": _supporting_context(roots, now=now),
            "guardrails": _market_guardrails(surface, {}, now=now),
        }
    current = sources[0]
    ready = next(
        (
            item
            for item in sources
            if bool(((item.get("bundle") or {}).get("quality") or {}).get("decision_ready"))
        ),
        None,
    )
    bundle = (
        _compact_public_market_bundle(current["bundle"])
        if public
        else compact_decision_bundle(current["bundle"])
    )
    _apply_market_row_validity(bundle, now=now)
    current_payload: dict[str, Any] = {
        "run_id": current["manifest"].get("run_id"),
        "started_at": current["manifest"].get("started_at"),
        "run_mode": ((current["manifest"].get("settings") or {}).get("run_mode")),
        "bundle": bundle,
    }
    if not public:
        private_overlay = _local_private_overlay(current["run_dir"], current["manifest"], bundle)
        if private_overlay:
            current_payload["private_portfolio_overlay"] = private_overlay
    last_ready = {}
    if ready:
        last_ready = {
            "run_id": ready["manifest"].get("run_id"),
            "started_at": ready["manifest"].get("started_at"),
            "same_as_current": ready["manifest"].get("run_id") == current["manifest"].get("run_id"),
            "same_session": _session_id(surface, ready["bundle"]) == _session_id(surface, current["bundle"]),
            "reference_only": ready["manifest"].get("run_id") != current["manifest"].get("run_id"),
        }
    quality = bundle.get("quality") or {}
    mode = str(quality.get("report_mode") or _market_report_mode(bundle)).upper()
    guardrails = _market_guardrails(surface, bundle, now=now)
    manifest_status = str(current["manifest"].get("status") or "unknown").strip().lower()
    if guardrails.get("expired_at_build") is True:
        source_health = "STALE"
    elif manifest_status in {"failed", "failure", "error"}:
        source_health = "FAILED"
    elif manifest_status in {"partial", "partial_failure", "degraded"}:
        source_health = "DEGRADED"
    else:
        source_health = "OK"
    return {
        "kind": "market",
        "market": surface.upper(),
        "session_id": _session_id(surface, current["bundle"]),
        "source_health": source_health,
        "source": {
            "run_id": current["manifest"].get("run_id"),
            "last_run_at": current["manifest"].get("finished_at") or current["manifest"].get("started_at"),
            "status": current["manifest"].get("status"),
        },
        "report_mode": mode,
        "current": current_payload,
        "last_ready": last_ready,
        "supporting_context": _supporting_context(roots, now=now),
        "guardrails": guardrails,
    }


def _compact_public_market_bundle(bundle: dict[str, Any], *, max_candidates: int = 5) -> dict[str, Any]:
    """Build a recovery packet without publishing portfolio membership or actions."""

    if not bundle:
        return {}
    rows = [
        row
        for row in (bundle.get("strategy_table") or [])
        if isinstance(row, dict) and row.get("is_held") is not True
    ][: max(0, int(max_candidates))]
    compact_rows = []
    for index, row in enumerate(rows, start=1):
        compact = _compact_market_row(row, index)
        for key in (
            "is_held",
            "portfolio_priority",
            "strategy_code",
            "strategy_ko",
            "execution_condition_ko",
            "risk_condition_ko",
            "decision_state_ko",
            "execution_timing_ko",
        ):
            compact.pop(key, None)
        quality = compact.get("quality") if isinstance(compact.get("quality"), dict) else {}
        compact["quality"] = {
            key: quality.get(key)
            for key in (
                "row_mode",
                "execution_ready",
                "conditional_strategy_ready",
                "current_execution_promotion",
                "generated_in_current_run",
                "freshness_class",
                "execution_eligibility",
                "data_status",
                "provider_status",
            )
            if quality.get(key) is not None
        }
        compact_rows.append(compact)
    quality = bundle.get("quality") if isinstance(bundle.get("quality"), dict) else {}
    public_quality = {
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
    public_quality["portfolio_membership_omitted"] = True
    return {
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
    } | {
        "quality": public_quality,
        "strategy_table": compact_rows,
        "benchmark_context": {},
        "transmission_scope": {
            "public_recovery_only": True,
            "portfolio_membership_omitted": True,
            "transmitted_research_candidate_count": len(compact_rows),
            "raw_codes_omitted": True,
        },
    }


def _apply_market_row_validity(bundle: dict[str, Any], *, now: datetime) -> None:
    current_now = now.astimezone()
    for row in bundle.get("strategy_table") or []:
        if not isinstance(row, dict):
            continue
        quality = row.get("quality") if isinstance(row.get("quality"), dict) else {}
        parsed = _datetime(row.get("market_data_asof"))
        valid_until = parsed + timedelta(minutes=30) if parsed else None
        expired = bool(valid_until and valid_until < current_now.astimezone(valid_until.tzinfo))
        quality["row_valid_until"] = valid_until.isoformat() if valid_until else None
        quality["expired_at_build"] = expired
        if expired and quality.get("row_mode") in {"IMMEDIATE", "CONDITIONAL"}:
            quality["source_row_mode"] = quality.get("row_mode")
            quality["row_mode"] = "BLOCKED_STALE"
            quality["execution_ready"] = False
            quality["conditional_strategy_ready"] = False
            blockers = [str(item) for item in (quality.get("provider_blockers") or []) if str(item)]
            quality["provider_blockers"] = list(dict.fromkeys([*blockers, "work_packet_row_expired"]))
        row["quality"] = quality


def _market_sources(archive_dir: Path, market: str) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    runs_root = Path(archive_dir) / "runs"
    if not runs_root.exists():
        return sources
    candidates = list(runs_root.glob("*/*/run.json"))
    if not candidates:
        candidates = list(runs_root.rglob("run.json"))
    candidates.sort(key=_manifest_path_recency, reverse=True)
    for manifest_path in candidates[:240]:
        manifest = load_json(manifest_path)
        configured_market = str(((manifest.get("settings") or {}).get("market") or manifest.get("market") or "")).lower()
        if configured_market != market:
            continue
        run_dir = manifest_path.parent
        artifact = ((manifest.get("decision_bundle") or {}).get("artifacts") or {}).get("decision_bundle_v2_json")
        bundle_path = _safe_artifact(run_dir, artifact) if artifact else run_dir / "decision_bundle_v2.json"
        bundle = load_json(bundle_path)
        if not bundle:
            continue
        sources.append({"manifest": manifest, "bundle": bundle, "run_dir": run_dir})
        if bool((bundle.get("quality") or {}).get("decision_ready")):
            break
    sources.sort(key=lambda item: str(item["manifest"].get("started_at") or item["manifest"].get("run_id") or ""), reverse=True)
    return sources


def _manifest_path_recency(path: Path) -> tuple[int, str]:
    try:
        modified = path.stat().st_mtime_ns
    except OSError:
        modified = 0
    return modified, path.parent.name


def _local_private_overlay(run_dir: Path, manifest: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
    artifacts = ((manifest.get("portfolio") or {}).get("artifacts") or {})
    report = load_json(_safe_artifact(run_dir, artifacts.get("portfolio_report_json")))
    selected = {str(row.get("ticker") or "").upper() for row in (bundle.get("strategy_table") or [])}
    actions = []
    for action in report.get("actions") or []:
        if not isinstance(action, dict):
            continue
        ticker = str(action.get("canonical_ticker") or action.get("ticker") or "").upper()
        if ticker not in selected:
            continue
        actions.append(
            {
                key: action.get(key)
                for key in (
                    "canonical_ticker",
                    "confidence",
                    "action_now",
                    "delta_krw_now",
                    "target_weight_now",
                    "action_if_triggered",
                    "delta_krw_if_triggered",
                    "target_weight_if_triggered",
                    "strategy_state",
                    "execution_feasibility_now",
                    "portfolio_relative_action",
                    "risk_action",
                    "sell_side_category",
                    "sell_intent",
                    "sell_size_plan",
                    "position_metrics",
                    "profit_taking_plan",
                    "reason_codes",
                    "gate_reasons",
                )
                if action.get(key) is not None
            }
        )
    return {
        "privacy": "LOCAL_ONLY_DO_NOT_PUBLISH",
        "actions": actions,
    } if actions else {}


def _youtube_body(archive_dir: Path, *, now: datetime) -> dict[str, Any]:
    events: dict[str, dict[str, Any]] = {}
    manifests = _source_manifests(archive_dir, "youtube_run.json")
    for manifest, run_dir in manifests:
        for item in manifest.get("videos") or []:
            if not isinstance(item, dict) or not item.get("video_id"):
                continue
            event = _youtube_event(item, run_dir)
            if not event:
                continue
            previous = events.get(str(event["event_key"]))
            if previous is None or str(event.get("occurred_at") or "") > str(previous.get("occurred_at") or ""):
                events[str(event["event_key"])] = event
    ordered = sorted(events.values(), key=lambda item: str(item.get("occurred_at") or ""), reverse=True)
    cutoff = now.astimezone().timestamp() - 72 * 3600
    included = [item for item in ordered if (_timestamp(item.get("occurred_at")) or 0) >= cutoff]
    window_count = len(included)
    included = included[:30]
    source = _producer_snapshot(manifests, event_count=window_count, now=now, stale_after_hours=36)
    return {
        "kind": "youtube",
        "source_health": source["health"],
        "source": source,
        "window_hours": 72,
        "execution_eligible": False,
        "coverage": {
            "total_unique_events": len(ordered),
            "window_events": window_count,
            "transmitted_events": len(included),
            "truncated": len(included) < window_count,
            "oldest_occurred_at": included[-1].get("occurred_at") if included else None,
            "newest_occurred_at": included[0].get("occurred_at") if included else None,
        },
        "events": included,
        "guardrails": {
            "untrusted_content": True,
            "may_promote_market_execution": False,
            "allowed_actions": [
                "UPGRADE_RESEARCH",
                "UPGRADE_WATCH",
                "MAINTAIN",
                "DOWNGRADE_WATCH",
                "DOWNGRADE_RISK",
                "EXCLUDE",
                "REQUIRES_PRIMARY_VERIFICATION",
                "NO_ACTIONABLE_DELTA",
            ],
        },
    }


def _youtube_event(item: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    summary = load_json(_safe_artifact(run_dir, item.get("public_summary_path")))
    if not summary:
        summary = {key: item.get(key) for key in ("video_id", "title", "channel", "video_url", "published_at", "status")}
    compact = {
        "video_id": summary.get("video_id") or item.get("video_id"),
        "title": summary.get("title") or item.get("title"),
        "channel": summary.get("channel") or item.get("channel"),
        "source_url": summary.get("url") or item.get("video_url"),
        "published_at": summary.get("published_at") or item.get("published_at"),
        "status": summary.get("status") or item.get("status"),
        "transcript_quality": summary.get("transcript_quality"),
        "claim_status_summary": summary.get("claim_status_summary"),
        "claims": [
            {
                key: _truncate_value(claim.get(key), 280)
                for key in (
                    "claim_id",
                    "claim_text",
                    "status",
                    "confidence",
                    "supporting_evidence_ids",
                    "manual_check_required",
                    "investor_implication",
                )
                if claim.get(key) is not None
            }
            for claim in (summary.get("claims") or [])[:3]
            if isinstance(claim, dict)
        ],
        "entities": [
            {
                key: _truncate_value(entity.get(key), 220)
                for key in ("ticker", "name", "status", "verification_notes")
                if entity.get(key) is not None
            }
            for entity in (summary.get("entities") or [])[:4]
            if isinstance(entity, dict)
        ],
        "evidence": [
            {
                key: evidence.get(key)
                for key in (
                    "evidence_id",
                    "claim_id",
                    "title",
                    "source_url",
                    "publisher",
                    "published_at",
                    "source_tier",
                )
                if evidence.get(key) is not None
            }
            for evidence in (summary.get("evidence") or [])[:3]
            if isinstance(evidence, dict)
        ],
    }
    content_sha = sha256_json(compact)
    return {
        "event_key": str(compact.get("video_id")),
        "content_sha256": content_sha,
        "occurred_at": compact.get("published_at"),
        "summary": compact,
    }


def _prism_body(archive_dir: Path, *, now: datetime) -> dict[str, Any]:
    events: dict[str, dict[str, Any]] = {}
    manifests = _source_manifests(archive_dir, "prism_telegram_run.json")
    for manifest, run_dir in manifests:
        channel = str((manifest.get("source") or {}).get("channel") or "stock_ai_agent")
        for message in manifest.get("messages") or []:
            if not isinstance(message, dict) or not message.get("message_id"):
                continue
            event = _prism_event(channel, message, run_dir)
            previous = events.get(str(event["event_key"]))
            if previous is None or str(event.get("occurred_at") or "") > str(previous.get("occurred_at") or ""):
                events[str(event["event_key"])] = event
    ordered = sorted(events.values(), key=lambda item: str(item.get("occurred_at") or ""), reverse=True)
    cutoff = now.astimezone().timestamp() - 24 * 3600
    window = [item for item in ordered if (_timestamp(item.get("occurred_at")) or 0) >= cutoff]
    included = window[:80]
    source = _producer_snapshot(manifests, event_count=len(window), now=now, stale_after_hours=30)
    return {
        "kind": "prism",
        "source_health": source["health"],
        "source": source,
        "window_hours": 24,
        "execution_eligible": False,
        "coverage": {
            "total_unique_events": len(ordered),
            "window_events": len(window),
            "transmitted_events": len(included),
            "truncated": len(included) < len(window),
            "oldest_occurred_at": included[-1].get("occurred_at") if included else None,
            "newest_occurred_at": included[0].get("occurred_at") if included else None,
        },
        "events": included,
        "guardrails": {
            "untrusted_content": True,
            "advisory_only": True,
            "may_promote_market_execution": False,
            "multi_ticker_message_prices_require_recheck": True,
        },
    }


def _prism_event(channel: str, message: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    signals_payload = load_json(_safe_artifact(run_dir, message.get("signals_path")))
    preview = str(message.get("text_preview") or "")[:1200]
    simulation = "시뮬" in preview or "simulation" in preview.lower()
    signals = []
    source_signals = [item for item in (signals_payload.get("signals") or []) if isinstance(item, dict)]
    for signal in source_signals[:8]:
        if not isinstance(signal, dict):
            continue
        signals.append(
            {
                key: _truncate_value(signal.get(key), 300)
                for key in (
                    "canonical_ticker",
                    "display_name",
                    "market",
                    "source_asof",
                    "signal_action",
                    "trigger_type",
                    "trigger_score",
                    "composite_score",
                    "risk_reward_ratio",
                    "stop_loss_price",
                    "target_price",
                    "confidence",
                    "warnings",
                )
                if signal.get(key) is not None
            }
        )
    compact = {
        "channel": channel,
        "message_id": str(message.get("message_id")),
        "posted_at": message.get("posted_at"),
        "source_url": message.get("url"),
        "preview": preview,
        "signals": signals,
        "signals_total": len(source_signals),
        "signals_transmitted": len(signals),
        "signals_truncated": len(signals) < len(source_signals),
        "simulation_only": simulation,
        "actionability": "research_only",
    }
    return {
        "event_key": f"{channel}:{message.get('message_id')}",
        "content_sha256": sha256_json(compact),
        "occurred_at": message.get("posted_at"),
        "summary": compact,
    }


def _supporting_context(roots: dict[str, Path], *, now: datetime) -> dict[str, Any]:
    youtube = _youtube_body(roots["youtube"], now=now)
    prism = _prism_body(roots["prism"], now=now)
    return {
        "youtube": {
            "source_health": youtube.get("source_health"),
            "coverage": youtube.get("coverage"),
            "events": [_compact_support_event(item, kind="youtube") for item in (youtube.get("events") or [])[:3]],
            "execution_eligible": False,
        },
        "prism": {
            "source_health": prism.get("source_health"),
            "coverage": prism.get("coverage"),
            "events": [_compact_support_event(item, kind="prism") for item in (prism.get("events") or [])[:5]],
            "execution_eligible": False,
        },
    }


def _compact_support_event(event: dict[str, Any], *, kind: str) -> dict[str, Any]:
    summary = event.get("summary") if isinstance(event.get("summary"), dict) else {}
    base = {
        "event_key": event.get("event_key"),
        "content_sha256": event.get("content_sha256"),
        "occurred_at": event.get("occurred_at"),
    }
    if kind == "youtube":
        base["summary"] = {
            "video_id": summary.get("video_id"),
            "title": summary.get("title"),
            "channel": summary.get("channel"),
            "source_url": summary.get("source_url"),
            "claim_status_summary": summary.get("claim_status_summary"),
            "claims": (summary.get("claims") or [])[:2],
        }
    else:
        base["summary"] = {
            "message_id": summary.get("message_id"),
            "posted_at": summary.get("posted_at"),
            "source_url": summary.get("source_url"),
            "preview": _truncate_value(summary.get("preview"), 500),
            "signals": (summary.get("signals") or [])[:5],
            "simulation_only": summary.get("simulation_only"),
            "actionability": "research_only",
        }
    return base


def _market_guardrails(surface: str, bundle: dict[str, Any], *, now: datetime) -> dict[str, Any]:
    rows = bundle.get("strategy_table") or []
    asofs = [str(row.get("market_data_asof")) for row in rows if isinstance(row, dict) and row.get("market_data_asof")]
    latest_asof = max(asofs) if asofs else None
    actionable_validities = [
        _datetime((row.get("quality") or {}).get("row_valid_until"))
        for row in rows
        if isinstance(row, dict) and (row.get("quality") or {}).get("row_mode") == "IMMEDIATE"
    ]
    actionable_validities = [value for value in actionable_validities if value is not None]
    fallback = _datetime(latest_asof) or _datetime(bundle.get("generated_at"))
    valid_datetime = min(actionable_validities) if actionable_validities else (fallback + timedelta(minutes=30) if fallback else None)
    valid_until = valid_datetime.isoformat() if valid_datetime else None
    required = ["실시간 호가와 주문 가능 상태 재확인", "계좌 현금·미체결 주문 재확인"]
    if surface == "kr":
        required.append("VI·시장경보·거래정지·투자자/프로그램 수급 상태 재확인")
    else:
        required.append("NBBO/스프레드·LULD·뉴스 halt·feed 지연 상태 재확인")
    return {
        "untrusted_external_context": True,
        "global_mode_cannot_promote_a_row": True,
        "immediate_requires_row_mode": "IMMEDIATE",
        "market_data_asof": latest_asof,
        "valid_until": valid_until,
        "expired_at_build": bool(valid_until and (_datetime(valid_until) or now) < now.astimezone((_datetime(valid_until) or now).tzinfo)),
        "required_rechecks": required,
        "stale_buy_sell_reduce_is_reference_only": True,
        "supporting_context_may_promote_execution": False,
    }


def _seal_packet(surface: str, *, body: dict[str, Any]) -> dict[str, Any]:
    contract_hashes = workflow_contract_hashes(surface)
    semantic_source_sha = sha256_json(body)
    contract = PROMPT_CONTRACTS[surface]
    workflow_contract_sha = sha256_json({"version": contract, **contract_hashes})
    event_material = {
        "schema": WORK_SCHEMA,
        "surface": surface,
        "prompt_contract_version": contract,
        "workflow_contract_sha256": workflow_contract_sha,
        "source_sha256": semantic_source_sha,
    }
    event_id = f"{surface}:{sha256_json(event_material)[:32]}"
    return {
        "schema": WORK_SCHEMA,
        "surface": surface,
        "event_id": event_id,
        "prompt_contract_version": contract,
        **contract_hashes,
        "workflow_contract_sha256": workflow_contract_sha,
        "source_sha256": semantic_source_sha,
        "body": body,
    }


def seal_packet(surface: str, *, body: dict[str, Any]) -> dict[str, Any]:
    """Seal a prepared body after runtime delta filtering."""

    return _seal_packet(_surface(surface), body=body)


def _market_report_mode(bundle: dict[str, Any]) -> str:
    quality = bundle.get("quality") or {}
    rows = bundle.get("strategy_table") or []
    ready = sum(bool((row.get("quality") or {}).get("execution_ready")) for row in rows if isinstance(row, dict))
    conditional = sum(bool((row.get("quality") or {}).get("conditional_strategy_ready")) for row in rows if isinstance(row, dict))
    if quality.get("decision_ready") is True:
        return "READY"
    if ready:
        return "MIXED"
    if quality.get("conditional_strategy_ready") is True:
        return "CONDITIONAL"
    if conditional:
        return "MIXED"
    return "OUTAGE" if rows else "RESEARCH"


def _session_id(surface: str, bundle: dict[str, Any]) -> str:
    values = [
        str(row.get("market_data_asof"))
        for row in (bundle.get("strategy_table") or [])
        if isinstance(row, dict) and row.get("market_data_asof")
    ]
    candidate = max(values) if values else str(bundle.get("generated_at") or "")
    parsed = _datetime(candidate)
    date = parsed.date().isoformat() if parsed else candidate[:10] or "unknown"
    return f"{surface.upper()}:{date}"


def _source_manifests(archive_dir: Path, filename: str) -> list[tuple[dict[str, Any], Path]]:
    manifests: list[tuple[dict[str, Any], Path]] = []
    root = Path(archive_dir) / "runs"
    if not root.exists():
        return manifests
    for path in root.rglob(filename):
        payload = load_json(path)
        if payload:
            manifests.append((payload, path.parent))
    manifests.sort(key=lambda pair: str(pair[0].get("started_at") or pair[0].get("run_id") or ""), reverse=True)
    return manifests


def _producer_snapshot(
    manifests: list[tuple[dict[str, Any], Path]],
    *,
    event_count: int,
    now: datetime,
    stale_after_hours: int,
) -> dict[str, Any]:
    if not manifests:
        return {
            "health": "MISSING",
            "run_id": None,
            "last_run_at": None,
            "status": None,
            "stale_after_hours": stale_after_hours,
        }
    latest = manifests[0][0]
    last_run_at = latest.get("finished_at") or latest.get("started_at")
    parsed = _datetime(last_run_at)
    stale = bool(
        parsed
        and now.astimezone(parsed.tzinfo) - parsed > timedelta(hours=max(1, int(stale_after_hours)))
    )
    status = str(latest.get("status") or "unknown").strip().lower()
    if status in {"failed", "failure", "error"}:
        health = "FAILED"
    elif stale:
        health = "STALE"
    elif event_count <= 0:
        health = "EMPTY"
    elif status in {"partial", "partial_failure", "degraded"}:
        health = "DEGRADED"
    else:
        health = "OK"
    return {
        "health": health,
        "run_id": latest.get("run_id"),
        "last_run_at": last_run_at,
        "status": latest.get("status"),
        "stale_after_hours": stale_after_hours,
    }


def _safe_artifact(run_dir: Path, value: Any) -> Path:
    if not value:
        return Path(run_dir) / "__missing__"
    path = Path(str(value))
    candidate = path if path.is_absolute() else Path(run_dir) / path
    try:
        candidate.resolve().relative_to(Path(run_dir).resolve())
    except (OSError, ValueError):
        return Path(run_dir) / "__blocked__"
    return candidate


def _datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.astimezone()


def _timestamp(value: Any) -> float | None:
    parsed = _datetime(value)
    return parsed.timestamp() if parsed else None


def _first_existing(*paths: Path) -> Path:
    for path in paths:
        if path.exists():
            return path
    return paths[0]


def _surface(value: str) -> str:
    key = str(value or "").strip().lower()
    if key not in SURFACES:
        raise ValueError(f"Unsupported Work surface: {value}")
    return key


def _truncate_value(value: Any, limit: int) -> Any:
    if isinstance(value, str):
        return value if len(value) <= limit else value[: max(0, limit - 3)].rstrip() + "..."
    if isinstance(value, list):
        return [_truncate_value(item, limit) for item in value[:5]]
    return value
