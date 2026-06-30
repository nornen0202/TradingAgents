from __future__ import annotations

import html
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import SiteSettings
from tradingagents.dataflows.intraday_market import DELAYED_ANALYSIS_ONLY, REALTIME_EXECUTION_READY, STALE_INVALID_FOR_EXECUTION
from tradingagents.presentation import (
    present_account_action,
    present_action_summary,
    present_data_status,
    present_decision_payload,
    present_investment_view,
    present_primary_condition,
    present_snapshot_mode,
    sanitize_investor_text,
)
from tradingagents.schemas import parse_structured_decision

try:
    from markdown_it import MarkdownIt
except ImportError:  # pragma: no cover
    MarkdownIt = None


_MARKDOWN = (
    MarkdownIt("commonmark", {"html": False, "linkify": True}).enable(["table", "strikethrough"])
    if MarkdownIt
    else None
)


def build_site(archive_dir: Path, site_dir: Path, settings: SiteSettings) -> list[dict[str, Any]]:
    archive_dir = Path(archive_dir)
    site_dir = Path(site_dir)
    manifests = _load_run_manifests(archive_dir)
    published_manifests = _select_published_manifests(manifests, settings)
    published_run_ids = {str(manifest.get("run_id") or "") for manifest in published_manifests}

    if site_dir.exists():
        shutil.rmtree(site_dir)
    (site_dir / "assets").mkdir(parents=True, exist_ok=True)
    _write_text(site_dir / "assets" / "style.css", _STYLE_CSS)

    for manifest in published_manifests:
        run_dir = Path(manifest["_run_dir"])
        portfolio_summary = _load_portfolio_summary(run_dir)
        _copy_artifacts(site_dir, run_dir, manifest, portfolio_summary)
        _write_text(
            site_dir / "runs" / manifest["run_id"] / "index.html",
            _render_run_page(manifest, settings, portfolio_summary=portfolio_summary, manifests=manifests),
        )
        if portfolio_summary.get("status_path"):
            _write_text(
                site_dir / "runs" / manifest["run_id"] / "portfolio.html",
                _render_portfolio_page(manifest, settings, portfolio_summary=portfolio_summary),
            )
            if _portfolio_has_etf_benchmark_page(portfolio_summary):
                _write_text(
                    site_dir / "runs" / manifest["run_id"] / "etf_benchmark.html",
                    _render_etf_benchmark_page(manifest, settings, portfolio_summary=portfolio_summary),
                )
        for ticker_summary in manifest.get("tickers", []):
            _write_text(
                site_dir / "runs" / manifest["run_id"] / f"{ticker_summary['ticker']}.html",
                _render_ticker_page(manifest, ticker_summary, settings, manifests=manifests, portfolio_summary=portfolio_summary),
            )

    _write_text(site_dir / "index.html", _render_index_page(manifests, settings, published_run_ids=published_run_ids))
    _write_json(
        site_dir / "feed.json",
        {
            "generated_at": datetime.now().isoformat(),
            "runs": [
                {
                    **{key: value for key, value in manifest.items() if key != "_run_dir"},
                    "published_to_site": str(manifest.get("run_id") or "") in published_run_ids,
                }
                for manifest in manifests
            ],
        },
    )
    _build_youtube_site_addon(archive_dir=archive_dir, site_dir=site_dir)
    _build_prism_telegram_site_addon(archive_dir=archive_dir, site_dir=site_dir)
    return manifests


def _load_run_manifests(archive_dir: Path) -> list[dict[str, Any]]:
    manifests: list[dict[str, Any]] = []
    runs_root = archive_dir / "runs"
    if not runs_root.exists():
        return manifests

    for path in runs_root.rglob("run.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["_run_dir"] = str(path.parent)
        manifests.append(payload)

    manifests.sort(key=lambda item: item.get("started_at", ""), reverse=True)
    return manifests


def _select_published_manifests(manifests: list[dict[str, Any]], settings: SiteSettings) -> list[dict[str, Any]]:
    if not manifests:
        return []

    configured_limit = int(getattr(settings, "max_published_runs", 120) or 0)
    if configured_limit <= 0:
        return list(manifests)

    homepage_limit = int(getattr(settings, "max_runs_on_homepage", 30) or 0)
    base_limit = max(configured_limit, homepage_limit, 1)
    selected: list[dict[str, Any]] = list(manifests[:base_limit])
    selected_ids = {str(manifest.get("run_id") or "") for manifest in selected}

    for manifest in (
        manifests[0],
        _select_representative_run(manifests),
        _select_latest_daily_run(manifests),
    ):
        if not manifest:
            continue
        run_id = str(manifest.get("run_id") or "")
        if run_id and run_id not in selected_ids:
            selected.append(manifest)
            selected_ids.add(run_id)

    return selected


def _copy_artifacts(
    site_dir: Path,
    run_dir: Path,
    manifest: dict[str, Any],
    portfolio_summary: dict[str, Any],
) -> None:
    for ticker_summary in manifest.get("tickers", []):
        download_dir = site_dir / "downloads" / manifest["run_id"] / ticker_summary["ticker"]
        download_dir.mkdir(parents=True, exist_ok=True)
        for relative_path in (ticker_summary.get("artifacts") or {}).values():
            if not relative_path:
                continue
            source = _resolve_artifact_source(run_dir, relative_path)
            if source.is_file():
                shutil.copy2(source, download_dir / source.name)

    execution_download_dir = site_dir / "downloads" / manifest["run_id"] / "execution"
    for artifact_path in ((manifest.get("execution") or {}).get("artifacts") or {}).values():
        if not artifact_path:
            continue
        source = _resolve_artifact_source(run_dir, artifact_path)
        if source.is_file():
            execution_download_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, execution_download_dir / source.name)

    download_dir = site_dir / "downloads" / manifest["run_id"] / "portfolio"
    copied_any = False
    for artifact_path in ((manifest.get("portfolio") or {}).get("artifacts") or {}).values():
        if not artifact_path:
            continue
        source = _resolve_artifact_source(run_dir, artifact_path)
        if _is_summary_image_artifact(source) and not _summary_image_publish_enabled(manifest):
            continue
        if not _should_publish_portfolio_artifact(source):
            continue
        if source.is_file():
            download_dir.mkdir(parents=True, exist_ok=True)
            _copy_public_portfolio_artifact(source, download_dir / source.name)
            copied_any = True

    if copied_any:
        delta_artifacts = ((manifest.get("portfolio_delta") or {}).get("artifacts") or {}).values()
        for artifact_path in delta_artifacts:
            if not artifact_path:
                continue
            source = _resolve_artifact_source(run_dir, artifact_path)
            if source.is_file():
                download_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, download_dir / source.name)
        for artifact_path in ((manifest.get("live_context_delta") or {}).get("artifacts") or {}).values():
            if not artifact_path:
                continue
            source = _resolve_artifact_source(run_dir, artifact_path)
            if source.is_file():
                download_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, download_dir / source.name)
        for artifact_path in ((manifest.get("performance") or {}).get("artifacts") or {}).values():
            if not artifact_path:
                continue
            source = _resolve_artifact_source(run_dir, artifact_path)
            if source.is_file():
                download_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, download_dir / source.name)
        return

    for source in portfolio_summary.get("downloadable_files", []):
        if not isinstance(source, Path) or not source.is_file():
            continue
        if _is_summary_image_artifact(source) and not _summary_image_publish_enabled(manifest):
            continue
        if not _should_publish_portfolio_artifact(source):
            continue
        download_dir.mkdir(parents=True, exist_ok=True)
        _copy_public_portfolio_artifact(source, download_dir / source.name)

    for artifact_path in ((manifest.get("portfolio_delta") or {}).get("artifacts") or {}).values():
        if not artifact_path:
            continue
        source = _resolve_artifact_source(run_dir, artifact_path)
        if source.is_file():
            download_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, download_dir / source.name)
    for artifact_path in ((manifest.get("live_context_delta") or {}).get("artifacts") or {}).values():
        if not artifact_path:
            continue
        source = _resolve_artifact_source(run_dir, artifact_path)
        if source.is_file():
            download_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, download_dir / source.name)
    for artifact_path in ((manifest.get("performance") or {}).get("artifacts") or {}).values():
        if not artifact_path:
            continue
        source = _resolve_artifact_source(run_dir, artifact_path)
        if source.is_file():
            download_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, download_dir / source.name)


def _resolve_artifact_source(run_dir: Path, path_value: Any) -> Path:
    candidate = Path(str(path_value))
    if candidate.is_absolute():
        return candidate
    return run_dir / candidate


def _copy_public_portfolio_artifact(source: Path, destination: Path) -> None:
    if source.suffix.lower() == ".json":
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
            if source.name == "account_performance_public.json":
                payload = _normalize_account_performance_payload(payload)
            sanitized = _sanitize_public_json(payload)
            destination.write_text(json.dumps(sanitized, indent=2, ensure_ascii=False), encoding="utf-8")
            return
        except Exception:
            pass
    shutil.copy2(source, destination)


def _should_publish_portfolio_artifact(source: Path) -> bool:
    if _is_summary_image_artifact(source):
        return True
    return _is_public_portfolio_download(source)


def _normalize_account_performance_payload(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    periods = value.get("periods")
    if not isinstance(periods, list):
        return value

    normalized = dict(value)
    normalized_periods: list[Any] = [dict(period) if isinstance(period, dict) else period for period in periods]
    converted_warnings: list[str] = []
    all_period = _account_performance_all_period(normalized_periods)
    if all_period:
        all_start = _account_performance_date_text(all_period.get("start_date"))
        all_end = _account_performance_date_text(all_period.get("end_date"))
        for index, period in enumerate(normalized_periods):
            if not isinstance(period, dict):
                continue
            if not _is_legacy_account_performance_history_gap(period, all_start=all_start, all_end=all_end):
                continue
            normalized_periods[index], warning = _mark_account_performance_history_gap(period)
            converted_warnings.append(warning)

    normalized["periods"] = normalized_periods
    if converted_warnings:
        quality = dict(normalized.get("data_quality")) if isinstance(normalized.get("data_quality"), dict) else {}
        warnings = list(quality.get("warnings")) if isinstance(quality.get("warnings"), list) else []
        existing_warnings = {str(item) for item in warnings}
        for warning in converted_warnings:
            if warning not in existing_warnings:
                warnings.append(warning)
                existing_warnings.add(warning)
        quality["warnings"] = warnings
        normalized["data_quality"] = quality

    summary = normalized.get("summary") if isinstance(normalized.get("summary"), dict) else {}
    default_period = _account_performance_default_period(normalized_periods)
    if default_period and (
        converted_warnings
        or not _account_performance_summary_is_usable(summary, normalized_periods)
        or "default_period_label" not in summary
        or "primary_return_method" not in summary
    ):
        normalized["summary"] = _account_performance_summary_from_period(default_period, previous=summary)
    normalized["profit_calendar"] = _normalize_profit_calendar_payload(normalized.get("profit_calendar"))
    return normalized


def _normalize_profit_calendar_payload(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    normalized = dict(value)
    for key in ("weekly", "monthly", "rolling"):
        rows = normalized.get(key)
        if isinstance(rows, list):
            normalized[key] = [_normalize_profit_calendar_bucket(row) for row in rows]
    summary = normalized.get("summary")
    if isinstance(summary, dict):
        normalized["summary"] = {
            key: _normalize_profit_calendar_bucket(item) if isinstance(item, dict) else item
            for key, item in summary.items()
        }
    return normalized


def _normalize_profit_calendar_bucket(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    bucket = dict(value)
    source = str(bucket.get("source") or "")
    trust_state = str(bucket.get("trust_state") or "")
    warnings = [str(item) for item in bucket.get("warnings", [])] if isinstance(bucket.get("warnings"), list) else []
    unreconciled_internal = (
        source == "internal_snapshot"
        and (
            trust_state == "unreconciled_reference"
            or bucket.get("display_eligible") is False
            or "snapshot_reconciliation_failed" in warnings
        )
    )
    if unreconciled_internal:
        if "reference_investment_pnl_krw" not in bucket:
            bucket["reference_investment_pnl_krw"] = bucket.get("investment_pnl_krw")
        if "reference_return_pct" not in bucket:
            bucket["reference_return_pct"] = bucket.get("return_pct")
        bucket["profit_krw"] = None
        bucket["profit_basis"] = "internal_snapshot"
        bucket["investment_pnl_krw"] = None
        bucket["return_pct"] = None
        bucket["display_eligible"] = False
        return bucket
    if "profit_krw" not in bucket and bucket.get("investment_pnl_krw") is not None:
        bucket["profit_krw"] = bucket.get("investment_pnl_krw")
        bucket.setdefault("profit_basis", "investment_pnl" if source == "broker_reported" else source or "internal_snapshot")
    return bucket


def _account_performance_all_period(periods: list[Any]) -> dict[str, Any] | None:
    for period in periods:
        if not isinstance(period, dict):
            continue
        if str(period.get("period") or "").upper() != "ALL":
            continue
        if _account_performance_number(period.get("actual_return")) is not None:
            return period
    return None


def _is_legacy_account_performance_history_gap(period: dict[str, Any], *, all_start: str, all_end: str) -> bool:
    if str(period.get("period") or "").upper() == "ALL":
        return False
    if period.get("status") == "insufficient_history":
        return False
    if not period.get("partial"):
        return False
    if _account_performance_number(period.get("actual_return")) is None:
        return False

    requested = _account_performance_date_text(period.get("requested_start_date"))
    start = _account_performance_date_text(period.get("start_date"))
    end = _account_performance_date_text(period.get("end_date"))
    if not requested or not start or not _account_performance_date_before(requested, start):
        return False
    if start != all_start:
        return False
    if all_end and end and end != all_end:
        return False
    return True


def _mark_account_performance_history_gap(period: dict[str, Any]) -> tuple[dict[str, Any], str]:
    normalized = dict(period)
    period_name = str(normalized.get("period") or "-")
    requested = _account_performance_date_text(normalized.get("requested_start_date")) or str(
        normalized.get("requested_start_date") or "-"
    )
    available = _account_performance_date_text(normalized.get("start_date")) or str(normalized.get("start_date") or "-")
    reason = f"requested_start={requested}:available_start={available}"
    partial_reasons = (
        list(normalized.get("partial_reasons")) if isinstance(normalized.get("partial_reasons"), list) else []
    )
    if reason not in {str(item) for item in partial_reasons}:
        partial_reasons.append(reason)
    coverage = dict(normalized.get("period_coverage")) if isinstance(normalized.get("period_coverage"), dict) else {}
    coverage.update(
        {
            "period": period_name,
            "requested_start_date": requested,
            "actual_start_date": available,
            "end_date": _account_performance_date_text(normalized.get("end_date")) or normalized.get("end_date"),
            "is_partial": True,
            "same_actual_window_as": "ALL_AVAILABLE",
            "is_summary_eligible": False,
            "insufficient_reason": "account history starts after requested period start",
        }
    )
    normalized.update(
        {
            "status": "insufficient_history",
            "partial": True,
            "partial_reasons": partial_reasons,
            "actual_start_value_krw": None,
            "actual_end_value_krw": None,
            "simple_nav_return": None,
            "twr_return": None,
            "mwr_return": None,
            "primary_return": None,
            "primary_return_method": "insufficient_history",
            "return_method_warning": "insufficient_history",
            "actual_return": None,
            "mdd": None,
            "volatility": None,
            "period_coverage": coverage,
            "simple_benchmarks": [],
            "cashflow_benchmarks": [],
            "best_excess": {},
            "worst_excess": {},
        }
    )
    warning = f"account_performance_period_insufficient_history:{period_name}:{reason}"
    return normalized, warning


def _account_performance_summary_is_usable(summary: dict[str, Any], periods: list[Any]) -> bool:
    summary_period = str(summary.get("default_period") or "")
    source_period = str(summary.get("source_period") or "")
    if not summary_period:
        return False
    for period in periods:
        if not isinstance(period, dict):
            continue
        period_name = str(period.get("period") or "")
        period_label = _account_performance_period_summary_label(period)
        if period_name not in {summary_period, source_period} and period_label != summary_period:
            continue
        if period.get("status") == "insufficient_history":
            return False
        return _account_performance_number(period.get("actual_return")) is not None
    return False


def _account_performance_default_period(periods: list[Any]) -> dict[str, Any] | None:
    dict_periods = [period for period in periods if isinstance(period, dict)]
    eligible = [
        period
        for period in dict_periods
        if _account_performance_number(period.get("actual_return")) is not None
        and _account_period_summary_eligible(period)
        and not period.get("same_actual_window_as")
    ]
    non_all = [period for period in eligible if str(period.get("period") or "").upper() != "ALL"]
    if non_all:
        return max(non_all, key=lambda item: _account_period_requested_days(item))
    for period in dict_periods:
        if str(period.get("period") or "").upper() == "ALL" and _account_performance_number(period.get("actual_return")) is not None:
            return period
    for period in dict_periods:
        if _account_performance_number(period.get("actual_return")) is not None:
            return period
    return dict_periods[-1] if dict_periods else None


def _account_performance_summary_from_period(period: dict[str, Any], *, previous: dict[str, Any]) -> dict[str, Any]:
    summary = dict(previous)
    best = period.get("best_excess") if isinstance(period.get("best_excess"), dict) else {}
    worst = period.get("worst_excess") if isinstance(period.get("worst_excess"), dict) else {}
    summary.update(
        {
            "default_period": _account_performance_period_summary_label(period),
            "source_period": period.get("period"),
            "default_period_label": _account_period_display_label(period),
            "requested_start_date": period.get("requested_start_date"),
            "start_date": period.get("start_date"),
            "end_date": period.get("end_date"),
            "partial": bool(period.get("partial")),
            "simple_nav_return": period.get("simple_nav_return", period.get("actual_return")),
            "twr_return": period.get("twr_return"),
            "mwr_return": period.get("mwr_return"),
            "primary_return": period.get("primary_return", period.get("actual_return")),
            "primary_return_method": period.get("primary_return_method") or (
                "available_history_simple_nav" if str(period.get("period") or "").upper() == "ALL" else "simple_nav"
            ),
            "return_method_warning": period.get("return_method_warning"),
            "actual_return": period.get("actual_return"),
            "period_coverage": period.get("period_coverage") if isinstance(period.get("period_coverage"), dict) else {},
            "best_excess": best,
            "worst_excess": worst,
        }
    )
    return summary


def _account_period_summary_eligible(period: dict[str, Any]) -> bool:
    coverage = period.get("period_coverage")
    if isinstance(coverage, dict) and "is_summary_eligible" in coverage:
        return bool(coverage.get("is_summary_eligible"))
    return period.get("status") not in {"insufficient_history", "duplicate_actual_window"}


def _account_period_requested_days(period: dict[str, Any]) -> int:
    coverage = period.get("period_coverage")
    if isinstance(coverage, dict):
        try:
            return int(float(coverage.get("requested_days") or 0))
        except (TypeError, ValueError):
            return 0
    return 0


def _account_performance_period_summary_label(period: dict[str, Any]) -> str:
    return "ALL_AVAILABLE" if str(period.get("period") or "").upper() == "ALL" else str(period.get("period") or "-")


def _account_period_display_label(period: dict[str, Any]) -> str:
    return "사용 가능 전체 기간" if str(period.get("period") or "").upper() == "ALL" else str(period.get("period") or "-")


def _account_performance_number(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _account_performance_date_text(value: Any) -> str:
    text = str(value or "").strip()[:10]
    return text if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text) else ""


def _account_performance_date_before(left: str, right: str) -> bool:
    try:
        return datetime.strptime(left, "%Y-%m-%d").date() < datetime.strptime(right, "%Y-%m-%d").date()
    except ValueError:
        return False


def _sanitize_public_json(value: Any) -> Any:
    sensitive_keys = {
        "account_id",
        "account_no",
        "broker_account_id",
        "broker_order_id",
        "order_id",
        "odno",
        "cano",
        "acnt_prdt_cd",
        "snapshot_id",
        "kis_order_id",
        "ord_gno_brno",
        "ord_no",
    }
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if key_text.lower() in sensitive_keys:
                sanitized[key_text] = _mask_identifier(item)
            else:
                sanitized[key_text] = _sanitize_public_json(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_public_json(item) for item in value]
    if isinstance(value, str):
        return _mask_sensitive_text(value)
    return value


def _mask_identifier(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return "***MASKED***"


def _mask_sensitive_text(value: str) -> str:
    text = str(value)
    text = re.sub(r"\b\d{8}-\d{2}\b", "***MASKED***", text)
    text = re.sub(r"\bkis_\d{8}-\d{2}\b", "kis_***MASKED***", text)
    text = re.sub(r"(CANO=)[^&\s]+", r"\1***MASKED***", text)
    text = re.sub(r"(ACNT_PRDT_CD=)[^&\s]+", r"\1***MASKED***", text)
    return text


def _render_index_page(
    manifests: list[dict[str, Any]],
    settings: SiteSettings,
    *,
    published_run_ids: set[str] | None = None,
) -> str:
    latest = manifests[0] if manifests else None
    representative = _select_representative_run(manifests)
    latest_portfolio = _load_portfolio_summary(Path(representative["_run_dir"])) if representative else {}
    latest_health_badges = ""
    latest_health_compact = _render_health_compact_card(manifest=representative, portfolio_summary=latest_portfolio) if representative else ""
    representative_badge = ""
    if representative and _run_phase_label(representative) in {"delayed_analysis_only", "post_close"}:
        representative_badge = "<div class='warning-banner'>Not for live execution</div>"
    latest_portfolio_label = _portfolio_report_label(latest_portfolio)
    latest_portfolio_link = (
        f"<a class=\"button\" href=\"runs/{_escape(representative['run_id'])}/portfolio.html\">Open {_escape(latest_portfolio_label.lower())}</a>"
        if representative and latest_portfolio.get("status_path")
        else ""
    )
    latest_technical_html = ""
    latest_technical_run = latest if latest and representative and latest["run_id"] != representative["run_id"] else None
    latest_daily_run = _select_latest_daily_run(manifests)
    if latest and representative and latest["run_id"] != representative["run_id"]:
        latest_technical_html = (
            "<p class='empty'>"
            f"가장 최근 기술 run: "
            f"<a href='runs/{_escape(latest['run_id'])}/index.html'>{_escape(latest['run_id'])}</a>"
            f" ({_escape(_run_phase_display_label(latest))})"
            "</p>"
        )
    if latest_technical_run:
        latest_technical_html = (
            "<p class='empty'>"
            f"가장 최근 기술 run / Latest technical run: "
            f"<a href='runs/{_escape(latest_technical_run['run_id'])}/index.html'>"
            f"{_escape(latest_technical_run['run_id'])}</a>"
            f" ({_escape(_run_phase_display_label(latest_technical_run))})"
            "</p>"
        )
    latest_daily_html = ""
    if latest_daily_run and representative and latest_daily_run.get("run_id") != representative.get("run_id"):
        latest_daily_html = (
            "<p class='empty'>"
            f"가장 최근 daily 분석 / Latest daily analysis: "
            f"<a href='runs/{_escape(latest_daily_run['run_id'])}/index.html'>"
            f"{_escape(latest_daily_run['run_id'])}</a>"
            f" ({_escape(_run_phase_display_label(latest_daily_run))})"
            "</p>"
        )
    latest_html = (
        f"""
        <section class="hero">
          <div>
            <p class="eyebrow">대표 투자 run</p>
            <h1>{_escape(settings.title)}</h1>
            <p class="subtitle">{_escape(settings.subtitle)}</p>
          </div>
          <div class="hero-card">
            <div class="status {representative['status']}">{_escape(representative['status'].replace('_', ' '))}</div>
            <p><strong>Run ID</strong><span>{_escape(representative['run_id'])}</span></p>
            <p><strong>Started</strong><span>{_escape(representative['started_at'])}</span></p>
            <p><strong>세션 단계</strong><span>{_escape(_run_phase_display_label(representative))}</span></p>
            <p><strong>Tickers</strong><span>{representative['summary']['total_tickers']}</span></p>
            <p><strong>Success</strong><span>{representative['summary']['successful_tickers']}</span></p>
            <p><strong>Failed</strong><span>{representative['summary']['failed_tickers']}</span></p>
            {representative_badge}
            {latest_health_badges}
            {latest_health_compact}
            <a class="button" href="runs/{_escape(representative['run_id'])}/index.html">Open 대표 투자 run</a>
            <a class="button" href="runs/{_escape(representative['run_id'])}/index.html">Open representative investment run</a>
            <a class="button" href="youtube/index.html">Open YouTube 검증 리포트</a>
            <a class="button" href="prism-telegram/index.html">Open PRISM Telegram 리포트</a>
            {latest_portfolio_link}
            {latest_daily_html}
            {latest_technical_html}
          </div>
        </section>
        """
        if representative
        else f"""
        <section class="hero">
          <div>
            <p class="eyebrow">Waiting for first run</p>
            <h1>{_escape(settings.title)}</h1>
            <p class="subtitle">{_escape(settings.subtitle)}</p>
          </div>
          <div class="hero-card">
            <div class="status pending">no data yet</div>
            <p>The scheduled workflow has not produced an archived run yet.</p>
            <a class="button" href="youtube/index.html">Open YouTube 검증 리포트</a>
            <a class="button" href="prism-telegram/index.html">Open PRISM Telegram 리포트</a>
          </div>
        </section>
        """
    )

    cards = []
    for manifest in manifests[: settings.max_runs_on_homepage]:
        portfolio_summary = _load_portfolio_summary(Path(manifest["_run_dir"]))
        portfolio_label = _portfolio_report_label(portfolio_summary)
        portfolio_link = (
            f"<p><a href=\"runs/{_escape(manifest['run_id'])}/portfolio.html\">{_escape(portfolio_label)}</a></p>"
            if portfolio_summary.get("status_path")
            else ""
        )
        sell_side_counts = portfolio_summary.get("sell_side_counts") if isinstance(portfolio_summary.get("sell_side_counts"), dict) else {}
        sell_side_line = (
            f"<p>이익실현 {int(sell_side_counts.get('TAKE_PROFIT') or 0)} / "
            f"리스크 축소 {int(sell_side_counts.get('REDUCE_RISK') or 0)} / "
            f"손절·청산 {int(sell_side_counts.get('STOP_LOSS') or 0) + int(sell_side_counts.get('EXIT') or 0)}</p>"
            if sell_side_counts
            else ""
        )
        cards.append(
            f"""
            <article class="run-card">
              <div class="run-card-header">
                <a href="runs/{_escape(manifest['run_id'])}/index.html">{_escape(manifest['run_id'])}</a>
                <span class="status {manifest['status']}">{_escape(manifest['status'].replace('_', ' '))}</span>
              </div>
              <p>{_escape(manifest['started_at'])}</p>
              <p>{manifest['summary']['successful_tickers']} succeeded, {manifest['summary']['failed_tickers']} failed</p>
              <p>{_escape(manifest['settings'].get('output_language', '-'))} report</p>
              <p>{_escape(_run_category(manifest))}</p>
              {sell_side_line}
              {portfolio_link}
            </article>
            """
        )

    warning_html = ""
    if representative and representative.get("warnings"):
        warning_html = "".join(
            f"<div class='warning-banner'>{_escape(warning)}</div>" for warning in representative.get("warnings", [])
        )

    archive_count_label = f"{len(manifests)} archived run(s)"
    if published_run_ids is not None and len(published_run_ids) < len(manifests):
        archive_count_label = f"{archive_count_label} / {len(published_run_ids)} published on Pages"

    body = latest_html + warning_html + f"""
    <section class="section">
      <div class="section-head">
        <h2>Recent runs</h2>
        <p>{_escape(archive_count_label)}</p>
      </div>
      <div class="run-grid">
        {''.join(cards) if cards else '<p class="empty">No archived runs were found.</p>'}
      </div>
    </section>
    """
    return _page_template(settings.title, body, prefix="")


def _build_youtube_site_addon(*, archive_dir: Path, site_dir: Path) -> None:
    try:
        from tradingagents.youtube.config import load_youtube_config
        from tradingagents.youtube.site import build_youtube_site

        youtube_config = load_youtube_config()
        youtube_archive_dir = youtube_config.storage.archive_dir
        shared_youtube_archive = Path(archive_dir) / "youtube-archive"
        if (
            not os.getenv("TRADINGAGENTS_YOUTUBE_ARCHIVE_DIR", "").strip()
            and (shared_youtube_archive.exists() or _is_default_runtime_youtube_archive(youtube_archive_dir))
        ):
            youtube_archive_dir = shared_youtube_archive
        build_youtube_site(youtube_archive_dir, site_dir, youtube_config.site)
    except Exception as exc:  # pragma: no cover - defensive in Pages jobs
        print(f"::warning::Could not build YouTube report site add-on: {exc}")


def _build_prism_telegram_site_addon(*, archive_dir: Path, site_dir: Path) -> None:
    try:
        from tradingagents.prism_telegram.config import load_prism_telegram_config
        from tradingagents.prism_telegram.site import build_prism_telegram_site

        prism_telegram_config = load_prism_telegram_config()
        prism_telegram_archive_dir = prism_telegram_config.storage.archive_dir
        shared_archive = Path(archive_dir) / "prism-telegram-archive"
        if (
            not os.getenv("TRADINGAGENTS_PRISM_TELEGRAM_ARCHIVE_DIR", "").strip()
            and (shared_archive.exists() or _is_default_runtime_prism_telegram_archive(prism_telegram_archive_dir))
        ):
            prism_telegram_archive_dir = shared_archive
        build_prism_telegram_site(prism_telegram_archive_dir, site_dir, prism_telegram_config.site)
    except Exception as exc:  # pragma: no cover - defensive in Pages jobs
        print(f"::warning::Could not build PRISM Telegram report site add-on: {exc}")


def _is_default_runtime_prism_telegram_archive(path: Path) -> bool:
    normalized = str(path).replace("\\", "/").rstrip("/")
    return normalized.endswith(".runtime/prism-telegram-archive")


def _is_default_runtime_youtube_archive(path: Path) -> bool:
    normalized = str(path).replace("\\", "/").rstrip("/")
    return normalized.endswith(".runtime/youtube-archive")


def _render_run_page(
    manifest: dict[str, Any],
    settings: SiteSettings,
    *,
    portfolio_summary: dict[str, Any] | None = None,
    manifests: list[dict[str, Any]] | None = None,
) -> str:
    portfolio_summary = portfolio_summary or {}
    portfolio_status = manifest.get("portfolio") or {}
    portfolio_status_value = str(
        portfolio_status.get("status") or portfolio_summary.get("status") or "unknown"
    ).strip()
    portfolio_status_class = _status_class(portfolio_status_value)
    portfolio_status_label = _portfolio_status_label(portfolio_status_value)
    portfolio_profile = portfolio_status.get("profile") or portfolio_summary.get("profile") or "-"
    portfolio_label = _portfolio_report_label(portfolio_summary)
    language = _manifest_language(manifest)
    stale_after_seconds = _execution_stale_threshold_seconds(manifest)

    portfolio_links: list[str] = []
    for artifact_path in (portfolio_status.get("artifacts") or {}).values():
        if not artifact_path:
            continue
        artifact_name = Path(str(artifact_path)).name
        artifact = Path(artifact_name)
        if _is_summary_image_artifact(artifact) and not _summary_image_publish_enabled(manifest):
            continue
        if not _should_publish_portfolio_artifact(artifact):
            continue
        portfolio_links.append(
            f"<a class='pill' href='../../downloads/{_escape(manifest['run_id'])}/portfolio/{_escape(artifact_name)}'>{_escape(artifact_name)}</a>"
        )
    if not portfolio_links:
        for source in portfolio_summary.get("downloadable_files", []):
            if not isinstance(source, Path):
                continue
            if _is_summary_image_artifact(source) and not _summary_image_publish_enabled(manifest):
                continue
            if not _should_publish_portfolio_artifact(source):
                continue
            portfolio_links.append(
                f"<a class='pill' href='../../downloads/{_escape(manifest['run_id'])}/portfolio/{_escape(source.name)}'>{_escape(source.name)}</a>"
            )

    execution_links: list[str] = []
    for artifact_path in ((manifest.get("execution") or {}).get("artifacts") or {}).values():
        if not artifact_path:
            continue
        artifact_name = Path(str(artifact_path)).name
        execution_links.append(
            f"<a class='pill' href='../../downloads/{_escape(manifest['run_id'])}/execution/{_escape(artifact_name)}'>{_escape(artifact_name)}</a>"
        )

    ticker_cards = []
    for ticker_summary in manifest.get("tickers", []):
        display_summary = _with_portfolio_action(ticker_summary, portfolio_summary)
        investor_summary = _ticker_investor_summary(
            display_summary,
            manifest,
            language=language,
            stale_after_seconds=stale_after_seconds,
        )
        ticker_cards.append(
            f"""
            <article class="ticker-card">
              <div class="ticker-card-header">
                <a href="{_escape(ticker_summary['ticker'])}.html">{_escape(ticker_summary['ticker'])}</a>
                <span class="status {ticker_summary['status']}">{_escape(ticker_summary['status'])}</span>
              </div>
              <p><strong>종목명</strong><span>{_escape(_ticker_display_label(ticker_summary))}</span></p>
              <p><strong>{_escape(investor_summary['investment_view_label'])}</strong><span>{_escape(investor_summary['investment_view'])}</span></p>
              <p><strong>중기 리서치 관점</strong><span>{_escape(investor_summary['research_view'])}</span></p>
              <p><strong>오늘 할 일</strong><span>{_escape(investor_summary['today_action'])}</span></p>
              <p><strong>장중 pilot 조건</strong><span>{_escape(investor_summary['intraday_pilot_action'])}</span></p>
              <p><strong>종가 확인 시 할 일</strong><span>{_escape(investor_summary['close_action'])}</span></p>
              <p><strong>내일 follow-through</strong><span>{_escape(investor_summary['next_day_action'])}</span></p>
              <p class="long-field"><strong>핵심 가격대</strong><span>{_escape(investor_summary['key_levels'])}</span></p>
              <p class="long-field"><strong>위험 요약</strong><span>{_escape(investor_summary['risk_summary'])}</span></p>
              <p><strong>리서치 기준</strong><span>{_escape(investor_summary['research_basis'])}</span></p>
              <p><strong>실행 기준</strong><span>{_escape(investor_summary['execution_basis'])}</span></p>
              {_advanced_diagnostics_html(ticker_summary, manifest, stale_after_seconds=stale_after_seconds, compact=True)}
            </article>
            """
        )

    portfolio_html = ""
    if portfolio_status or portfolio_summary:
        rendered_links = []
        if portfolio_summary.get("status_path"):
            rendered_links.append("<a class='pill' href='portfolio.html'>portfolio.html</a>")
        if _portfolio_has_etf_benchmark_page(portfolio_summary):
            rendered_links.append("<a class='pill' href='etf_benchmark.html'>etf_benchmark.html</a>")
        rendered_page = (
            "".join(rendered_links)
            if rendered_links
            else f"<span class='empty'>No published {_escape(portfolio_label.lower())}</span>"
        )
        portfolio_html = f"""
    <section class="section">
      <div class="section-head">
        <h2>{_escape(portfolio_label)}</h2>
      </div>
      <article class="run-card">
        <div class="run-card-header">
          <span>Status</span>
          <span class="status {portfolio_status_class}">{_escape(portfolio_status_label)}</span>
        </div>
        <p><strong>Profile</strong><span>{_escape(str(portfolio_profile))}</span></p>
        <p><strong>Report page</strong><span>{rendered_page}</span></p>
        <div class="pill-row">
          {''.join(portfolio_links) if portfolio_links else "<span class='empty'>No downloads</span>"}
        </div>
      </article>
    </section>
        """

    execution_html = ""
    execution_status = manifest.get("execution") or {}
    if execution_links:
        overlay_phase = execution_status.get("overlay_phase") if isinstance(execution_status.get("overlay_phase"), dict) else {}
        selected = overlay_phase.get("selected_checkpoints") or []
        checkpoint_notice = ""
        if not selected:
            checkpoint_notice = (
                "<p><strong>상태</strong><span>이번 run에서는 장중 체크포인트가 선택되지 않아 "
                "microstructure 파일이 새로 생성되지 않았습니다. 링크는 최신 보존/참고 컨텍스트입니다.</span></p>"
            )
        execution_html = f"""
    <section class="section">
      <div class="section-head">
        <h2>장중 실행 컨텍스트</h2>
      </div>
      <article class="run-card">
        <p><strong>용도</strong><span>ChatGPT가 기준시각별 현재가, VWAP, RVOL, 호가/체결강도, 수급 상태를 읽는 공개 실행 컨텍스트</span></p>
        {checkpoint_notice}
        <div class="pill-row">{''.join(execution_links)}</div>
      </article>
    </section>
        """
    elif execution_status:
        overlay_phase = execution_status.get("overlay_phase") if isinstance(execution_status.get("overlay_phase"), dict) else {}
        selected = overlay_phase.get("selected_checkpoints") or []
        notes = execution_status.get("notes") or []
        note_text = " / ".join(str(item) for item in notes if str(item).strip())
        if not note_text:
            note_text = "No execution checkpoint was refreshed in this run."
        if not selected:
            execution_html = f"""
    <section class="section">
      <div class="section-head">
        <h2>장중 실행 컨텍스트</h2>
      </div>
      <article class="run-card">
        <p><strong>상태</strong><span>이번 run에서는 장중 체크포인트가 선택되지 않아 microstructure 파일이 새로 생성되지 않았습니다.</span></p>
        <p class="long-field"><strong>메모</strong><span>{_escape(note_text)}</span></p>
      </article>
    </section>
            """

    warning_html = "".join(
        f"<div class='warning-banner'>{_escape(warning)}</div>"
        for warning in (manifest.get("warnings") or [])
    )
    delta_html = _render_portfolio_delta_section(manifest)
    live_delta_html = _render_live_context_delta_section(manifest)
    timeline_html = _render_session_timeline_section(manifest, manifests or [])
    body = f"""
    <nav class="breadcrumbs"><a href="../../index.html">Home</a></nav>
    <section class="hero compact">
      <div>
        <p class="eyebrow">Run detail</p>
        <h1>{_escape(manifest['run_id'])}</h1>
        <p class="subtitle">{_escape(manifest['started_at'])}</p>
      </div>
      <div class="hero-card">
        <div class="status {manifest['status']}">{_escape(manifest['status'].replace('_', ' '))}</div>
        <p><strong>Started</strong><span>{_escape(manifest['started_at'])}</span></p>
        <p><strong>Report language</strong><span>{_escape(manifest['settings'].get('output_language', '-'))}</span></p>
        <p><strong>Tickers</strong><span>{manifest['summary']['successful_tickers']} success / {manifest['summary']['failed_tickers']} failed</span></p>
      </div>
    </section>
    {warning_html}
    {delta_html}
    {timeline_html}
    {execution_html}
    {portfolio_html}
    <section class="section">
      <div class="section-head">
        <h2>Tickers</h2>
        <p>{manifest['summary']['successful_tickers']} success / {manifest['summary']['failed_tickers']} failed</p>
      </div>
      {_render_run_health_section(manifest, portfolio_summary)}
      <div class="ticker-grid">
        {''.join(ticker_cards)}
      </div>
    </section>
    {live_delta_html}
    """
    return _page_template(f"{manifest['run_id']} | {settings.title}", body, prefix="../../")


def _render_portfolio_delta_section(manifest: dict[str, Any]) -> str:
    delta = manifest.get("portfolio_delta") or {}
    if not delta:
        return ""
    artifacts = delta.get("artifacts") or {}
    json_name = Path(str(artifacts.get("portfolio_delta_json") or "portfolio_delta.json")).name
    md_name = Path(str(artifacts.get("portfolio_delta_markdown") or "portfolio_delta.md")).name
    summary = str(delta.get("summary") or "직전 run 대비 요약 없음")
    from_run = str(delta.get("from_run") or "-")
    return f"""
    <section class="section">
      <div class="section-head">
        <h2>직전 overlay 대비 변화</h2>
      </div>
      <article class="run-card">
        <p><strong>비교 run</strong><span>{_escape(from_run)}</span></p>
        <p class="long-field"><strong>요약</strong><span>{_escape(summary)}</span></p>
        <div class="pill-row">
          <a class="pill" href="../../downloads/{_escape(manifest['run_id'])}/portfolio/{_escape(json_name)}">{_escape(json_name)}</a>
          <a class="pill" href="../../downloads/{_escape(manifest['run_id'])}/portfolio/{_escape(md_name)}">{_escape(md_name)}</a>
        </div>
      </article>
    </section>
    """


def _render_live_context_delta_section(manifest: dict[str, Any]) -> str:
    delta = manifest.get("live_context_delta") or {}
    if not delta:
        return ""

    artifacts = delta.get("artifacts") or {}
    json_name = Path(str(artifacts.get("live_context_delta_json") or "live_context_delta.json")).name
    md_name = Path(str(artifacts.get("report_vs_live_delta_markdown") or "report_vs_live_delta.md")).name
    changed = [
        str(item.get("ticker") or "")
        for item in (delta.get("ticker_deltas") or [])
        if str(item.get("base_action") or "").upper() != str(item.get("live_action") or "").upper()
    ]
    reasons: list[str] = []
    for item in (delta.get("ticker_deltas") or []):
        for code in item.get("reason_codes") or []:
            normalized = str(code).strip().upper()
            if normalized and normalized not in reasons:
                reasons.append(normalized)
    return f"""
    <section class="section">
      <div class="section-head">
        <h2>Report vs latest intraday reanalysis</h2>
      </div>
      <article class="run-card">
        <p><strong>Base thesis</strong><span>{_escape(str(manifest.get('daily_thesis_trade_date') or manifest.get('run_id') or '-'))}</span></p>
        <p><strong>Live context as of</strong><span>{_escape(str(delta.get('as_of') or '-'))}</span></p>
        <p class="long-field"><strong>Changed tickers</strong><span>{_escape(', '.join(changed) if changed else 'None')}</span></p>
        <p class="long-field"><strong>Why it changed</strong><span>{_escape(', '.join(reasons[:6]) if reasons else 'live price and volume did not materially change the thesis')}</span></p>
        <div class="pill-row">
          <a class="pill" href="../../downloads/{_escape(manifest['run_id'])}/portfolio/{_escape(json_name)}">{_escape(json_name)}</a>
          <a class="pill" href="../../downloads/{_escape(manifest['run_id'])}/portfolio/{_escape(md_name)}">{_escape(md_name)}</a>
        </div>
      </article>
    </section>
    """


def _render_session_timeline_section(manifest: dict[str, Any], manifests: list[dict[str, Any]]) -> str:
    items = _session_timeline_items(manifest, manifests)
    if not items:
        return ""
    rows = "".join(
        "<li>"
        f"<a href='index.html'>{_escape(item['run_id'])}</a>" if item["run_id"] == manifest["run_id"] else f"<a href='../{_escape(item['run_id'])}/index.html'>{_escape(item['run_id'])}</a>"
        + f" · {_escape(item['started_at'])} · {_escape(item['phase'])}"
        + (" <strong>(current)</strong>" if item["run_id"] == manifest["run_id"] else "")
        + "</li>"
        for item in items
    )
    return (
        "<section class='section'>"
        "<div class='section-head'><h2>동일 세션 timeline</h2></div>"
        f"<article class='run-card'><ul>{rows}</ul></article>"
        "</section>"
    )


def _session_timeline_items(manifest: dict[str, Any], manifests: list[dict[str, Any]]) -> list[dict[str, str]]:
    current_market = str(((manifest.get("settings") or {}).get("market") or "")).strip().lower()
    current_date = str(manifest.get("run_id") or "")[:8]
    matched: list[dict[str, str]] = []
    for item in manifests:
        run_id = str(item.get("run_id") or "")
        if not run_id.startswith(current_date):
            continue
        market = str(((item.get("settings") or {}).get("market") or "")).strip().lower()
        if current_market and market and current_market != market:
            continue
        matched.append(
            {
                "run_id": run_id,
                "started_at": str(item.get("started_at") or "-"),
                "phase": _run_phase_label(item),
            }
        )
    matched.sort(key=lambda row: row["started_at"])
    return matched


def _render_live_ticker_context_delta_section(
    *,
    manifest: dict[str, Any],
    ticker_summary: dict[str, Any],
) -> str:
    delta = manifest.get("live_context_delta") or {}
    ticker = str(ticker_summary.get("ticker") or "").strip().upper()
    ticker_delta = next(
        (
            item
            for item in (delta.get("ticker_deltas") or [])
            if str(item.get("ticker") or "").strip().upper() == ticker
        ),
        None,
    )
    if not ticker_delta:
        if delta:
            return ""
        return ""
    return f"""
    <section class="section">
      <div class="section-head">
        <h2>Latest intraday reanalysis</h2>
      </div>
      <article class="run-card">
        <p><strong>Base action</strong><span>{_escape(str(ticker_delta.get('base_action') or '-'))}</span></p>
        <p><strong>Live action</strong><span>{_escape(str(ticker_delta.get('live_action') or '-'))}</span></p>
        <p class="long-field"><strong>Reason codes</strong><span>{_escape(', '.join(ticker_delta.get('reason_codes') or []) or '-')}</span></p>
      </article>
    </section>
    """


def _render_ticker_delta_section(
    *,
    manifest: dict[str, Any],
    ticker_summary: dict[str, Any],
    manifests: list[dict[str, Any]],
    language: str,
) -> str:
    previous = _previous_comparable_run(manifest, manifests)
    if not previous:
        return ""
    ticker = str(ticker_summary.get("ticker") or "").strip().upper()
    previous_ticker = _find_ticker_summary(previous, ticker)
    if not previous_ticker:
        return ""
    stale_after_seconds = _execution_stale_threshold_seconds(manifest)
    previous_today = _ticker_investor_summary(
        previous_ticker,
        previous,
        language=language,
        stale_after_seconds=stale_after_seconds,
    ).get("today_action", "-")
    current_today = _ticker_investor_summary(
        ticker_summary,
        manifest,
        language=language,
        stale_after_seconds=stale_after_seconds,
    ).get("today_action", "-")
    previous_state = _execution_display_state(previous_ticker, stale_after_seconds=stale_after_seconds)
    current_state = _execution_display_state(ticker_summary, stale_after_seconds=stale_after_seconds)
    return f"""
    <section class="section">
      <div class="section-head">
        <h2>직전 run 대비 종목 변화</h2>
      </div>
      <article class="run-card">
        <p><strong>비교 run</strong><span>{_escape(str(previous.get('run_id') or '-'))}</span></p>
        <p><strong>판단 상태</strong><span>{_escape(previous_state)} → {_escape(current_state)}</span></p>
        <p class="long-field"><strong>Today 변화</strong><span>{_escape(previous_today)} → {_escape(current_today)}</span></p>
      </article>
    </section>
    """


def _previous_comparable_run(manifest: dict[str, Any], manifests: list[dict[str, Any]]) -> dict[str, Any] | None:
    current_run_id = str(manifest.get("run_id") or "")
    current_market = str(((manifest.get("settings") or {}).get("market") or "")).strip().lower()
    for item in manifests:
        run_id = str(item.get("run_id") or "")
        if run_id == current_run_id:
            continue
        market = str(((item.get("settings") or {}).get("market") or "")).strip().lower()
        if current_market and market and current_market != market:
            continue
        started = str(item.get("started_at") or "")
        current_started = str(manifest.get("started_at") or "")
        if started < current_started:
            return item
    return None


def _find_ticker_summary(manifest: dict[str, Any], ticker: str) -> dict[str, Any] | None:
    for item in manifest.get("tickers") or []:
        if str(item.get("ticker") or "").strip().upper() == ticker:
            return item
    return None


def _render_portfolio_page(
    manifest: dict[str, Any],
    settings: SiteSettings,
    *,
    portfolio_summary: dict[str, Any],
) -> str:
    run_dir = Path(manifest["_run_dir"])
    report_html = "<p class='empty'>No portfolio markdown report was generated.</p>"
    report_path = portfolio_summary.get("portfolio_report_md")
    if isinstance(report_path, Path) and report_path.exists():
        report_html = _render_markdown(report_path.read_text(encoding="utf-8"))

    download_links = []
    for source in portfolio_summary.get("downloadable_files", []):
        if not isinstance(source, Path):
            continue
        if _is_summary_image_artifact(source) and not _summary_image_publish_enabled(manifest):
            continue
        if not _is_public_portfolio_download(source):
            continue
        download_links.append(
            f"<a class='pill' href='../../downloads/{_escape(manifest['run_id'])}/portfolio/{_escape(source.name)}'>{_escape(source.name)}</a>"
        )

    failure_html = ""
    if portfolio_summary.get("status") == "failed":
        failure_html = (
            "<section class='section'>"
            "<div class='section-head'><h2>Failure</h2></div>"
            f"<pre class='error-block'>{_escape(portfolio_summary.get('error') or 'Unknown error')}</pre>"
            "</section>"
        )

    downloads_html = _download_details_html(
        download_links,
        summary="자료 다운로드",
        empty_text="다운로드 가능한 파일 없음",
    )
    status_label = _portfolio_status_label(str(portfolio_summary.get("status") or "unknown"))
    snapshot_mode = (
        present_snapshot_mode(str(portfolio_summary.get("snapshot_health")), language="English")
        if portfolio_summary.get("snapshot_health")
        else _portfolio_report_label(portfolio_summary)
    )
    portfolio_label = _portfolio_report_label(portfolio_summary)
    summary_image_html = _portfolio_summary_image_html(manifest, portfolio_summary)
    body = f"""
    <nav class="breadcrumbs">
      <a href="../../index.html">Home</a>
      <a href="index.html">{_escape(manifest['run_id'])}</a>
    </nav>
    <section class="hero compact">
      <div>
        <p class="eyebrow">{_escape(portfolio_label)}</p>
        <h1>{_escape(manifest['run_id'])}</h1>
        <p class="subtitle">{_escape(status_label)}</p>
      </div>
      <div class="hero-card">
        <div class="status {portfolio_summary.get('status_class', 'pending')}">{_escape(status_label)}</div>
        <p><strong>Account mode</strong><span>{_escape(snapshot_mode)}</span></p>
        <p><strong>Generated</strong><span>{_escape(portfolio_summary.get('generated_at') or '-')}</span></p>
      </div>
    </section>
    {failure_html}
    {summary_image_html}
    <section class="section prose">
      <div class="section-head">
        <h2>{_escape(portfolio_label)}</h2>
      </div>
      {report_html}
    </section>
    {_render_account_performance_section(manifest, portfolio_summary)}
    {_render_performance_tracking_section(manifest)}
    {downloads_html}
    {_render_live_context_delta_section(manifest)}
    """
    return _page_template(f"{manifest['run_id']} {portfolio_label.lower()} | {settings.title}", body, prefix="../../")


def _portfolio_has_etf_benchmark_page(portfolio_summary: dict[str, Any]) -> bool:
    payload = portfolio_summary.get("account_performance")
    if not isinstance(payload, dict):
        return False
    comparison = payload.get("etf_alternative_comparison")
    if not isinstance(comparison, dict) or not comparison:
        return False
    status = str(comparison.get("status") or "").strip().lower()
    return bool(status) and status not in {"cashflow_dates_required", "actual_performance_unavailable"}


def _render_etf_benchmark_page(
    manifest: dict[str, Any],
    settings: SiteSettings,
    *,
    portfolio_summary: dict[str, Any],
) -> str:
    payload = portfolio_summary.get("account_performance") if isinstance(portfolio_summary, dict) else {}
    comparison = payload.get("etf_alternative_comparison") if isinstance(payload, dict) else {}
    etf_html = _render_etf_alternative_comparison(comparison)
    etf_status = _etf_status_label((comparison or {}).get("status"))
    downloads = []
    for source in (
        portfolio_summary.get("etf_dca_comparison_json"),
        portfolio_summary.get("etf_dca_policy_recommendation_json"),
        portfolio_summary.get("etf_alternative_portfolios_public_json"),
    ):
        if isinstance(source, Path) and source.exists():
            downloads.append(
                f"<a class='pill' href='../../downloads/{_escape(manifest['run_id'])}/portfolio/{_escape(source.name)}'>{_escape(source.name)}</a>"
            )
    body = f"""
    <nav class="breadcrumbs">
      <a href="../../index.html">Home</a>
      <a href="index.html">{_escape(manifest['run_id'])}</a>
      <a href="portfolio.html">Portfolio</a>
    </nav>
    <section class="hero compact">
      <div>
        <p class="eyebrow">ETF DCA benchmark</p>
        <h1>동일 입금일 ETF 대체 비교</h1>
        <p class="subtitle">{_escape(str((comparison or {}).get('period_start') or '-'))} ~ {_escape(str((comparison or {}).get('period_end') or '-'))}</p>
      </div>
      <div class="hero-card">
        <div class="status {portfolio_summary.get('status_class', 'pending')}">{_escape(etf_status)}</div>
        <p><strong>실제 성과 출처</strong><span>{_escape(_actual_source_label((comparison or {}).get('actual_source')))}</span></p>
        <p><strong>목적</strong><span>동일 현금흐름 ETF 대체 비교</span></p>
      </div>
    </section>
    <section class="section">
      {etf_html or "<p class='empty'>ETF 대체 비교 데이터가 없습니다.</p>"}
    </section>
    {_download_details_html(downloads, summary="자료 다운로드", empty_text="다운로드 가능한 ETF 비교 파일 없음")}
    """
    return _page_template(f"{manifest['run_id']} ETF benchmark | {settings.title}", body, prefix="../../")


def _render_account_performance_section(manifest: dict[str, Any], portfolio_summary: dict[str, Any]) -> str:
    account_performance_status = (manifest.get("portfolio") or {}).get("account_performance") or {}
    if account_performance_status and not account_performance_status.get("publish_to_site", True):
        return ""
    payload = portfolio_summary.get("account_performance")
    if not isinstance(payload, dict) or not payload:
        return ""
    periods = payload.get("periods") if isinstance(payload.get("periods"), list) else []
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    quality = payload.get("data_quality") if isinstance(payload.get("data_quality"), dict) else {}
    costs = payload.get("costs") if isinstance(payload.get("costs"), dict) else {}
    contribution = payload.get("contribution_by_ticker") if isinstance(payload.get("contribution_by_ticker"), list) else []
    reconciliation = payload.get("reconciliation") if isinstance(payload.get("reconciliation"), dict) else {}
    broker_performance = payload.get("broker_performance") if isinstance(payload.get("broker_performance"), dict) else {}
    profit_calendar = payload.get("profit_calendar") if isinstance(payload.get("profit_calendar"), dict) else {}
    broker_comparison = (
        payload.get("broker_performance_comparison")
        if isinstance(payload.get("broker_performance_comparison"), dict)
        else {}
    )
    benchmarks = [str(item) for item in payload.get("benchmarks", []) if str(item)]
    default_period = str(summary.get("default_period") or (periods[-1].get("period") if periods and isinstance(periods[-1], dict) else "-"))
    default_period_label = str(summary.get("default_period_label") or default_period)
    if summary.get("partial") and default_period_label != "-":
        default_period_label = f"{default_period_label} (부분)"
    method_label = _account_return_method_label(summary.get("primary_return_method"), summary.get("return_method_warning"))
    coverage_label = _account_summary_coverage_label(summary)
    best = summary.get("best_excess") if isinstance(summary.get("best_excess"), dict) else {}
    worst = summary.get("worst_excess") if isinstance(summary.get("worst_excess"), dict) else {}
    hide_excess_headline = bool(summary.get("hide_excess_headline"))
    confidence_label = _account_confidence_label(summary)
    reconciliation_label = _account_reconciliation_label(reconciliation)
    reconciliation_status = str(reconciliation.get("reconciliation_status") or "").upper()
    profit_calendar_html = _render_profit_calendar_section(profit_calendar)
    has_broker_numbers = _broker_performance_has_numbers(broker_performance)
    if reconciliation_status == "FAILED" and not has_broker_numbers and not profit_calendar_html:
        return ""
    show_snapshot_headline = reconciliation_status != "FAILED" or bool(
        summary.get("show_snapshot_performance_when_unreconciled")
    )
    snapshot_return_value = (
        _format_pct_value(summary.get("actual_return"))
        if show_snapshot_headline
        else "성과 미표시"
    )
    snapshot_method_label = (
        "내부 스냅샷 기반 보조 계산"
        if broker_performance
        else method_label
    )
    public_json = portfolio_summary.get("account_performance_public_json")
    chart_json = portfolio_summary.get("account_performance_chart_data_json")
    report_md = portfolio_summary.get("account_performance_report_md")
    etf_dca_json = portfolio_summary.get("etf_dca_comparison_json")
    etf_policy_json = portfolio_summary.get("etf_dca_policy_recommendation_json")
    download_links = []
    for source in (public_json, chart_json, report_md, etf_dca_json, etf_policy_json):
        if isinstance(source, Path) and source.exists():
            download_links.append(
                f"<a class='pill' href='../../downloads/{_escape(manifest['run_id'])}/portfolio/{_escape(source.name)}'>{_escape(source.name)}</a>"
            )
    display_periods = _account_performance_display_periods(periods)
    hidden_period_note = _account_hidden_period_note(periods, display_periods)
    period_tabs = "".join(
        f"<a class='pill' href='#account-perf-{_escape(str(period.get('period') or 'period'))}'>{_escape(_account_period_label(period))}</a>"
        for period in display_periods
        if isinstance(period, dict)
    )
    table_rows = _account_performance_period_rows(display_periods, hide_untrusted=not show_snapshot_headline)
    contribution_rows = _account_contribution_rows(contribution, reconciliation=reconciliation)
    chart_html = _account_performance_svg(payload.get("chart_data") if isinstance(payload.get("chart_data"), dict) else {})
    if not show_snapshot_headline:
        chart_html = ""
    broker_html = _render_broker_performance_summary(
        broker_performance,
        broker_comparison,
        include_reconciliation_warning=show_snapshot_headline,
    )
    etf_html = _render_etf_alternative_comparison(payload.get("etf_alternative_comparison"))
    if not show_snapshot_headline and not broker_html and not etf_html and not profit_calendar_html:
        return ""
    if show_snapshot_headline and not display_periods and not broker_html and not etf_html and not profit_calendar_html:
        return ""
    benchmark_label = ", ".join(benchmarks) or "-"
    investor_notes = _account_performance_investor_notes(
        periods=periods,
        summary=summary,
        reconciliation=reconciliation,
        quality=quality,
    )
    benchmark_reliability = _account_benchmark_reliability_label(summary, reconciliation)
    benchmark_headline_value = (
        "-"
        if hide_excess_headline
        else f"{str(best.get('benchmark') or '-')} {_format_pct_value(best.get('excess_return'))}"
    )
    excess_headline_label = "초과손익 생략" if hide_excess_headline else str(best.get("benchmark") or "-")
    excess_headline_value = "-" if hide_excess_headline else _format_signed_krw_value(best.get("excess_krw"))
    snapshot_card = (
        f"""
        <article class="run-card">
          <h3>내부 스냅샷 수익률</h3>
          <p><strong>{_escape(snapshot_method_label)}</strong><span>{_escape(snapshot_return_value)}</span></p>
        </article>
        """
        if show_snapshot_headline and not hide_excess_headline
        else ""
    )
    benchmark_card = (
        f"""
        <article class="run-card">
          <h3>벤치마크 비교</h3>
          <p><strong>{_escape(benchmark_reliability)}</strong><span>{_escape(benchmark_headline_value)}</span></p>
        </article>
        """
        if show_snapshot_headline and not hide_excess_headline
        else ""
    )
    excess_card = (
        f"""
        <article class="run-card">
          <h3>초과손익 해석</h3>
          <p><strong>{_escape(excess_headline_label)}</strong><span>{_escape(excess_headline_value)}</span></p>
        </article>
        """
        if show_snapshot_headline and not hide_excess_headline
        else ""
    )
    period_table_html = (
        f"""
      <div class="pill-row account-period-tabs">{period_tabs}</div>
      {hidden_period_note}
      {chart_html}
      <div class="account-table-wrap">
        <table>
          <thead>
            <tr>
              <th>기간</th>
              <th>수익금</th>
              <th>실제</th>
              <th>단순 기간 수익률 비교</th>
              <th>동일 현금흐름 시뮬레이션</th>
              <th>MDD</th>
              <th>변동성</th>
            </tr>
          </thead>
          <tbody>{table_rows}</tbody>
        </table>
      </div>
        """
        if show_snapshot_headline
        else ""
    )
    internal_detail_grid = (
        f"""
      <div class="run-grid">
        <article class="run-card">
          <h3>보유/실현 손익 기여도</h3>
          {contribution_rows}
        </article>
        <article class="run-card">
          <h3>매매 비용</h3>
          <p><strong>수수료</strong><span>{_escape(_format_krw_value(costs.get('fees_krw')))}</span></p>
          <p><strong>세금</strong><span>{_escape(_format_krw_value(costs.get('taxes_krw')))}</span></p>
          <p><strong>총 비용</strong><span>{_escape(_format_krw_value(costs.get('total_cost_krw')))}</span></p>
        </article>
      </div>
        """
        if show_snapshot_headline
        else ""
    )
    summary_kpi_grid = (
        f"""
      <div class="run-grid account-kpi-grid">
        <article class="run-card">
          <h3>성과 신뢰도</h3>
          <p><strong>{_escape(confidence_label)}</strong><span>{_escape(reconciliation_label)}</span></p>
        </article>
        <article class="run-card">
          <h3>성과 기준 기간</h3>
          <p><strong>{_escape(default_period_label)}</strong><span>{_escape(coverage_label)}</span></p>
        </article>
        {snapshot_card}
        {benchmark_card}
        {excess_card}
      </div>
        """
        if show_snapshot_headline
        else ""
    )
    return f"""
    <section class="section account-performance">
      <div class="section-head">
        <h2>계좌 성과 vs 지수/ETF</h2>
        <p>{_escape(benchmark_label)}</p>
      </div>
      {profit_calendar_html}
      {broker_html}
      {etf_html}
      {summary_kpi_grid}
      {investor_notes}
      {period_table_html}
      {internal_detail_grid}
      <div class="pill-row">{''.join(download_links)}</div>
    </section>
    """


def _render_profit_calendar_section(value: dict[str, Any]) -> str:
    if not isinstance(value, dict) or not value:
        return ""
    weekly = value.get("weekly") if isinstance(value.get("weekly"), list) else []
    monthly = value.get("monthly") if isinstance(value.get("monthly"), list) else []
    rolling = value.get("rolling") if isinstance(value.get("rolling"), list) else []
    summary = value.get("summary") if isinstance(value.get("summary"), dict) else {}
    if not weekly and not monthly and not rolling:
        return ""
    cards = [
        _profit_kpi_card("이번 주 수익금", summary.get("current_week")),
        _profit_kpi_card("이번 달 수익금", summary.get("current_month")),
        _profit_kpi_card("최근 1주", summary.get("rolling_1w")),
        _profit_kpi_card("최근 1개월", summary.get("rolling_1m")),
    ]
    detail_rows = _profit_bucket_rows([*weekly, *monthly, *rolling])
    return f"""
      <div class="account-profit-calendar">
        <h3>기간별 수익금</h3>
        <div class="run-grid account-kpi-grid profit-kpi-grid">{''.join(cards)}</div>
        <div class="profit-calendar-grid">
          <article class="run-card profit-panel">
            <h3>주간</h3>
            {_profit_week_strip(weekly)}
          </article>
          <article class="run-card profit-panel">
            <h3>월간</h3>
            {_profit_month_bars(monthly)}
          </article>
        </div>
        <div class="account-table-wrap profit-detail-table">
          <h3>롤링 및 상세</h3>
          <table>
            <thead>
              <tr>
                <th>기간</th>
                <th>수익금</th>
                <th>수익률</th>
                <th>입금/출금</th>
                <th>기초/기말</th>
                <th>산출 소스</th>
              </tr>
            </thead>
            <tbody>{detail_rows}</tbody>
          </table>
        </div>
      </div>
    """


def _profit_kpi_card(title: str, bucket: Any) -> str:
    bucket = bucket if isinstance(bucket, dict) else {}
    status = _profit_status_label(bucket)
    return f"""
      <article class="run-card profit-kpi-card {_profit_value_class(bucket)}">
        <h3>{_escape(title)}</h3>
        <p><strong>{_escape(_format_signed_krw_value(_profit_amount(bucket)))}</strong><span>{_escape(_format_pct_points_value(_profit_return_pct(bucket)))}</span></p>
        <p><strong>{_escape(_profit_period_range(bucket))}</strong><span>{_escape(_profit_basis_status(bucket, status))}</span></p>
      </article>
    """


def _profit_week_strip(weekly: list[Any]) -> str:
    rows = [bucket for bucket in weekly if isinstance(bucket, dict)]
    if not rows:
        return "<p class='empty'>주간 수익금 데이터가 없습니다.</p>"
    return (
        "<div class='profit-week-strip'>"
        + "".join(
            "<div class='profit-week-item "
            f"{_profit_value_class(bucket)}'>"
            f"<strong>{_escape(str(bucket.get('label') or '-'))}</strong>"
            f"<span>{_escape(_format_signed_krw_value(_profit_amount(bucket)))}</span>"
            f"<em>{_escape(_profit_basis_status(bucket, _profit_status_label(bucket)))}</em>"
            "</div>"
            for bucket in rows
        )
        + "</div>"
    )


def _profit_month_bars(monthly: list[Any]) -> str:
    rows = [bucket for bucket in monthly if isinstance(bucket, dict)]
    if not rows:
        return "<p class='empty'>월간 수익금 데이터가 없습니다.</p>"
    max_abs = max(
        [
            abs(float(value))
            for bucket in rows
            if (value := _account_performance_number(_profit_amount(bucket))) is not None
        ]
        or [1.0]
    )
    parts = []
    for bucket in rows:
        value = _account_performance_number(_profit_amount(bucket))
        width = 0.0 if value is None else min(100.0, abs(float(value)) / max_abs * 100.0)
        parts.append(
            "<div class='profit-month-row'>"
            f"<span class='profit-month-label'>{_escape(str(bucket.get('label') or '-'))}</span>"
            "<span class='profit-month-track'>"
            f"<i class='{_profit_value_class(bucket)}' style='--profit-width:{width:.1f}%'></i>"
            "</span>"
            f"<strong>{_escape(_format_signed_krw_value(_profit_amount(bucket)))}</strong>"
            "</div>"
        )
    return "<div class='profit-month-bars'>" + "".join(parts) + "</div>"


def _profit_bucket_rows(buckets: list[Any]) -> str:
    rows = []
    for bucket in buckets:
        if not isinstance(bucket, dict):
            continue
        status = _profit_status_label(bucket)
        rows.append(
            "<tr>"
            f"<td>{_escape(str(bucket.get('label') or '-'))}<br><span class='account-period-note'>{_escape(_profit_period_range(bucket))}</span></td>"
            f"<td>{_escape(_format_signed_krw_value(_profit_amount(bucket)))}</td>"
            f"<td>{_escape(_format_pct_points_value(_profit_return_pct(bucket)))}</td>"
            f"<td>입금 {_escape(_format_krw_value(bucket.get('deposit_amount_krw')))}<br><span class='account-period-note'>출금 {_escape(_format_krw_value(bucket.get('withdrawal_amount_krw')))}</span></td>"
            f"<td>{_escape(_format_krw_value(bucket.get('start_asset_krw')))}<br><span class='account-period-note'>{_escape(_format_krw_value(bucket.get('end_asset_krw')))}</span></td>"
            f"<td>{_escape(_profit_source_label(bucket.get('source')))}<br><span class='account-period-note'>{_escape(_profit_basis_status(bucket, status))}</span></td>"
            "</tr>"
        )
    return "".join(rows) or "<tr><td colspan='6'>기간별 수익금 데이터가 없습니다.</td></tr>"


def _profit_status_label(bucket: dict[str, Any]) -> str:
    if not bucket:
        return "-"
    trust = str(bucket.get("trust_state") or "").strip()
    partial = "부분 기간" if bucket.get("partial") else ""
    labels = {
        "trusted": "검증",
        "broker_reported_with_warning": "브로커 경고",
        "partial_reference": "부분 참고",
        "cashflow_unadjusted_reference": "현금흐름 검증 필요",
        "unreconciled_reference": "정합성 검증 필요",
        "unavailable": "데이터 부족",
    }
    base = labels.get(trust, trust or "-")
    return f"{partial} / {base}" if partial and base != partial else base


def _profit_source_label(value: Any) -> str:
    labels = {
        "broker_reported": "브로커 앱",
        "internal_snapshot": "내부 스냅샷",
        "unavailable": "미산출",
    }
    return labels.get(str(value or ""), "-")


def _profit_amount(bucket: dict[str, Any]) -> Any:
    if not isinstance(bucket, dict):
        return None
    if "profit_krw" in bucket:
        return bucket.get("profit_krw")
    if bucket.get("display_eligible") is False and str(bucket.get("source") or "") == "internal_snapshot":
        return None
    return bucket.get("investment_pnl_krw")


def _profit_return_pct(bucket: dict[str, Any]) -> Any:
    if not isinstance(bucket, dict):
        return None
    if _profit_amount(bucket) is None:
        return None
    return bucket.get("return_pct")


def _profit_basis_status(bucket: dict[str, Any], status: str) -> str:
    basis = str(bucket.get("profit_basis") or "").strip()
    labels = {
        "realized_trade_pnl": "실현손익",
        "investment_pnl": "투자손익",
        "internal_snapshot": "내부 NAV 참고",
    }
    label = labels.get(basis, "")
    if not label:
        return status
    return f"{label} / {status}" if status and status != "-" else label


def _profit_period_range(bucket: dict[str, Any]) -> str:
    start = str(bucket.get("period_start") or "")
    end = str(bucket.get("period_end") or "")
    if not start and not end:
        return "-"
    return f"{start} ~ {end}"


def _profit_value_class(bucket: dict[str, Any]) -> str:
    number = _account_performance_number(_profit_amount(bucket)) if isinstance(bucket, dict) else None
    if number is None:
        return "profit-neutral"
    if number > 0:
        return "profit-positive"
    if number < 0:
        return "profit-negative"
    return "profit-neutral"


def _render_broker_performance_summary(
    broker: dict[str, Any],
    comparison: dict[str, Any],
    *,
    include_reconciliation_warning: bool = True,
) -> str:
    if not isinstance(broker, dict) or not broker:
        return ""
    broker_name = "한국투자증권" if str(broker.get("broker") or "").lower() == "kis" else str(broker.get("broker") or "브로커")
    period = f"{broker.get('period_start') or '-'} ~ {broker.get('period_end') or '-'}"
    comparison_status = str(comparison.get("comparison_status") or "OK").upper()
    warning = ""
    if comparison_status == "FAILED" and include_reconciliation_warning:
        warning = (
            "<div class='warning-banner account-performance-note'>"
            "브로커 앱 기말자산과 TradingAgents 내부 계좌 평가액이 크게 다릅니다. "
            "내부 스냅샷 기반 수익률과 초과수익은 기본 화면에서 제외합니다."
            "</div>"
        )
    elif comparison_status == "WARNING" and include_reconciliation_warning:
        warning = (
            "<div class='warning-banner account-performance-note'>"
            "브로커 앱 성과와 내부 스냅샷 성과의 기간 또는 값이 완전히 일치하지 않습니다."
            "</div>"
        )
    benchmark_rows = _broker_benchmark_cells(broker.get("benchmark_returns"))
    trade_cost = None
    trade_fees = _account_performance_number(broker.get("trade_fees_krw"))
    trade_taxes = _account_performance_number(broker.get("trade_taxes_krw"))
    if trade_fees is not None or trade_taxes is not None:
        trade_cost = float(trade_fees or 0.0) + float(trade_taxes or 0.0)
    trade_html = ""
    if broker.get("realized_trade_pnl_krw") is not None or broker.get("realized_trade_return_pct") is not None:
        trade_html = f"""
          <article class="run-card">
            <h3>매매손익</h3>
            <p><strong>{_escape(_format_signed_krw_value(broker.get('realized_trade_pnl_krw')))}</strong><span>매매손익률 {_escape(_format_pct_points_value(broker.get('realized_trade_return_pct')))}</span></p>
            <p><strong>매매 비용</strong><span>{_escape(_format_krw_value(trade_cost))}</span></p>
          </article>
        """
    return_html = ""
    if broker.get("balance_return_pct") is not None or broker.get("net_asset_return_pct") is not None:
        return_html = f"""
          <article class="run-card">
            <h3>브로커 수익률</h3>
            <p><strong>잔액/순자산 기준</strong><span>{_escape(_format_pct_points_value(broker.get('balance_return_pct')))}</span></p>
          </article>
        """
    investment_html = ""
    if broker.get("investment_pnl_krw") is not None or broker.get("end_asset_krw") is not None:
        investment_html = f"""
          <article class="run-card">
            <h3>투자손익</h3>
            <p><strong>{_escape(_format_signed_krw_value(broker.get('investment_pnl_krw')))}</strong><span>기말 {_escape(_format_krw_value(broker.get('end_asset_krw')))}</span></p>
          </article>
        """
    cashflow_html = ""
    if broker.get("deposit_amount_krw") is not None or broker.get("withdrawal_amount_krw") is not None:
        cashflow_html = f"""
          <article class="run-card">
            <h3>입출금</h3>
            <p><strong>입금 {_escape(_format_krw_value(broker.get('deposit_amount_krw')))}</strong><span>출금 {_escape(_format_krw_value(broker.get('withdrawal_amount_krw')))}</span></p>
          </article>
        """
    benchmark_html = ""
    if benchmark_rows != "-":
        benchmark_html = f"""
          <article class="run-card">
            <h3>브로커 기준 벤치마크</h3>
            <p><strong>앱 수익률 기준</strong><span>{benchmark_rows}</span></p>
          </article>
        """
    return f"""
      <div class="account-broker-performance">
        <h3>{_escape(broker_name)} 앱 기준 성과</h3>
        <div class="run-grid account-kpi-grid">
          <article class="run-card">
            <h3>브로커 기준 기간</h3>
            <p><strong>{_escape(period)}</strong><span>{_escape(str(broker.get('account_scope') or '-'))}</span></p>
          </article>
          {return_html}
          {investment_html}
          {cashflow_html}
          {trade_html}
          {benchmark_html}
        </div>
        {warning}
      </div>
    """


def _broker_performance_has_numbers(broker: dict[str, Any]) -> bool:
    if not isinstance(broker, dict) or not broker:
        return False
    return any(
        _account_performance_number(broker.get(key)) is not None
        for key in (
            "balance_return_pct",
            "investment_pnl_krw",
            "end_asset_krw",
            "realized_trade_pnl_krw",
            "realized_trade_return_pct",
        )
    )


def _broker_benchmark_cells(values: Any) -> str:
    if not isinstance(values, list) or not values:
        return "-"
    parts = []
    for item in values:
        if not isinstance(item, dict):
            continue
        parts.append(
            f"{_escape(str(item.get('benchmark') or '-'))} "
            f"{_escape(_format_pct_points_value(item.get('benchmark_return_pct')))}"
        )
    return " / ".join(parts) if parts else "-"


def _render_etf_alternative_comparison(value: Any) -> str:
    if not isinstance(value, dict) or not value:
        return ""
    status = str(value.get("status") or "").strip()
    if not status:
        return ""
    if status.lower() in {"cashflow_dates_required", "actual_performance_unavailable"}:
        return ""
    actual = value.get("actual") if isinstance(value.get("actual"), dict) else {}
    cashflows = value.get("cashflows") if isinstance(value.get("cashflows"), dict) else {}
    alternatives = [item for item in value.get("alternatives", []) if isinstance(item, dict)]
    ok_alternatives = [item for item in alternatives if str(item.get("status") or "").upper() == "OK"]
    best = (
        max(
            ok_alternatives,
            key=lambda item: _account_performance_number(item.get("balance_return_pct")) or -10**9,
        )
        if ok_alternatives
        else {}
    )
    blended = next((item for item in ok_alternatives if str(item.get("key") or "").upper() == "BLENDED"), {})
    policy = value.get("policy") if isinstance(value.get("policy"), dict) else {}
    decisions = policy.get("decisions") if isinstance(policy.get("decisions"), list) else []
    policy_text = ", ".join(str(item) for item in decisions) if decisions else str(policy.get("status") or "INSUFFICIENT_DATA")
    warning_items = [str(item) for item in value.get("warnings", []) if str(item)]
    warning_html = (
        "<div class='warning-banner account-performance-note'>"
        + "<br>".join(_escape(_friendly_etf_warning(item)) for item in warning_items[:4])
        + "</div>"
        if warning_items
        else ""
    )
    if status == "cashflow_dates_required":
        return f"""
      <div class="account-etf-alternatives">
        <h3>동일 입금일 ETF 대체 포트폴리오 비교</h3>
        <div class="warning-banner account-performance-note">
          정확한 ETF 대체 비교를 계산하려면 날짜별 입금/출금 내역이 필요합니다.
          현재 KIS 자동 원천에서는 총액 또는 다른 계좌 이벤트만 확인되어 정확한 적립식 ETF 비교를 제공하지 않습니다.
        </div>
        <div class="run-grid account-kpi-grid">
          <article class="run-card">
            <h3>현금흐름 상태</h3>
            <p><strong>KIS 일자 원장 미확인</strong><span>총입금 {_escape(_format_krw_value(cashflows.get('broker_deposit_amount_krw')))}</span></p>
          </article>
          <article class="run-card">
            <h3>실제 계좌 기준</h3>
            <p><strong>{_escape(str(value.get('actual_source') or '-'))}</strong><span>{_escape(_format_pct_points_value(actual.get('balance_return_pct')))}</span></p>
          </article>
          <article class="run-card">
            <h3>자동화 상태</h3>
            <p><strong>체결/손익/권리 자동</strong><span>외부 입출금 일자는 API 미제공</span></p>
          </article>
        </div>
        {warning_html}
      </div>
        """
    if status == "actual_performance_unavailable":
        reason_text = _friendly_etf_warning(str(value.get("reason") or status))
        return f"""
      <div class="account-etf-alternatives">
        <h3>동일 입금일 ETF 대체 포트폴리오 비교</h3>
        <div class="warning-banner account-performance-note">
          실제 계좌 성과가 검증되지 않아 ETF 대체 포트폴리오와 직접 비교하지 않습니다.
          브로커 계좌 수익률 또는 정합성 OK/WARNING 내부 스냅샷이 필요합니다.
        </div>
        <div class="run-grid account-kpi-grid">
          <article class="run-card">
            <h3>실제 계좌 성과</h3>
            <p><strong>비교 제외</strong><span>{_escape(reason_text)}</span></p>
          </article>
          <article class="run-card">
            <h3>날짜별 현금흐름</h3>
            <p><strong>{int(cashflows.get('dated_flow_count') or 0)}건</strong><span>KIS 일반계좌 입출금 일자 원천 미확인</span></p>
          </article>
          <article class="run-card">
            <h3>자동화 한계</h3>
            <p><strong>체결/손익/권리 자동</strong><span>외부 입출금 원장은 API 미제공</span></p>
          </article>
        </div>
        <p class="empty">CSV/JSON 연결은 KIS가 해당 원장을 제공하지 않을 때 쓰는 선택적 fallback입니다. 임의 날짜 합성은 하지 않습니다.</p>
        {warning_html}
      </div>
        """
    rows = _etf_alternative_rows(alternatives)
    curve_html = _etf_equity_curve_svg(
        alternatives=ok_alternatives,
        markers=[item for item in value.get("cashflow_markers", []) if isinstance(item, dict)],
    )
    return f"""
      <div class="account-etf-alternatives">
        <h3>동일 입금일 ETF 대체 포트폴리오 비교</h3>
        <p class="empty">같은 입금일에 같은 금액으로 ETF를 샀다면 어땠는지 계산합니다. 단순 기간 지수 수익률보다 실제 계좌 운용과 더 공정하게 비교합니다.</p>
        <div class="run-grid account-kpi-grid">
          <article class="run-card">
            <h3>실제 계좌 수익률</h3>
            <p><strong>{_escape(_actual_source_label(value.get('actual_source')))}</strong><span>{_escape(_format_pct_points_value(actual.get('balance_return_pct')))}</span></p>
          </article>
          <article class="run-card">
            <h3>ETF 대체 최고 수익률</h3>
            <p><strong>{_escape(str(best.get('label') or '-'))}</strong><span>{_escape(_format_pct_points_value(best.get('balance_return_pct')))}</span></p>
          </article>
          <article class="run-card">
            <h3>혼합 벤치마크</h3>
            <p><strong>{_escape(_format_pct_points_value(blended.get('balance_return_pct')))}</strong><span>실제 대비 {_escape(_format_pct_points_value(blended.get('excess_return_pct')))}</span></p>
          </article>
          <article class="run-card">
            <h3>정책 제안</h3>
            <p><strong>{_escape(str(policy.get('mode') or 'report_only'))}</strong><span>{_escape(policy_text)}</span></p>
          </article>
        </div>
        <div class="account-table-wrap">
          <table>
            <thead>
              <tr>
                <th>대체 포트폴리오</th>
                <th>최종 평가액</th>
                <th>수익률</th>
                <th>실제 계좌 대비</th>
                <th>MDD</th>
                <th>판단</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        {curve_html}
        {_render_etf_policy_box(policy)}
        {warning_html}
      </div>
    """


def _etf_alternative_rows(alternatives: list[dict[str, Any]]) -> str:
    rows: list[str] = []
    for item in alternatives:
        status = str(item.get("status") or "")
        if status.upper() != "OK":
            judgment = _friendly_etf_warning(",".join(str(warning) for warning in item.get("warnings", []) if warning)) or status
            rows.append(
                "<tr>"
                f"<td>{_escape(str(item.get('label') or item.get('key') or '-'))}</td>"
                "<td>-</td><td>-</td><td>-</td><td>-</td>"
                f"<td>{_escape(judgment)}</td>"
                "</tr>"
            )
            continue
        excess = _account_performance_number(item.get("excess_return_pct"))
        judgment = "실제 우위" if excess is not None and excess >= 0 else "ETF 우위"
        rows.append(
            "<tr>"
            f"<td>{_escape(str(item.get('label') or item.get('key') or '-'))}<br><span class='account-period-note'>{_escape(_etf_weights_label(item.get('weights')))}</span></td>"
            f"<td>{_escape(_format_krw_value(item.get('end_value_krw')))}</td>"
            f"<td>{_escape(_format_pct_points_value(item.get('balance_return_pct')))}</td>"
            f"<td>{_escape(_format_pct_points_value(item.get('excess_return_pct')))}<br><span class='account-period-note'>{_escape(_format_signed_krw_value(item.get('excess_pnl_krw')))}</span></td>"
            f"<td>{_escape(_format_pct_points_value(item.get('mdd_pct')))}</td>"
            f"<td>{_escape(judgment)}</td>"
            "</tr>"
        )
    if not rows:
        return "<tr><td colspan='6'>ETF 대체 포트폴리오를 계산할 수 없습니다.</td></tr>"
    return "".join(rows)


def _render_etf_policy_box(policy: dict[str, Any]) -> str:
    if not isinstance(policy, dict) or not policy:
        return ""
    checks = policy.get("checks") if isinstance(policy.get("checks"), dict) else {}
    labels = {
        "three_month_consecutive_underperformance": "3개월 기준",
        "six_month_cumulative_excess": "6개월 기준",
        "twelve_month_return_mdd_turnover": "12개월 기준",
        "action_add_starter_vs_etf": "액션 성과",
    }
    rows = []
    for key, label in labels.items():
        item = checks.get(key) if isinstance(checks.get(key), dict) else {}
        rows.append(f"<p><strong>{_escape(label)}</strong><span>{_escape(str(item.get('status') or 'INSUFFICIENT_DATA'))}</span></p>")
    core = policy.get("core_satellite_recommendation") if isinstance(policy.get("core_satellite_recommendation"), dict) else {}
    if core:
        core_weight = (_account_performance_number(core.get("recommended_core_etf_weight")) or 0.0) * 100.0
        individual_weight = (_account_performance_number(core.get("recommended_individual_stock_weight")) or 0.0) * 100.0
        rows.append(
            "<p><strong>현재 권고</strong><span>"
            f"ETF core {_escape(_format_pct_points_value(core_weight))} / "
            f"개별 종목 {_escape(_format_pct_points_value(individual_weight))}"
            "</span></p>"
        )
    return (
        "<article class='run-card account-performance-note'>"
        "<h3>개별 종목 비중 판단</h3>"
        + "".join(rows)
        + "</article>"
    )


def _etf_equity_curve_svg(*, alternatives: list[dict[str, Any]], markers: list[dict[str, Any]]) -> str:
    series = []
    for item in alternatives[:6]:
        curve = [point for point in item.get("equity_curve", []) if isinstance(point, dict)]
        points = []
        for point in curve:
            value = _account_performance_number(point.get("value_krw"))
            date_text = str(point.get("date") or "")
            if value is not None and date_text:
                points.append((date_text, value))
        if points:
            series.append({"label": str(item.get("label") or item.get("key") or "-"), "points": points})
    if not series:
        return ""
    width = 760
    height = 260
    pad_x = 56
    pad_y = 28
    all_dates = sorted({date_text for item in series for date_text, _value in item["points"]})
    all_values = [value for item in series for _date_text, value in item["points"]]
    if not all_dates or not all_values:
        return ""
    min_value = min(all_values)
    max_value = max(all_values)
    if max_value <= min_value:
        max_value = min_value + 1
    date_index = {date_text: index for index, date_text in enumerate(all_dates)}

    def x_for(date_text: str) -> float:
        if len(all_dates) == 1:
            return width / 2
        return pad_x + (width - pad_x * 2) * date_index[date_text] / (len(all_dates) - 1)

    def y_for(value: float) -> float:
        return height - pad_y - (height - pad_y * 2) * (value - min_value) / (max_value - min_value)

    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf"]
    lines = []
    legends = []
    for index, item in enumerate(series):
        path = " ".join(f"{x_for(date_text):.1f},{y_for(value):.1f}" for date_text, value in item["points"])
        color = colors[index % len(colors)]
        lines.append(f"<polyline fill='none' stroke='{color}' stroke-width='2.2' points='{path}' />")
        legends.append(
            f"<span><i style='background:{color}'></i>{_escape(item['label'])}</span>"
        )
    marker_lines = []
    marker_dates = sorted({str(item.get("date") or "") for item in markers if str(item.get("date") or "") in date_index})
    for date_text in marker_dates:
        x = x_for(date_text)
        marker_lines.append(
            f"<line x1='{x:.1f}' y1='{pad_y}' x2='{x:.1f}' y2='{height - pad_y}' stroke='#8b95a1' stroke-dasharray='4 4' stroke-width='1' />"
        )
    return (
        "<div class='account-performance-chart account-etf-curve'>"
        "<h3>ETF 대체 포트폴리오 equity curve</h3>"
        "<p class='account-period-note'>점선은 날짜별 입출금 이벤트가 있었던 날입니다. 금액은 공개 화면에 표시하지 않습니다.</p>"
        f"<svg viewBox='0 0 {width} {height}' role='img' aria-label='ETF DCA equity curves'>"
        f"<rect x='0' y='0' width='{width}' height='{height}' fill='white' />"
        + "".join(marker_lines)
        + f"<line x1='{pad_x}' y1='{height - pad_y}' x2='{width - pad_x}' y2='{height - pad_y}' stroke='#d0d7de' />"
        + f"<line x1='{pad_x}' y1='{pad_y}' x2='{pad_x}' y2='{height - pad_y}' stroke='#d0d7de' />"
        + "".join(lines)
        + f"<text x='{pad_x}' y='{height - 6}' font-size='11' fill='#57606a'>{_escape(all_dates[0])}</text>"
        + f"<text x='{width - pad_x - 70}' y='{height - 6}' font-size='11' fill='#57606a'>{_escape(all_dates[-1])}</text>"
        + "</svg>"
        + "<div class='etf-curve-legend'>"
        + "".join(legends)
        + "</div></div>"
    )


def _etf_weights_label(value: Any) -> str:
    if not isinstance(value, dict):
        return "-"
    parts = []
    for key, weight in value.items():
        try:
            parts.append(f"{key} {float(weight) * 100:.0f}%")
        except (TypeError, ValueError):
            continue
    return " / ".join(parts) if parts else "-"


def _actual_source_label(value: Any) -> str:
    source = str(value or "")
    if source == "broker_reported":
        return "한국투자증권 앱 기준"
    if source == "internal_reconciled_snapshot":
        return "내부 스냅샷 정합 기준"
    if source == "unavailable":
        return "비교 제외"
    return source or "-"


def _friendly_etf_warning(value: str) -> str:
    text = str(value or "")
    if "actual_performance_unavailable" in text:
        return "실제 계좌 성과가 검증되지 않아 ETF 대체 비교를 계산하지 않았습니다."
    if "cashflow_dates_required" in text:
        return "날짜별 입금/출금 원장이 필요합니다."
    if "yfinance_empty" in text or "price_missing" in text:
        code = text.rsplit(":", 1)[-1] if ":" in text else "ETF"
        return f"{code} 가격 데이터가 비어 해당 ETF 대체 포트폴리오를 계산하지 않았습니다."
    if "price_missing" in text:
        return "ETF 가격 데이터가 없어 해당 벤치마크를 계산하지 않았습니다."
    if "fx_missing" in text:
        return "해외 ETF의 KRW 환산 FX 데이터가 필요합니다."
    if "deposit_total_mismatch" in text:
        return "날짜별 입금 합계와 브로커 총입금액이 일치하지 않습니다."
    if "withdrawal_total_mismatch" in text:
        return "날짜별 출금 합계와 브로커 총출금액이 일치하지 않습니다."
    if "seed_ignored_below_minimum" in text:
        return "기초자산이 최소 seed 기준보다 작아 ETF seed 매수에서 제외했습니다."
    if "period_start_mismatch" in text or "period_end_mismatch" in text:
        return "실제 계좌 성과 기간과 ETF 대체 비교 기간이 달라 직접 비교할 수 없습니다."
    return text


def _etf_status_label(value: Any) -> str:
    status = str(value or "").strip()
    normalized = status.lower()
    if normalized == "ok":
        return "계산 완료"
    if normalized == "actual_performance_unavailable":
        return "비교 데이터 없음"
    if normalized == "cashflow_dates_required":
        return "입금일 원장 필요"
    if normalized == "no_alternatives":
        return "대체 포트폴리오 없음"
    return _friendly_etf_warning(status) if status else "-"


def _account_reconciliation_detail_html(
    reconciliation: dict[str, Any],
    quality: dict[str, Any],
    comparison: dict[str, Any],
) -> str:
    status = str(reconciliation.get("reconciliation_status") or "").upper()
    comparison_status = str(comparison.get("comparison_status") or "").upper()
    if status != "FAILED" and comparison_status != "FAILED":
        return ""
    return f"""
      <div class="warning-banner account-performance-note">
        정합성 상세:
        NAV 변화 {_escape(_format_signed_krw_value(reconciliation.get('simple_nav_pnl_krw')))} /
        기여도 합계 {_escape(_format_signed_krw_value(reconciliation.get('sum_position_contribution_krw')))} /
        외부 현금흐름 {_escape(_format_signed_krw_value(reconciliation.get('external_cashflow_net_krw')))} /
        설명 가능 변화 {_escape(_format_signed_krw_value(reconciliation.get('explained_change_krw')))} /
        현금 변화 {_escape(_format_signed_krw_value(reconciliation.get('cash_delta_krw')))} /
        보유 평가액 변화 {_escape(_format_signed_krw_value(reconciliation.get('position_market_value_delta_krw')))} /
        비용 {_escape(_format_krw_value(reconciliation.get('fees_taxes_krw')))} /
        미해명 차이 {_escape(_format_signed_krw_value(reconciliation.get('unexplained_difference_krw')))} /
        외부자금흐름 감지 {int(quality.get('external_capital_flow_count') or 0)}건 /
        브로커-내부 기말자산 차이 {_escape(_format_signed_krw_value(comparison.get('end_asset_delta_krw')))}
      </div>
    """


def _account_reconciliation_guidance_html(reconciliation: dict[str, Any]) -> str:
    actions = reconciliation.get("resolution_actions") if isinstance(reconciliation, dict) else None
    if not isinstance(actions, list) or not actions:
        return ""
    cards = []
    for item in actions[:5]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "정합성 보완").strip()
        evidence = str(item.get("evidence") or "").strip()
        required = str(item.get("required_input") or "").strip()
        suggested = str(item.get("suggested_file") or "").strip()
        cards.append(
            "<article class='run-card'>"
            f"<h3>{_escape(title)}</h3>"
            f"<p><strong>{_escape(evidence or '-')}</strong><span>{_escape(required or '-')}</span></p>"
            f"<p><strong>연결 상태</strong><span>{_escape(suggested or '-')}</span></p>"
            "</article>"
        )
    if not cards:
        return ""
    return (
        "<div class='account-reconciliation-guidance'>"
        "<h3>정합성 해결/자동화 상태</h3>"
        "<div class='run-grid account-kpi-grid'>"
        + "".join(cards)
        + "</div></div>"
    )


def _friendly_account_warning(value: Any) -> str:
    text = str(value or "")
    if "etf_alternative_actual_performance_unavailable" in text:
        return "실제 계좌 성과가 검증되지 않아 ETF 대체 비교를 계산하지 않았습니다."
    if "etf_alternative_cashflow_dates_required" in text:
        return "날짜별 입금/출금 원장이 없어 동일 현금흐름 ETF 비교를 계산하지 않았습니다."
    if "account_performance_resolution_actions_required" in text:
        return "성과 정합성을 풀기 위한 자동화 상태와 남은 입력을 표시했습니다."
    if "account_performance_unreconciled_pnl" in text:
        return "NAV 변화와 보유/실현 손익 기여도 합계가 맞지 않아 수익률을 기본 해석에서 제외했습니다."
    if "account_performance_contribution_not_total_return" in text:
        return "보유/실현 손익 기여도는 총 NAV 수익률 전체를 대체하지 않습니다."
    if "account_performance_broker_external_flows_not_in_snapshot_ledger" in text:
        return "브로커 집계 입출금은 있지만 내부 원장에는 날짜별 외부자금흐름이 없습니다."
    if "broker_performance_missing_balance_return" in text:
        return "브로커 계좌 전체 수익률 데이터가 없어 KIS 매매손익과 NAV 성과를 분리했습니다."
    if "broker_performance_missing_end_asset" in text:
        return "브로커 기말자산 데이터가 없어 내부 계좌 평가액과 직접 대조하지 못했습니다."
    if "account_performance_kis_ledger_endpoint_failed:domestic_period_rights" in text:
        return "KIS 기간별 계좌권리 자동 조회가 실패해 배당/권리 현금 이벤트 보강이 제한됐습니다."
    if "account_performance_kis_ledger_endpoint_failed" in text:
        return "일부 KIS 원장 API 조회가 실패했지만 가능한 원장만 사용했습니다."
    if "account_performance_cashflow" in text:
        return "입출금 원장이 부족해 현금흐름 보정 성과가 제한됩니다."
    return _friendly_etf_warning(text)


def _prioritized_account_warnings(warnings: Any) -> list[str]:
    if not isinstance(warnings, list):
        return []
    priority_markers = (
        "broker_performance_comparison",
        "account_performance_broker_external_flows",
        "account_performance_unreconciled_pnl",
        "account_performance_resolution_actions_required",
        "account_performance_cashflow",
        "etf_alternative_actual_performance_unavailable",
        "etf_alternative_cashflow_dates_required",
    )
    values = [str(item) for item in warnings]
    return sorted(
        values,
        key=lambda item: (
            0 if any(marker in item for marker in priority_markers) else 1,
            item,
        ),
    )


def _account_performance_display_periods(periods: list[Any]) -> list[dict[str, Any]]:
    display = [
        period
        for period in periods
        if isinstance(period, dict)
        and _account_performance_number(period.get("actual_return")) is not None
        and period.get("status") not in {"insufficient_history", "duplicate_actual_window"}
        and not period.get("same_actual_window_as")
        and period.get("display_eligible") is not False
        and str(period.get("trust_state") or "") != "unreconciled_reference"
    ]
    if display:
        return display
    return [
        period
        for period in periods
        if isinstance(period, dict)
        and _account_performance_number(period.get("actual_return")) is not None
        and period.get("display_eligible") is not False
        and str(period.get("trust_state") or "") != "unreconciled_reference"
    ]


def _account_hidden_period_note(periods: list[Any], display_periods: list[dict[str, Any]]) -> str:
    display_names = {str(period.get("period") or "") for period in display_periods}
    hidden = []
    for period in periods:
        if not isinstance(period, dict):
            continue
        name = str(period.get("period") or "-")
        if name in display_names:
            continue
        if period.get("status") in {"insufficient_history", "duplicate_actual_window"} or period.get("same_actual_window_as"):
            hidden.append(name)
    if not hidden:
        return ""
    labels = "/".join(dict.fromkeys(hidden))
    return (
        "<p class='empty'>"
        f"{_escape(labels)}는 계좌 기록이 해당 기간 전체를 커버하지 않아 별도 성과로 표시하지 않습니다. "
        "아래 사용 가능 전체 기간 기준만 기본 비교에 사용합니다."
        "</p>"
    )


def _account_performance_period_rows(
    periods: list[Any],
    *,
    diagnostics: bool = False,
    hide_untrusted: bool = False,
) -> str:
    rows: list[str] = []
    for period in periods:
        if not isinstance(period, dict):
            continue
        period_name = str(period.get("period") or "-")
        row_id = f"account-perf-raw-{period_name}" if diagnostics else f"account-perf-{period_name}"
        period_label = _account_period_label(period)
        partial_note = ""
        if period.get("partial"):
            start = str(period.get("start_date") or "-")
            requested = str(period.get("requested_start_date") or "-")
            coverage = period.get("period_coverage") if isinstance(period.get("period_coverage"), dict) else {}
            ratio = _format_coverage_ratio(coverage.get("coverage_ratio"))
            duplicate = str(coverage.get("same_actual_window_as") or period.get("same_actual_window_as") or "")
            duplicate_text = f" / {duplicate}와 동일 창" if duplicate else ""
            partial_note = (
                f"<br><span class='account-period-note'>부분 산출: 요청 {_escape(requested)} / 실제 {_escape(start)}"
                f" / 커버리지 {_escape(ratio)}{_escape(duplicate_text)}</span>"
            )
        if period.get("status") in {"insufficient_history", "duplicate_actual_window"} and not diagnostics:
            continue
        if period.get("status") == "insufficient_history":
            rows.append(
                "<tr "
                f"id='{_escape(row_id)}'>"
                f"<td>{_escape(period_label)}{partial_note}</td>"
                "<td>-</td>"
                "<td>데이터 부족</td>"
                "<td>요청 기간 시작일의 계좌 스냅샷 없음</td>"
                "<td>-</td>"
                "<td>-</td>"
                "<td>-</td>"
                "</tr>"
            )
            continue
        if period.get("status") == "duplicate_actual_window":
            rows.append(
                "<tr "
                f"id='{_escape(row_id)}'>"
                f"<td>{_escape(period_label)}{partial_note}</td>"
                "<td>-</td>"
                "<td>중복 기간</td>"
                f"<td>{_escape(str(period.get('same_actual_window_as') or '-'))}와 동일 실제 기간</td>"
                "<td>-</td>"
                "<td>-</td>"
                "<td>-</td>"
                "</tr>"
            )
            continue
        method_note = _account_return_method_label(period.get("primary_return_method"), period.get("return_method_warning"))
        if not diagnostics and (
            hide_untrusted
            or period.get("display_eligible") is False
            or str(period.get("trust_state") or "") == "unreconciled_reference"
        ):
            continue
        rows.append(
            "<tr "
            f"id='{_escape(row_id)}'>"
            f"<td>{_escape(period_label)}{partial_note}</td>"
            f"<td>{_escape(_format_signed_krw_value(period.get('investment_pnl_krw')))}<br><span class='account-period-note'>{_escape(_profit_source_label(period.get('profit_source')))}</span></td>"
            f"<td>{_escape(_format_pct_value(period.get('actual_return')))}<br><span class='account-period-note'>{_escape(method_note)}</span></td>"
            f"<td>{_benchmark_comparison_cells(period.get('simple_benchmarks'))}</td>"
            f"<td>{_benchmark_comparison_cells(period.get('cashflow_benchmarks'))}</td>"
            f"<td>{_escape(_format_pct_value(period.get('mdd')))}</td>"
            f"<td>{_escape(_format_pct_value(period.get('volatility')))}</td>"
            "</tr>"
        )
    if not rows:
        return "<tr><td colspan='7'>성과를 계산할 수 있는 기간 데이터가 아직 부족합니다.</td></tr>"
    return "".join(rows)


def _account_period_label(period: dict[str, Any]) -> str:
    name = str(period.get("period") or "-")
    if name.upper() == "ALL":
        name = "사용 가능 전체 기간"
    return f"{name} (부분)" if period.get("partial") else name


def _benchmark_comparison_cells(values: Any) -> str:
    if not isinstance(values, list) or not values:
        return "-"
    parts = []
    for item in values:
        if not isinstance(item, dict):
            continue
        reliability = str(item.get("reliability") or "")
        suffix = " 참고용" if reliability == "reference" else ""
        parts.append(
            f"<span>{_escape(str(item.get('benchmark') or '-'))}: "
            f"{_escape(_format_pct_value(item.get('benchmark_return')))} / "
            f"초과 {_escape(_format_pct_value(item.get('excess_return')))} "
            f"({_escape(_format_signed_krw_value(item.get('excess_krw')))}"
            f"){_escape(suffix)}</span>"
        )
    return "<br>".join(parts) if parts else "-"


def _account_return_method_label(method: Any, warning: Any = None) -> str:
    method_text = str(method or "").strip().lower()
    warning_text = str(warning or "").strip().lower()
    if method_text == "twr":
        return "현금흐름 보정 TWR"
    if method_text in {"twr_equivalent", "available_history_twr_equivalent"}:
        return "외부 현금흐름 없음 - TWR 상당 단순 NAV"
    if method_text == "mwr":
        return "현금흐름 보정 MWR"
    if warning_text in {"cashflow_adjustment_unavailable", "broker_external_cashflow_unmodeled"} or method_text == "simple_nav_unadjusted":
        return "현금흐름 미보정 단순 NAV 기준"
    if method_text == "available_history_simple_nav":
        return "사용 가능 기간 단순 NAV 기준"
    if method_text == "insufficient_history":
        return "기간 데이터 부족"
    return "단순 NAV 기준"


def _format_coverage_ratio(value: Any) -> str:
    try:
        if value is None:
            return "-"
        return f"{float(value) * 100:.0f}%"
    except (TypeError, ValueError):
        return "-"


def _account_summary_coverage_label(summary: dict[str, Any]) -> str:
    start = str(summary.get("start_date") or "-")
    end = str(summary.get("end_date") or "-")
    coverage = summary.get("period_coverage") if isinstance(summary.get("period_coverage"), dict) else {}
    ratio = _format_coverage_ratio(coverage.get("coverage_ratio"))
    if start != "-" and end != "-":
        return f"{start} ~ {end} ({ratio})"
    return ratio


def _account_confidence_label(summary: dict[str, Any]) -> str:
    confidence = str(summary.get("performance_confidence") or "").strip().lower()
    return {
        "high": "높음",
        "medium": "보통",
        "low": "낮음",
    }.get(confidence, "미확인")


def _account_reconciliation_label(reconciliation: dict[str, Any]) -> str:
    status = str(reconciliation.get("reconciliation_status") or "UNAVAILABLE").strip().upper()
    labels = {
        "OK": "확인됨",
        "WARNING": "참고용",
        "FAILED": "성과 미표시",
        "UNAVAILABLE": "성과 미표시",
    }
    return labels.get(status, "성과 미표시")


def _account_performance_status_badges(portfolio_summary: dict[str, Any]) -> str:
    payload = portfolio_summary.get("account_performance") if isinstance(portfolio_summary, dict) else None
    if not isinstance(payload, dict):
        return ""
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    reconciliation = payload.get("reconciliation") if isinstance(payload.get("reconciliation"), dict) else {}
    if not summary and not reconciliation:
        return ""
    confidence = _account_confidence_label(summary)
    reconciliation_label = _account_reconciliation_label(reconciliation)
    status = str(reconciliation.get("reconciliation_status") or "").strip().upper()
    if status in {"FAILED", "UNAVAILABLE"}:
        return ""
    badge_class = "failed" if status == "FAILED" else ("partial_failure" if status in {"WARNING", "UNAVAILABLE"} else "success")
    return (
        f"<div class='status {badge_class}'>계좌 성과: {_escape(reconciliation_label)}</div>"
        f"<p><strong>성과 신뢰도</strong><span>{_escape(confidence)}</span></p>"
    )


def _account_benchmark_reliability_label(summary: dict[str, Any], reconciliation: dict[str, Any]) -> str:
    if bool(summary.get("hide_excess_headline")):
        return "비교 생략"
    warning = str(summary.get("return_method_warning") or "")
    status = str(reconciliation.get("reconciliation_status") or "").upper()
    if warning in {"cashflow_adjustment_unavailable", "broker_external_cashflow_unmodeled"} or status in {"WARNING", "FAILED", "UNAVAILABLE"}:
        return "참고용"
    return "비교 가능"


def _account_performance_investor_notes(
    *,
    periods: list[Any],
    summary: dict[str, Any],
    reconciliation: dict[str, Any],
    quality: dict[str, Any],
) -> str:
    notes: list[str] = []
    if str(summary.get("default_period") or "") == "ALL_AVAILABLE":
        start = str(summary.get("start_date") or "-")
        end = str(summary.get("end_date") or "-")
        notes.append(f"성과 기준 기간: {start} ~ {end} (사용 가능 전체 기간)")
    method_label = _account_return_method_label(summary.get("primary_return_method"), summary.get("return_method_warning"))
    notes.append(f"계좌 수익률: {method_label}")
    if summary.get("return_method_warning") == "cashflow_adjustment_unavailable":
        notes.append("벤치마크 비교: 참고용 - 외부 현금흐름 보정이 불완전합니다.")
    if summary.get("return_method_warning") == "broker_external_cashflow_unmodeled":
        notes.append("브로커 입출금이 반영되지 않은 보조 계산은 기본 해석에서 제외합니다.")
    status = str(reconciliation.get("reconciliation_status") or "").upper()
    if status == "WARNING":
        notes.append("보유/실현 손익 합계와 NAV 변화가 크게 달라 초과수익 headline은 보조 참고로만 표시합니다.")
    warnings = quality.get("warnings") if isinstance(quality.get("warnings"), list) else []
    if any("account_performance_duplicate_actual_windows" in str(item) for item in warnings):
        notes.append("일부 요청 기간은 실제 사용 가능 기간이 같아 기본 표에서는 합쳐서 보여줍니다.")
    if not notes:
        return ""
    return "<div class='warning-banner account-performance-note'>" + "<br>".join(_escape(item) for item in notes) + "</div>"


def _account_benchmark_provider_messages(quality: dict[str, Any]) -> str:
    statuses = quality.get("benchmark_provider_status")
    if not isinstance(statuses, dict):
        return ""
    fallback_by_used: dict[tuple[str, str], list[str]] = {}
    provider_lines = []
    for benchmark, status in statuses.items():
        if not isinstance(status, dict):
            continue
        preferred = str(status.get("preferred_provider") or "-")
        used = str(status.get("used_provider") or "-")
        state = str(status.get("status") or "-")
        if state == "fallback":
            fallback_by_used.setdefault((preferred, used), []).append(str(benchmark))
        elif used not in {"", "-", "None"}:
            provider_lines.append(f"{benchmark}: {used}")
        elif state not in {"ok", "pending"}:
            provider_lines.append(f"{benchmark}: {state}")
        elif preferred:
            provider_lines.append(f"{benchmark}: {preferred}")
    messages = []
    for (preferred, used), names in fallback_by_used.items():
        provider = used if used not in {"", "-", "None"} else "대체 provider"
        preferred_label = preferred.upper() if preferred not in {"", "-", "None"} else "선호 provider"
        messages.append(f"벤치마크 가격: {'/'.join(names)} = {preferred_label} 실패 후 {provider} fallback")
    if provider_lines:
        messages.append("벤치마크 가격: " + ", ".join(provider_lines))
    if not messages:
        return ""
    return "<p class='empty'>" + "<br>".join(_escape(item) for item in messages) + "</p>"


def _account_benchmark_provider_label(quality: dict[str, Any]) -> str:
    statuses = quality.get("benchmark_provider_status")
    if not isinstance(statuses, dict) or not statuses:
        provider = str(quality.get("benchmark_provider") or "-")
        return f"기본 설정 {provider}" if provider not in {"", "-", "None"} else "-"
    ok_by_provider: dict[str, list[str]] = {}
    fallback: list[str] = []
    unavailable: list[str] = []
    for benchmark, status in statuses.items():
        if not isinstance(status, dict):
            continue
        used = str(status.get("used_provider") or "").strip()
        preferred = str(status.get("preferred_provider") or "").strip()
        state = str(status.get("status") or "").strip().lower()
        name = str(benchmark)
        if state == "fallback":
            provider = used or "fallback"
            fallback.append(f"{name}={provider} fallback")
        elif used:
            ok_by_provider.setdefault(used, []).append(name)
        elif preferred:
            ok_by_provider.setdefault(preferred, []).append(name)
        else:
            unavailable.append(f"{name}=unavailable")
    parts = [f"{'/'.join(names)}={provider}" for provider, names in sorted(ok_by_provider.items())]
    parts.extend(fallback)
    parts.extend(unavailable)
    return ", ".join(parts) if parts else "-"


def _account_contribution_rows(contribution: list[Any], *, reconciliation: dict[str, Any]) -> str:
    status = str(reconciliation.get("reconciliation_status") or "").upper()
    if status == "OK":
        status_html = "<p class='empty'>기간 중 실현손익과 미실현손익 변화가 NAV 변화와 허용 범위 안에서 일치합니다.</p>"
    else:
        status_html = (
            "<p class='empty'>이 표는 기간 중 실현손익과 미실현손익 변화를 요약하며, 입출금·환전·배당·수수료·데이터 차이로 "
            "총 NAV 변화와 일치하지 않을 수 있습니다.</p>"
        )
    if not contribution:
        return status_html + "<p class='empty'>산출 가능한 기여도 데이터가 없습니다.</p>"
    rows = []
    for item in contribution[:8]:
        if not isinstance(item, dict):
            continue
        ticker = str(item.get("ticker") or "-")
        display_name = str(item.get("display_name") or "").strip()
        label = display_name if display_name and display_name != ticker else ticker
        value = _format_signed_krw_value(item.get("total_contribution_krw"))
        detail = f"{value} · {ticker}" if label != ticker else value
        rows.append(
            "<p>"
            f"<strong>{_escape(label)}</strong>"
            f"<span>{_escape(detail)}</span>"
            "</p>"
        )
    return status_html + ("".join(rows) or "<p class='empty'>산출 가능한 기여도 데이터가 없습니다.</p>")


def _account_performance_svg(chart_data: dict[str, Any]) -> str:
    series = chart_data.get("series") if isinstance(chart_data.get("series"), list) else []
    benchmarks = [str(item) for item in chart_data.get("benchmarks", []) if str(item)]
    title = str(chart_data.get("title") or "사용 가능 기간 수익률")
    if len(series) < 2:
        return "<p class='empty'>차트를 그릴 만큼의 일별 계좌 스냅샷이 아직 충분하지 않습니다.</p>"
    keys = ["account_return", *benchmarks]
    values: list[float] = []
    for row in series:
        if not isinstance(row, dict):
            continue
        for key in keys:
            try:
                if row.get(key) is not None:
                    values.append(float(row[key]))
            except (TypeError, ValueError):
                continue
    if not values:
        return "<p class='empty'>차트 기준 수익률 데이터가 없습니다.</p>"
    min_value = min(values)
    max_value = max(values)
    if min_value == max_value:
        min_value -= 0.01
        max_value += 0.01
    width = 980
    height = 320
    left = 56
    right = 24
    top = 24
    bottom = 44
    plot_w = width - left - right
    plot_h = height - top - bottom
    colors = {
        "account_return": "#0f7c82",
        "KOSPI": "#7a4d9f",
        "KOSDAQ": "#c46a1c",
        "SPY": "#2f6f45",
        "QQQ": "#8b3f52",
    }

    def point(index: int, value: float) -> tuple[float, float]:
        x = left + (plot_w * index / max(1, len(series) - 1))
        y = top + plot_h - ((value - min_value) / (max_value - min_value) * plot_h)
        return x, y

    polylines = []
    labels = []
    for key in keys:
        points = []
        for index, row in enumerate(series):
            if not isinstance(row, dict) or row.get(key) is None:
                continue
            try:
                points.append(point(index, float(row[key])))
            except (TypeError, ValueError):
                continue
        if len(points) < 2:
            continue
        color = colors.get(key, "#374151")
        point_text = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        label = "계좌" if key == "account_return" else key
        polylines.append(f"<polyline points='{point_text}' fill='none' stroke='{color}' stroke-width='3' stroke-linecap='round' stroke-linejoin='round' />")
        labels.append(f"<span><i style='background:{color}'></i>{_escape(label)}</span>")
    zero_y = point(0, 0.0)[1] if min_value <= 0 <= max_value else None
    zero_line = (
        f"<line x1='{left}' y1='{zero_y:.1f}' x2='{width - right}' y2='{zero_y:.1f}' stroke='#d9e2e1' stroke-dasharray='4 5' />"
        if zero_y is not None
        else ""
    )
    start_label = str((series[0] or {}).get("date") or "")
    end_label = str((series[-1] or {}).get("date") or "")
    final_return = chart_data.get("final_return")
    peak_return = chart_data.get("peak_return")
    max_drawdown = chart_data.get("max_drawdown")
    if final_return is None:
        final_return = (series[-1] or {}).get("account_return")
    if peak_return is None:
        account_values = [
            float(row.get("account_return"))
            for row in series
            if isinstance(row, dict) and row.get("account_return") is not None
        ]
        peak_return = max(account_values) if account_values else None
    chart_warning = ""
    if str(chart_data.get("consistency_status") or "") == "warning":
        chart_warning = "<p class='empty'>차트 최종 수익률과 요약 수익률이 달라 원시 산출 검토가 필요합니다.</p>"
    screen_reader_text = (
        f"{title}. 기간 {start_label}부터 {end_label}까지. "
        f"최종 수익률 {_format_pct_value(final_return)}, "
        f"기간 중 최고 수익률 {_format_pct_value(peak_return)}, "
        f"최대 낙폭 {_format_pct_value(max_drawdown)}."
    )
    return (
        "<div class='account-chart'>"
        f"<h3 class='account-chart-title'>{_escape(title)}</h3>"
        "<div class='account-chart-stats'>"
        f"<span>최종 수익률: {_escape(_format_pct_value(final_return))}</span>"
        f"<span>기간 중 최고 수익률: {_escape(_format_pct_value(peak_return))}</span>"
        f"<span>최대 낙폭: {_escape(_format_pct_value(max_drawdown))}</span>"
        "</div>"
        f"{chart_warning}"
        f"<p class='sr-only'>{_escape(screen_reader_text)}</p>"
        f"<svg viewBox='0 0 {width} {height}' aria-hidden='true' focusable='false'>"
        f"<rect x='0' y='0' width='{width}' height='{height}' rx='12' fill='#fbfdfd' />"
        f"<line x1='{left}' y1='{height - bottom}' x2='{width - right}' y2='{height - bottom}' stroke='#cfd8d6' />"
        f"<line x1='{left}' y1='{top}' x2='{left}' y2='{height - bottom}' stroke='#cfd8d6' />"
        f"{zero_line}{''.join(polylines)}"
        "</svg>"
        f"<div class='account-chart-legend'>{''.join(labels)}</div>"
        "</div>"
    )


def _render_performance_tracking_section(manifest: dict[str, Any]) -> str:
    performance = manifest.get("performance") or {}
    if not performance.get("enabled"):
        return ""
    summary = performance.get("summary") if isinstance(performance.get("summary"), dict) else {}
    outcome_update = performance.get("outcome_update") if isinstance(performance.get("outcome_update"), dict) else {}
    artifacts = performance.get("artifacts") if isinstance(performance.get("artifacts"), dict) else {}
    if int(summary.get("outcomes") or 0) <= 0 or not outcome_update.get("updated"):
        return ""
    artifact_link = ""
    artifact_name = Path(str(artifacts.get("performance_summary_json") or "")).name
    if artifact_name:
        artifact_link = (
            f"<a class='pill' href='../../downloads/{_escape(manifest['run_id'])}/portfolio/{_escape(artifact_name)}'>"
            f"{_escape(artifact_name)}</a>"
        )
    action_rows = _performance_bucket_rows(summary.get("by_action") if isinstance(summary.get("by_action"), dict) else {})
    prism_rows = _performance_bucket_rows(summary.get("prism_agreement") if isinstance(summary.get("prism_agreement"), dict) else {})
    action_bucket_rows = _performance_bucket_rows(summary.get("action_buckets") if isinstance(summary.get("action_buckets"), dict) else {})
    profit_rows = _performance_bucket_rows(summary.get("profit_taking") if isinstance(summary.get("profit_taking"), dict) else {})
    calibration = summary.get("calibration") if isinstance(summary.get("calibration"), dict) else {}
    calibration_html = _performance_calibration_card(calibration)
    tables_html = "".join(
        table
        for table in (
            _performance_table("액션별 5일/20일 성과", action_rows),
            _performance_table("익절 성과", profit_rows),
            _performance_table("PRISM 일치/충돌별 성과", prism_rows),
            _performance_table("추천 출처/PRISM 커버리지별 성과", action_bucket_rows),
        )
        if table
    )
    if not calibration_html and not tables_html:
        return ""
    return f"""
    <section class="section">
      <div class="section-head">
        <h2>추천 성과 추적</h2>
      </div>
      <article class="run-card">
        <p><strong>기록된 추천</strong><span>{int(summary.get('recommendations') or 0)}</span></p>
        <p><strong>업데이트된 outcome</strong><span>{int(summary.get('outcomes') or 0)}</span></p>
        <div class="pill-row">{artifact_link}</div>
      </article>
      {calibration_html}
      <div class="run-grid">
        {tables_html}
      </div>
    </section>
    """


def _performance_calibration_card(calibration: dict[str, Any]) -> str:
    if not calibration:
        return ""
    fields = [
        ("액션 승격 미주문 비율", _format_pct_value(calibration.get("actionable_not_ordered_rate"))),
        ("미주문 후보 5일 성과", _format_pct_value(calibration.get("missed_upside_5d"))),
        ("미주문 후보 20일 missed upside", _format_pct_value(calibration.get("missed_upside_20d"))),
        ("PRISM 충돌 상승 비율", _format_pct_value(calibration.get("prism_conflict_winner_rate"))),
    ]
    rows = [
        f"<p><strong>{_escape(label)}</strong><span>{_escape(value)}</span></p>"
        for label, value in fields
        if value != "-"
    ]
    if not rows:
        return ""
    return f"""
      <article class="run-card">
        {''.join(rows)}
      </article>
    """


def _performance_bucket_rows(buckets: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for bucket, metrics in buckets.items():
        if not isinstance(metrics, dict):
            continue
        if metrics.get("avg_return_5d") is None and metrics.get("avg_return_20d") is None:
            continue
        rows.append(
            {
                "bucket": str(bucket or "UNKNOWN"),
                "count": int(metrics.get("count") or 0),
                "avg_return_5d": metrics.get("avg_return_5d"),
                "avg_return_20d": metrics.get("avg_return_20d"),
            }
        )
    rows.sort(key=lambda row: (-row["count"], row["bucket"]))
    return rows[:8]


def _performance_table(title: str, rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    table_rows = "".join(
        "<tr>"
        f"<td>{_escape(row['bucket'])}</td>"
        f"<td>{row['count']}</td>"
        f"<td>{_escape(_format_pct_value(row.get('avg_return_5d')))}</td>"
        f"<td>{_escape(_format_pct_value(row.get('avg_return_20d')))}</td>"
        "</tr>"
        for row in rows
    )
    body = (
        "<table><thead><tr><th>구분</th><th>건수</th><th>평균 5일</th><th>평균 20일</th></tr></thead>"
        f"<tbody>{table_rows}</tbody></table>"
    )
    return f"<article class='run-card'><h3>{_escape(title)}</h3>{body}</article>"


def _is_public_portfolio_download(source: Path) -> bool:
    if source.suffix.lower() not in {".json", ".md"}:
        return False
    private_names = {
        "account_snapshot.json",
        "status.json",
        "portfolio_action_judge.json",
        "portfolio_semantic_verdicts.json",
        "decision_audit.json",
        "report_writer.json",
        "portfolio_report_writer.json",
        "account_performance_report.json",
        "etf_alternative_portfolios_raw.json",
        "etf_dca_cashflows.json",
        "cashflows.json",
        "cashflows_audit.json",
        "etf_dca_benchmark_transactions.json",
        "etf_dca_equity_curves.json",
        "summary_image_spec.json",
        "summary_image_metadata.json",
        "broker_performance_raw.json",
        "broker_performance_normalized.json",
    }
    return source.name not in private_names


def _format_pct_value(value: Any) -> str:
    try:
        if value is None:
            return "-"
        return f"{float(value) * 100:.2f}%"
    except (TypeError, ValueError):
        return "-"


def _format_pct_points_value(value: Any) -> str:
    try:
        if value is None:
            return "-"
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return "-"


def _format_krw_value(value: Any) -> str:
    try:
        if value is None:
            return "-"
        return f"{int(round(float(value))):,} KRW"
    except (TypeError, ValueError):
        return "-"


def _format_signed_krw_value(value: Any) -> str:
    try:
        if value is None:
            return "-"
        number = int(round(float(value)))
    except (TypeError, ValueError):
        return "-"
    sign = "+" if number > 0 else ""
    return f"{sign}{number:,} KRW"


def _portfolio_summary_image_html(manifest: dict[str, Any], portfolio_summary: dict[str, Any]) -> str:
    if not _summary_image_publish_enabled(manifest):
        return ""
    image_path = portfolio_summary.get("summary_image_png") or portfolio_summary.get("summary_image_svg")
    if not isinstance(image_path, Path) or not image_path.exists():
        return ""
    image_name = image_path.name
    href = f"../../downloads/{_escape(manifest['run_id'])}/portfolio/{_escape(image_name)}"
    return f"""
    <section class="section summary-image-section">
      <div class="section-head">
        <h2>요약 이미지</h2>
        <a class="pill" href="{href}">Download image</a>
      </div>
      <figure class="summary-image-frame">
        <img src="{href}" alt="TradingAgents portfolio summary image for {_escape(manifest['run_id'])}" loading="lazy" />
      </figure>
    </section>
    """


def _summary_image_publish_enabled(manifest: dict[str, Any]) -> bool:
    settings = manifest.get("settings") or {}
    return bool(settings.get("summary_image_publish_to_site", True))


def _is_summary_image_artifact(path: Path) -> bool:
    name = path.name.lower()
    return name.startswith("summary_card") and path.suffix.lower() in {".svg", ".png", ".jpg", ".jpeg", ".webp"}


def _render_ticker_page(
    manifest: dict[str, Any],
    ticker_summary: dict[str, Any],
    settings: SiteSettings,
    *,
    manifests: list[dict[str, Any]] | None = None,
    portfolio_summary: dict[str, Any] | None = None,
) -> str:
    run_dir = Path(manifest["_run_dir"])
    language = _manifest_language(manifest)
    stale_after_seconds = _execution_stale_threshold_seconds(manifest)
    report_html = "<p class='empty'>No report markdown was generated for this ticker.</p>"
    report_relative = (ticker_summary.get("artifacts") or {}).get("report_markdown")
    if report_relative:
        report_path = _resolve_artifact_source(run_dir, report_relative)
        if report_path.exists():
            report_html = _render_markdown(report_path.read_text(encoding="utf-8"))

    download_links = []
    for relative_path in (ticker_summary.get("artifacts") or {}).values():
        if not relative_path:
            continue
        artifact_name = Path(str(relative_path)).name
        download_links.append(
            f"<a class='pill' href='../../downloads/{_escape(manifest['run_id'])}/{_escape(ticker_summary['ticker'])}/{_escape(artifact_name)}'>{_escape(artifact_name)}</a>"
        )
    downloads_html = _download_details_html(
        download_links,
        summary="자료 다운로드",
        empty_text="다운로드 가능한 파일 없음",
    )

    failure_html = ""
    if ticker_summary["status"] != "success":
        failure_html = (
            "<section class='section'>"
            "<div class='section-head'><h2>Failure</h2></div>"
            f"<pre class='error-block'>{_escape(ticker_summary.get('error') or 'Unknown error')}</pre>"
            "</section>"
        )

    display_summary = _with_portfolio_action(ticker_summary, portfolio_summary or {})
    investor_summary = _ticker_investor_summary(
        display_summary,
        manifest,
        language=language,
        stale_after_seconds=stale_after_seconds,
    )
    microstructure_status_html = _render_ticker_microstructure_publication_section(
        run_dir=run_dir,
        manifest=manifest,
        ticker_summary=ticker_summary,
    )
    live_ticker_delta_html = _render_live_ticker_context_delta_section(
        manifest=manifest,
        ticker_summary=ticker_summary,
    )
    ticker_delta_html = _render_ticker_delta_section(
        manifest=manifest,
        ticker_summary=ticker_summary,
        manifests=manifests or [],
        language=language,
    )
    institutional_html = _render_ticker_institutional_section(
        run_dir=run_dir,
        ticker_summary=ticker_summary,
    )
    body = f"""
    <nav class="breadcrumbs">
      <a href="../../index.html">Home</a>
      <a href="index.html">{_escape(manifest['run_id'])}</a>
    </nav>
    <section class="hero compact">
      <div>
        <p class="eyebrow">Ticker report</p>
        <h1>{_escape(_ticker_display_label(ticker_summary))}</h1>
        <p class="subtitle">Analysis {_escape(ticker_summary.get('analysis_date') or '-')} / Market {_escape(ticker_summary.get('trade_date') or '-')} / {_escape(ticker_summary['status'])}</p>
      </div>
      <div class="hero-card">
        <div class="status {ticker_summary['status']}">{_escape(ticker_summary['status'])}</div>
        <p><strong>기준 시각</strong><span>{_escape(investor_summary['basis_asof'])}</span></p>
        <p><strong>{_escape(investor_summary['investment_view_label'])}</strong><span>{_escape(investor_summary['investment_view'])}</span></p>
        <p><strong>중기 리서치 관점</strong><span>{_escape(investor_summary['research_view'])}</span></p>
        <p><strong>오늘 할 일</strong><span>{_escape(investor_summary['today_action'])}</span></p>
        <p><strong>장중 pilot 조건</strong><span>{_escape(investor_summary['intraday_pilot_action'])}</span></p>
        <p><strong>종가 확인 시 할 일</strong><span>{_escape(investor_summary['close_action'])}</span></p>
        <p><strong>내일 follow-through</strong><span>{_escape(investor_summary['next_day_action'])}</span></p>
        <p><strong>리서치 기준</strong><span>{_escape(investor_summary['research_basis'])}</span></p>
        <p><strong>실행 기준</strong><span>{_escape(investor_summary['execution_basis'])}</span></p>
        <p><strong>핵심 가격대</strong><span>{_escape(investor_summary['key_levels'])}</span></p>
        <p><strong>위험 요약</strong><span>{_escape(investor_summary['risk_summary'])}</span></p>
        <p><strong>왜 이 종목인가</strong><span>{_escape(investor_summary['why_this_ticker'])}</span></p>
        {_advanced_diagnostics_html(ticker_summary, manifest, stale_after_seconds=stale_after_seconds)}
      </div>
    </section>
    {microstructure_status_html}
    {live_ticker_delta_html}
    {ticker_delta_html}
    {institutional_html}
    {failure_html}
    <section class="section prose">
      <div class="section-head">
        <h2>Report</h2>
      </div>
      {report_html}
    </section>
    {downloads_html}
    """
    return _page_template(
        f"{_ticker_display_label(ticker_summary)} | {settings.title}",
        body,
        prefix="../../",
    )


def _render_ticker_institutional_section(*, run_dir: Path, ticker_summary: dict[str, Any]) -> str:
    artifacts = ticker_summary.get("artifacts") if isinstance(ticker_summary.get("artifacts"), dict) else {}
    source_rel = artifacts.get("source_quality_json")
    analysis_rel = artifacts.get("analysis_json")
    payload: dict[str, Any] = {}
    if source_rel:
        source_path = _resolve_artifact_source(run_dir, source_rel)
        if source_path.exists():
            try:
                loaded = json.loads(source_path.read_text(encoding="utf-8"))
                payload = loaded if isinstance(loaded, dict) else {}
            except Exception:
                payload = {}
    if not payload and analysis_rel:
        analysis_path = _resolve_artifact_source(run_dir, analysis_rel)
        if analysis_path.exists():
            try:
                analysis_payload = json.loads(analysis_path.read_text(encoding="utf-8"))
                payload = analysis_payload.get("institutional_intelligence") if isinstance(analysis_payload, dict) else {}
                payload = payload if isinstance(payload, dict) else {}
            except Exception:
                payload = {}
    if not payload:
        return ""

    coverage = payload.get("coverage") if isinstance(payload.get("coverage"), dict) else {}
    warnings = [str(item) for item in (payload.get("warnings") or []) if str(item).strip()]
    providers = coverage.get("public_providers") or []
    institutional = coverage.get("institutional_import_providers") or []
    warning_html = ""
    if warnings:
        warning_html = (
            "<div class='warning-banner'>"
            + _escape("; ".join(warnings[:5]))
            + "</div>"
        )
    return f"""
    <section class="section">
      <div class="section-head">
        <h2>원천/증거 상태</h2>
      </div>
      <div class="ticker-grid">
        <article class="ticker-card">
          <p><strong>원천 품질</strong><span>{_escape(payload.get('source_quality_score', '-'))}</span></p>
          <p><strong>데이터군</strong><span>{_escape(payload.get('source_cohort') or '-')}</span></p>
          <p><strong>공개 provider</strong><span>{_escape(', '.join(str(item) for item in providers) or '-')}</span></p>
          <p><strong>기관 import</strong><span>{_escape(', '.join(str(item) for item in institutional) or '-')}</span></p>
        </article>
        <article class="ticker-card">
          <p><strong>실적팩</strong><span>{_escape(coverage.get('earnings_event_status') or '-')}</span></p>
          <p><strong>전사록</strong><span>{_escape('available' if coverage.get('transcript_available') else 'unavailable')}</span></p>
          <p><strong>컨센서스 변화</strong><span>{_escape(coverage.get('estimate_revision_direction') or '-')}</span></p>
          <p><strong>증거 수</strong><span>{_escape(coverage.get('source_ref_count') or 0)}</span></p>
        </article>
      </div>
      {warning_html}
    </section>
    """


def _page_template(title: str, body: str, *, prefix: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{_escape(title)}</title>
  <link rel="stylesheet" href="{prefix}assets/style.css" />
</head>
<body>
  <main class="shell">
    {body}
  </main>
</body>
</html>
"""


def _render_ticker_microstructure_publication_section(
    *,
    run_dir: Path,
    manifest: dict[str, Any],
    ticker_summary: dict[str, Any],
) -> str:
    artifacts = ticker_summary.get("artifacts") if isinstance(ticker_summary.get("artifacts"), dict) else {}
    snapshot_rel = artifacts.get("microstructure_snapshot_json")
    if not snapshot_rel:
        return ""
    snapshot_path = _resolve_artifact_source(run_dir, snapshot_rel)
    if not snapshot_path.is_file():
        return ""
    try:
        payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    micro = payload.get("microstructure") if isinstance(payload.get("microstructure"), dict) else {}
    freshness = payload.get("freshness_class") or micro.get("freshness_class") or ""
    eligibility = payload.get("execution_eligibility") or micro.get("execution_eligibility") or ""
    generated = payload.get("generated_in_current_run")
    source_run = payload.get("microstructure_source_run_id") or micro.get("microstructure_source_run_id") or ""
    backfilled = payload.get("backfilled_from_run_id") or micro.get("backfilled_from_run_id") or ""
    asof = payload.get("artifact_asof") or payload.get("asof") or micro.get("artifact_asof") or micro.get("asof_local") or ""
    age = payload.get("artifact_age_seconds_at_publish") or micro.get("artifact_age_seconds_at_publish")
    generated_text = "true" if generated is True else ("false" if generated is False else "")
    status = (
        "fresh"
        if generated is True and str(eligibility).upper() in {"LIVE_EXECUTION_READY", "LIVE_EXECUTION_OK", "PILOT_READY", "ACTIONABLE_NOW"}
        else "warning"
    )
    note = (
        "이번 run에서 새로 생성된 장중 microstructure입니다."
        if generated is True
        else "이 microstructure는 이전 체크포인트에서 보존된 자료이며 현재 실행 판단이 아니라 과거 as-of 참고 자료입니다."
    )
    return f"""
    <section class="section">
      <div class="section-head">
        <h2>Microstructure freshness</h2>
      </div>
      <article class="run-card">
        <div class="run-card-header">
          <span>Execution eligibility</span>
          <span class="status {status}">{_escape(str(eligibility or '-'))}</span>
        </div>
        <p><strong>Generated in current run</strong><span>{_escape(generated_text)}</span></p>
        <p><strong>Freshness class</strong><span>{_escape(str(freshness or '-'))}</span></p>
        <p><strong>As-of</strong><span>{_escape(str(asof or '-'))}</span></p>
        <p><strong>Age at publish</strong><span>{_escape(str(age if age not in (None, '') else '-'))}</span></p>
        <p><strong>Source run</strong><span>{_escape(str(source_run or '-'))}</span></p>
        <p><strong>Backfilled from</strong><span>{_escape(str(backfilled or '-'))}</span></p>
        <p class="long-field"><strong>Note</strong><span>{_escape(note)}</span></p>
      </article>
    </section>
    """


def _manifest_language(manifest: dict[str, Any]) -> str:
    return str((manifest.get("settings") or {}).get("output_language") or "English")


def _decision_market_view(raw_decision: Any, *, language: str) -> str:
    presentation = present_decision_payload(raw_decision, language=language)
    return presentation.market_view if presentation else "-"


def _decision_primary_condition(raw_decision: Any, *, language: str) -> str:
    return present_primary_condition(raw_decision, language=language)


def _with_portfolio_action(ticker_summary: dict[str, Any], portfolio_summary: dict[str, Any]) -> dict[str, Any]:
    actions_by_ticker = portfolio_summary.get("actions_by_ticker") if isinstance(portfolio_summary, dict) else {}
    action_lift_by_ticker = portfolio_summary.get("action_lift_by_ticker") if isinstance(portfolio_summary, dict) else {}
    ticker = str(ticker_summary.get("ticker") or "").strip()
    extras: dict[str, Any] = {}
    if isinstance(actions_by_ticker, dict):
        action = actions_by_ticker.get(ticker)
        if isinstance(action, dict):
            extras["portfolio_action"] = action
    if isinstance(action_lift_by_ticker, dict):
        lift = action_lift_by_ticker.get(ticker)
        if isinstance(lift, dict):
            extras["action_lift_audit"] = lift
    if not extras:
        return ticker_summary
    return {**ticker_summary, **extras}


def _portfolio_execution_view(portfolio_action: dict[str, Any], *, language: str) -> str:
    if not isinstance(portfolio_action, dict) or not portfolio_action:
        return ""
    korean = language.lower().startswith("korean")
    action_now = str(portfolio_action.get("action_now") or "").upper()
    relative_action = str(portfolio_action.get("portfolio_relative_action") or "").upper()
    risk_action = str(portfolio_action.get("risk_action") or "").upper()
    sell_intent = str(portfolio_action.get("sell_intent") or "").upper()
    if action_now in {"STOP_LOSS_NOW", "EXIT_NOW"} or relative_action in {"STOP_LOSS", "EXIT"} or risk_action in {"STOP_LOSS", "EXIT"}:
        return "손절/청산 검토" if korean else "Review stop-loss / exit"
    if action_now == "TAKE_PROFIT_NOW" or sell_intent == "TAKE_PROFIT" or relative_action == "TAKE_PROFIT":
        return "이익실현 검토" if korean else "Review take-profit"
    if action_now in {"REDUCE_NOW", "TRIM_NOW"} or relative_action == "REDUCE_RISK":
        return "일부 축소 검토" if korean else "Review partial reduction"
    if action_now in {"ADD_NOW", "STARTER_NOW"}:
        return "매수 검토" if korean else "Review buy"
    if relative_action == "TRIM_TO_FUND":
        return "재배치용 축소 후보" if korean else "Trim candidate for funding"
    return ""


def _portfolio_today_action(portfolio_action: dict[str, Any], *, language: str) -> str:
    if not isinstance(portfolio_action, dict) or not portfolio_action:
        return ""
    korean = language.lower().startswith("korean")
    action_now = str(portfolio_action.get("action_now") or "").upper()
    if action_now not in {"STOP_LOSS_NOW", "EXIT_NOW", "REDUCE_NOW", "TRIM_NOW", "TAKE_PROFIT_NOW", "ADD_NOW", "STARTER_NOW"}:
        return ""
    label = present_account_action(action_now, language=language)
    reason = sanitize_investor_text(portfolio_action.get("rationale") or "", language=language)
    level = _portfolio_level_text(portfolio_action, language=language)
    if korean:
        detail = f": {level}" if level else ""
        suffix = f" - {reason}" if reason and reason != "없음" else ""
        return f"{label}{detail}{suffix}"
    detail = f": {level}" if level else ""
    suffix = f" - {reason}" if reason and reason != "None" else ""
    return f"{label}{detail}{suffix}"


def _portfolio_close_action(portfolio_action: dict[str, Any], *, language: str) -> str:
    if not isinstance(portfolio_action, dict) or not portfolio_action:
        return ""
    action_if_triggered = str(portfolio_action.get("action_if_triggered") or "").upper()
    if action_if_triggered not in {"REDUCE_IF_TRIGGERED", "TAKE_PROFIT_IF_TRIGGERED", "STOP_LOSS_IF_TRIGGERED", "EXIT_IF_TRIGGERED"}:
        return ""
    level = _portfolio_level_text(portfolio_action, language=language)
    label = present_account_action(action_if_triggered, conditional=True, language=language)
    if language.lower().startswith("korean"):
        return f"종가 기준 {level} 확인 시 {label}" if level else f"종가 확인 시 {label}"
    return f"At close, {label.lower()} if {level}" if level else f"At close, {label.lower()}"


def _action_lift_today_action(action_lift: dict[str, Any], *, language: str) -> str:
    if not isinstance(action_lift, dict) or not action_lift:
        return ""
    korean = language.lower().startswith("korean")
    status = str(action_lift.get("lift_status") or "").strip().upper()
    next_action = str(action_lift.get("next_valid_action") or "").strip()
    if status == "ACTION_LIFT_FAILURE":
        return (
            f"액션 승격 실패 점검: {next_action or 'block_reason 확인 후 pilot 전환 여부 검토'}"
            if korean
            else f"Action lift failure: {next_action or 'review block reasons before a pilot'}"
        )
    if status == "BUY_SIGNAL_RELABELED_AS_SELL_SIDE":
        return (
            f"매수 신호가 계좌 sell-side 표현에 묻힘: {next_action or 'pilot 가능 여부 재검토'}"
            if korean
            else f"Buy signal was relabeled as sell-side: {next_action or 'review pilot eligibility'}"
        )
    if status == "PRISM_SOFT_BLOCK_PILOT_ALLOWED":
        return (
            f"PRISM 충돌: full-size 금지, 수동 확인 후 pilot만 검토"
            if korean
            else "PRISM conflict: block full-size, review pilot only"
        )
    if status == "BUDGET_BLOCKED":
        return (
            f"실행 신호는 있으나 예산/버퍼 차단: {next_action or '현금 여력 확인'}"
            if korean
            else f"Signal exists but budget/cash buffer blocks it: {next_action or 'check cash capacity'}"
        )
    return ""


def _portfolio_level_text(portfolio_action: dict[str, Any], *, language: str) -> str:
    level = portfolio_action.get("risk_action_level") if isinstance(portfolio_action.get("risk_action_level"), dict) else {}
    if not level:
        return ""
    price = level.get("price")
    if price in (None, ""):
        low = level.get("low")
        high = level.get("high")
        if low not in (None, "") and high not in (None, ""):
            return f"{low}~{high}"
        price = low if low not in (None, "") else high
    if price in (None, ""):
        return ""
    return f"{price}"


def _ticker_investor_summary(
    ticker_summary: dict[str, Any],
    manifest: dict[str, Any] | None = None,
    *,
    language: str | None = None,
    stale_after_seconds: int = 180,
) -> dict[str, str]:
    return _ticker_investor_summary_v2(
        ticker_summary=ticker_summary,
        manifest=manifest,
        language=language,
        stale_after_seconds=stale_after_seconds,
    )


def _ticker_investor_summary_v2(
    *,
    ticker_summary: dict[str, Any],
    manifest: dict[str, Any] | None = None,
    language: str | None = None,
    stale_after_seconds: int = 180,
) -> dict[str, str]:
    manifest = manifest or {}
    language = language or _manifest_language(manifest)
    korean = language.lower().startswith("korean")
    primary_condition = _decision_primary_condition(ticker_summary.get("decision"), language=language)
    if primary_condition in {"", "-", "None", "?놁쓬"}:
        primary_condition = "조건 확인" if korean else "confirmation"

    display_state = _execution_display_state(ticker_summary, stale_after_seconds=stale_after_seconds)
    raw_timing_state = str(_execution_payload(ticker_summary).get("execution_timing_state") or "").strip().upper()
    timing_state = _normalize_execution_timing_state(raw_timing_state)
    stale_or_degraded = _is_stale_or_degraded(ticker_summary, stale_after_seconds=stale_after_seconds)
    execution_quality = _ticker_execution_data_quality(ticker_summary)
    delayed_analysis_only = execution_quality == DELAYED_ANALYSIS_ONLY
    stance = _decision_structured_value(ticker_summary.get("decision"), "portfolio_stance").upper()
    entry_action = _decision_structured_value(ticker_summary.get("decision"), "entry_action").upper()
    research_view = present_investment_view(ticker_summary.get("decision") or ticker_summary.get("error"), language=language)
    portfolio_action = ticker_summary.get("portfolio_action") if isinstance(ticker_summary.get("portfolio_action"), dict) else {}
    action_lift = ticker_summary.get("action_lift_audit") if isinstance(ticker_summary.get("action_lift_audit"), dict) else {}
    account_execution_view = _portfolio_execution_view(portfolio_action, language=language)

    if korean:
        if raw_timing_state == "LIVE_BREAKOUT":
            today_action = f"장중 기준 돌파 구간 진입: {primary_condition}"
            close_action = f"종가 확인 후 추가 검토: {primary_condition}"
        elif raw_timing_state == "CLOSE_CONFIRM":
            today_action = f"장중 조건 진입, 종가 확인 대기: {primary_condition}"
            close_action = f"종가 기준 {primary_condition} 유지 시 실행 검토"
        else:
            today_map = {
                "PILOT_READY": f"소형 pilot 가능: {primary_condition}",
                "PILOT_BLOCKED_VOLUME": f"거래량 확인 전 pilot 보류: {primary_condition}",
                "CLOSE_CONFIRM_PENDING": f"종가 확인 대기: {primary_condition}",
                "CLOSE_CONFIRMED": f"종가 확인 대기: {primary_condition}",
                "FAILED_BREAKOUT": f"실패 돌파 주의, 신규 금지 또는 축소 검토: {primary_condition}",
                "PILOT_BLOCKED_FAILED_BREAKOUT": f"실패 돌파 주의, 신규 금지 또는 축소 검토: {primary_condition}",
                "PRE_OPEN_THESIS_ONLY": f"장 시작 전 thesis only: {primary_condition}",
                "NO_LIVE_DATA": f"live data 미확보: {primary_condition}",
                "STALE_TRIGGERABLE": f"전략 후보 유지, live 실행은 보류: {primary_condition}",
            }
            close_map = {
                "PILOT_READY": f"종가에 유지 확인 후 add 검토: {primary_condition}",
                "CLOSE_CONFIRM_PENDING": f"종가 기준 {primary_condition} 유지 시 본격 add 검토",
                "CLOSE_CONFIRMED": f"종가 기준 {primary_condition} 유지 시 본격 add 검토",
                "FAILED_BREAKOUT": "종가에도 약하면 축소 우선 검토",
                "PILOT_BLOCKED_FAILED_BREAKOUT": "종가에도 약하면 축소 우선 검토",
            }
            today_action = today_map.get(timing_state)
            close_action = close_map.get(timing_state)
            if not today_action:
                if delayed_analysis_only:
                    today_action = f"조건부 관찰: {primary_condition}"
                elif display_state == "ACTIONABLE_NOW":
                    today_action = f"오늘 바로 검토: {primary_condition}"
                elif display_state == "TRIGGERED_PENDING_CLOSE":
                    today_action = f"장중 조건 진입, 종가 확인 대기: {primary_condition}"
                elif stance == "BULLISH" and entry_action in {"WAIT", "STARTER", "ADD"}:
                    today_action = f"추격 매수보다 조건 확인 우선: {primary_condition}"
                elif stance == "BEARISH" or entry_action == "EXIT":
                    today_action = f"위험 조건 확인 후 축소 검토: {primary_condition}"
                else:
                    today_action = f"보유/관찰 유지: {primary_condition}"
            if not close_action:
                close_action = (
                    f"종가 기준 {primary_condition} 이탈 시 축소 검토"
                    if stance == "BEARISH" or entry_action == "EXIT"
                    else f"종가에서 {primary_condition} 재확인"
                )
    else:
        if raw_timing_state == "LIVE_BREAKOUT":
            today_action = f"Live breakout zone entered: {primary_condition}"
            close_action = f"Recheck at close before adding size: {primary_condition}"
        elif raw_timing_state == "CLOSE_CONFIRM":
            today_action = f"Intraday trigger seen; confirm close: {primary_condition}"
            close_action = f"Add only if the close confirms: {primary_condition}"
        else:
            today_map = {
                "PILOT_READY": f"Small pilot allowed intraday: {primary_condition}",
                "PILOT_BLOCKED_VOLUME": f"Price triggered but volume confirmation is still missing: {primary_condition}",
                "CLOSE_CONFIRM_PENDING": f"Trigger seen; wait for the close: {primary_condition}",
                "CLOSE_CONFIRMED": f"Trigger seen; wait for the close: {primary_condition}",
                "FAILED_BREAKOUT": f"Failed breakout risk; avoid fresh buys and review trims: {primary_condition}",
                "PILOT_BLOCKED_FAILED_BREAKOUT": f"Failed breakout risk; avoid fresh buys and review trims: {primary_condition}",
                "PRE_OPEN_THESIS_ONLY": f"Pre-open thesis only: {primary_condition}",
                "NO_LIVE_DATA": f"No live data yet: {primary_condition}",
                "STALE_TRIGGERABLE": f"Strategic candidate remains valid, but live execution is blocked: {primary_condition}",
            }
            close_map = {
                "PILOT_READY": f"Recheck at close before adding size: {primary_condition}",
                "CLOSE_CONFIRM_PENDING": f"Add only if the close confirms: {primary_condition}",
                "CLOSE_CONFIRMED": f"Add only if the close confirms: {primary_condition}",
                "FAILED_BREAKOUT": "If weakness persists into the close, prioritize trims",
                "PILOT_BLOCKED_FAILED_BREAKOUT": "If weakness persists into the close, prioritize trims",
            }
            today_action = today_map.get(timing_state)
            close_action = close_map.get(timing_state)
            if not today_action:
                if delayed_analysis_only:
                    today_action = f"Delayed analysis only; monitor condition: {primary_condition}"
                elif display_state == "ACTIONABLE_NOW":
                    today_action = f"Review now: {primary_condition}"
                elif display_state == "TRIGGERED_PENDING_CLOSE":
                    today_action = f"Intraday trigger seen; confirm close: {primary_condition}"
                elif stance == "BULLISH" and entry_action in {"WAIT", "STARTER", "ADD"}:
                    today_action = f"Wait for confirmation: {primary_condition}"
                elif stance == "BEARISH" or entry_action == "EXIT":
                    today_action = f"Review risk before reducing: {primary_condition}"
                else:
                    today_action = f"Hold or watch: {primary_condition}"
            if not close_action:
                close_action = f"Recheck at close: {primary_condition}"

    caveats: list[str] = []
    if delayed_analysis_only:
        caveats.append("지연 데이터이며 실시간 실행용은 아닙니다" if korean else "quotes are delayed and not execution-ready")
    if stale_or_degraded:
        caveats.append(
            "장중 데이터가 stale/degraded라 종가 확인을 우선합니다"
            if korean
            else "intraday data is stale/degraded; prioritize close confirmation"
        )
    if bool(_execution_payload(ticker_summary).get("review_required")) or bool(ticker_summary.get("review_required")):
        caveats.append("사람 검토 필요" if korean else "manual review required")
    if caveats:
        today_action = f"{today_action}. {' / '.join(caveats)}."

    portfolio_today_action = _portfolio_today_action(portfolio_action, language=language)
    if portfolio_today_action:
        if caveats:
            portfolio_today_action = f"{portfolio_today_action}. {' / '.join(caveats)}."
        today_action = portfolio_today_action
    portfolio_close_action = _portfolio_close_action(portfolio_action, language=language)
    if portfolio_close_action:
        close_action = portfolio_close_action
    lift_today_action = _action_lift_today_action(action_lift, language=language)
    if lift_today_action:
        today_action = lift_today_action

    return {
        "investment_view": account_execution_view or research_view,
        "investment_view_label": (
            ("계좌 실행 판단" if account_execution_view else "투자판단")
            if korean
            else ("Account action" if account_execution_view else "Investment view")
        ),
        "research_view": research_view,
        "today_action": today_action,
        "intraday_pilot_action": _intraday_pilot_rule_summary(
            ticker_summary,
            primary_condition=primary_condition,
            language=language,
        ),
        "close_action": close_action,
        "next_day_action": _next_day_followthrough_summary(
            ticker_summary,
            primary_condition=primary_condition,
            language=language,
        ),
        "key_levels": _key_levels_summary(ticker_summary, primary_condition=primary_condition, language=language),
        "risk_summary": _risk_summary(ticker_summary, language=language),
        "why_this_ticker": _why_this_ticker_summary(ticker_summary, language=language),
        "research_basis": _research_basis_label(ticker_summary, language=language),
        "execution_basis": _execution_basis_label(ticker_summary, language=language),
        "basis_asof": _basis_asof_label(ticker_summary, language=language),
    }

    manifest = manifest or {}
    language = language or _manifest_language(manifest)
    korean = language.lower().startswith("korean")
    primary_condition = _decision_primary_condition(ticker_summary.get("decision"), language=language)
    if primary_condition in {"", "-", "None", "없음"}:
        primary_condition = "조건 확인" if korean else "confirmation"
    display_state = _execution_display_state(ticker_summary, stale_after_seconds=stale_after_seconds)
    timing_state = _normalize_execution_timing_state(_execution_payload(ticker_summary).get("execution_timing_state"))
    stale_or_degraded = _is_stale_or_degraded(ticker_summary, stale_after_seconds=stale_after_seconds)
    execution_quality = _ticker_execution_data_quality(ticker_summary)
    delayed_analysis_only = execution_quality == DELAYED_ANALYSIS_ONLY
    stance = _decision_structured_value(ticker_summary.get("decision"), "portfolio_stance").upper()
    entry_action = _decision_structured_value(ticker_summary.get("decision"), "entry_action").upper()

    if korean:
        if delayed_analysis_only:
            today_action = f"조건부 관찰: {primary_condition}"
        elif timing_state == "LIVE_BREAKOUT":
            today_action = f"장중 기준 돌파 구간 진입: {primary_condition}"
        elif timing_state == "CLOSE_CONFIRM":
            today_action = f"장중 조건 진입, 종가 확인 대기: {primary_condition}"
        elif display_state == "ACTIONABLE_NOW":
            today_action = f"오늘 바로 검토: {primary_condition}"
        elif display_state == "TRIGGERED_PENDING_CLOSE":
            today_action = f"장중 조건 진입, 종가 확인 대기: {primary_condition}"
        elif stance == "BULLISH" and entry_action in {"WAIT", "STARTER", "ADD"}:
            today_action = f"추격 매수보다 조건 확인 우선: {primary_condition}"
        elif stance == "BEARISH" or entry_action == "EXIT":
            today_action = f"위험 조건 확인 후 축소 검토: {primary_condition}"
        else:
            today_action = f"보유/관찰 유지: {primary_condition}"
        caveats: list[str] = []
        if delayed_analysis_only:
            caveats.append("실시간 실행용 시세가 아니라 지연 분석용입니다")
        if stale_or_degraded:
            caveats.append("다만 장중 데이터가 stale/degraded라 종가 확인을 우선합니다")
        if bool(_execution_payload(ticker_summary).get("review_required")) or bool(ticker_summary.get("review_required")):
            caveats.append("사람 검토 필요")
        if caveats:
            today_action = f"{today_action}. {' / '.join(caveats)}."

        if timing_state == "LIVE_BREAKOUT":
            close_action = f"종가 확인 후 추가 검토: {primary_condition}"
        elif timing_state == "CLOSE_CONFIRM":
            close_action = f"종가 기준 {primary_condition} 유지 시 실행 검토"
        elif stance == "BULLISH":
            close_action = f"종가 기준 {primary_condition} 충족 시 추가 검토"
        elif stance == "BEARISH" or entry_action == "EXIT":
            close_action = f"종가 기준 {primary_condition} 이탈 시 축소 검토"
        else:
            close_action = f"종가에서 {primary_condition} 재확인"
    else:
        if delayed_analysis_only:
            today_action = f"Delayed analysis only; monitor condition: {primary_condition}"
        elif timing_state == "LIVE_BREAKOUT":
            today_action = f"Live breakout zone entered: {primary_condition}"
        elif timing_state == "CLOSE_CONFIRM":
            today_action = f"Intraday trigger seen; confirm close: {primary_condition}"
        elif display_state == "ACTIONABLE_NOW":
            today_action = f"Review now: {primary_condition}"
        elif display_state == "TRIGGERED_PENDING_CLOSE":
            today_action = f"Intraday trigger seen; confirm close: {primary_condition}"
        elif stance == "BULLISH" and entry_action in {"WAIT", "STARTER", "ADD"}:
            today_action = f"Wait for confirmation: {primary_condition}"
        elif stance == "BEARISH" or entry_action == "EXIT":
            today_action = f"Review risk before reducing: {primary_condition}"
        else:
            today_action = f"Hold or watch: {primary_condition}"
        caveats = []
        if delayed_analysis_only:
            caveats.append("quotes are delayed and not execution-ready")
        if stale_or_degraded:
            caveats.append("intraday data is stale/degraded; prioritize close confirmation")
        if bool(_execution_payload(ticker_summary).get("review_required")) or bool(ticker_summary.get("review_required")):
            caveats.append("manual review required")
        if caveats:
            today_action = f"{today_action}. {' / '.join(caveats)}."
        close_action = f"Recheck at close: {primary_condition}"

    return {
        "investment_view": present_investment_view(ticker_summary.get("decision") or ticker_summary.get("error"), language=language),
        "today_action": today_action,
        "intraday_pilot_action": _intraday_pilot_rule_summary(
            ticker_summary,
            primary_condition=primary_condition,
            language=language,
        ),
        "close_action": close_action,
        "next_day_action": _next_day_followthrough_summary(
            ticker_summary,
            primary_condition=primary_condition,
            language=language,
        ),
        "key_levels": _key_levels_summary(ticker_summary, primary_condition=primary_condition, language=language),
        "risk_summary": _risk_summary(ticker_summary, language=language),
        "why_this_ticker": _why_this_ticker_summary(ticker_summary, language=language),
        "research_basis": _research_basis_label(ticker_summary, language=language),
        "execution_basis": _execution_basis_label(ticker_summary, language=language),
        "basis_asof": _basis_asof_label(ticker_summary, language=language),
    }


def _is_stale_or_degraded(ticker_summary: dict[str, Any], *, stale_after_seconds: int) -> bool:
    display_state = _execution_display_state(ticker_summary, stale_after_seconds=stale_after_seconds).lower()
    if "stale" in display_state or "degraded" in display_state:
        return True
    quality_flags = {str(item).strip().lower() for item in (ticker_summary.get("quality_flags") or [])}
    return "stale_market_data" in quality_flags


def _ticker_execution_data_quality(ticker_summary: dict[str, Any]) -> str:
    payload = _execution_payload(ticker_summary)
    source = payload.get("source") if isinstance(payload.get("source"), dict) else {}
    quality = str(source.get("execution_data_quality") or payload.get("execution_data_quality") or "").strip().upper()
    if quality in {REALTIME_EXECUTION_READY, DELAYED_ANALYSIS_ONLY, STALE_INVALID_FOR_EXECUTION}:
        return quality
    if source.get("provider_realtime_capable") is False:
        return DELAYED_ANALYSIS_ONLY
    return ""


def _research_basis_label(ticker_summary: dict[str, Any], *, language: str) -> str:
    trade_date = ticker_summary.get("trade_date") or ticker_summary.get("analysis_date") or "-"
    if language.lower().startswith("korean"):
        return f"리서치 본문은 {trade_date} 일봉 기준"
    return f"Research text uses daily data through {trade_date}"


def _execution_basis_label(ticker_summary: dict[str, Any], *, language: str) -> str:
    execution_asof = _execution_value(ticker_summary, "execution_asof", default="")
    if execution_asof:
        if _ticker_execution_data_quality(ticker_summary) == DELAYED_ANALYSIS_ONLY:
            if language.lower().startswith("korean"):
                return f"지연 분석용 intraday snapshot({execution_asof}) 기준; 실시간 실행 신호 아님"
            return f"Delayed analysis-only intraday snapshot at {execution_asof}; not execution-ready"
        if language.lower().startswith("korean"):
            return f"실행 오버레이는 {execution_asof} 장중 스냅샷 기준"
        return f"Execution overlay uses intraday snapshot at {execution_asof}"
    if language.lower().startswith("korean"):
        return "장중 실행 스냅샷 미갱신"
    return "Intraday execution snapshot not refreshed"


def _basis_asof_label(ticker_summary: dict[str, Any], *, language: str) -> str:
    if language.lower().startswith("korean"):
        return f"{ticker_summary.get('analysis_date') or '-'} 분석 / {ticker_summary.get('trade_date') or '-'} 거래일"
    return f"Analysis {ticker_summary.get('analysis_date') or '-'} / trade date {ticker_summary.get('trade_date') or '-'}"


def _intraday_pilot_rule_summary(
    ticker_summary: dict[str, Any],
    *,
    primary_condition: str,
    language: str,
) -> str:
    levels = _execution_levels_payload(ticker_summary)
    rule = str(levels.get("intraday_pilot_rule") or "").strip()
    if rule:
        return sanitize_investor_text(rule, language=language)
    if language.lower().startswith("korean"):
        return f"10:30 이후 {primary_condition} + VWAP 위 + 거래량 확인 시 소액 starter만 검토"
    return f"After 10:30, consider only a small starter if {primary_condition}, VWAP, and volume confirm"


def _next_day_followthrough_summary(
    ticker_summary: dict[str, Any],
    *,
    primary_condition: str,
    language: str,
) -> str:
    levels = _execution_levels_payload(ticker_summary)
    rule = str(levels.get("next_day_followthrough_rule") or "").strip()
    if rule:
        return sanitize_investor_text(rule, language=language)
    if language.lower().startswith("korean"):
        return f"다음 거래일 첫 30~60분 동안 {primary_condition} 재이탈이 없는지 확인"
    return f"Next session: require no loss of {primary_condition} during the first 30-60 minutes"


def _why_this_ticker_summary(ticker_summary: dict[str, Any], *, language: str) -> str:
    try:
        parsed = parse_structured_decision(ticker_summary.get("decision"))
    except Exception:
        return "근거 요약 생성 실패: 원문은 투자자 화면에서 숨깁니다." if language.lower().startswith("korean") else "Rationale unavailable"
    candidates = [*parsed.catalysts, parsed.entry_logic]
    for item in candidates:
        text = sanitize_investor_text(item, language=language)
        if text and text not in {"-", "None", "없음"}:
            return text
    return "조건 충족 전까지 관찰합니다." if language.lower().startswith("korean") else "Watch until the setup confirms"


def _execution_levels_payload(ticker_summary: dict[str, Any]) -> dict[str, Any]:
    contract = _execution_contract_payload(ticker_summary)
    levels = contract.get("execution_levels")
    return levels if isinstance(levels, dict) else {}


def _key_levels_summary(
    ticker_summary: dict[str, Any],
    *,
    primary_condition: str,
    language: str,
) -> str:
    contract = _execution_contract_payload(ticker_summary)
    if not contract:
        return primary_condition
    parts: list[str] = []
    breakout = contract.get("breakout_level")
    if breakout is not None:
        parts.append(f"돌파 확인선 {_format_level(breakout)}")
    zone = contract.get("pullback_buy_zone")
    if isinstance(zone, dict) and zone.get("low") is not None and zone.get("high") is not None:
        parts.append(f"눌림 매수 구간 {_format_level(zone.get('low'))}~{_format_level(zone.get('high'))}")
    invalid_close = contract.get("invalid_if_close_below")
    invalid_intraday = contract.get("invalid_if_intraday_below")
    invalid = invalid_close if invalid_close is not None else invalid_intraday
    if invalid is not None:
        parts.append(f"무효화 가격 {_format_level(invalid)}")
    volume = contract.get("min_relative_volume")
    if volume is not None:
        parts.append(f"거래량 확인선 {volume}배")
    if not parts:
        return primary_condition
    return " / ".join(parts)


def _risk_summary(ticker_summary: dict[str, Any], *, language: str) -> str:
    try:
        parsed = parse_structured_decision(ticker_summary.get("decision"))
    except Exception:
        return "위험 조건 확인 필요" if language.lower().startswith("korean") else "Risk checks needed"
    invalidators = [str(item).strip() for item in parsed.invalidators if str(item).strip()]
    if invalidators:
        return sanitize_investor_text(invalidators[0], language=language)
    if parsed.portfolio_stance.value == "BEARISH" or parsed.entry_action.value == "EXIT":
        return "약세 신호가 이어지면 축소 우선" if language.lower().startswith("korean") else "Reduce if bearish signal persists"
    return "핵심 조건 이탈 전까지 관찰" if language.lower().startswith("korean") else "Watch unless key levels fail"


def _execution_contract_payload(ticker_summary: dict[str, Any]) -> dict[str, Any]:
    payload = ticker_summary.get("execution_contract")
    return payload if isinstance(payload, dict) else {}


def _format_level(value: Any) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if numeric.is_integer():
        return f"{int(numeric):,}"
    return f"{numeric:,.2f}"


def _advanced_diagnostics_html(
    ticker_summary: dict[str, Any],
    manifest: dict[str, Any],
    *,
    stale_after_seconds: int,
    compact: bool = False,
) -> str:
    # Public investor pages intentionally omit operator/debug diagnostics.
    return ""


def _download_details_html(links: list[str], *, summary: str, empty_text: str) -> str:
    return f"""
    <section class="section downloads">
      <details>
        <summary>{_escape(summary)}</summary>
        <div class="pill-row">
          {''.join(links) if links else f"<span class='empty'>{_escape(empty_text)}</span>"}
        </div>
      </details>
    </section>
    """


def _execution_payload(ticker_summary: dict[str, Any]) -> dict[str, Any]:
    payload = ticker_summary.get("execution_update")
    return payload if isinstance(payload, dict) else {}


def _normalize_execution_timing_state(value: Any) -> str:
    state = str(value or "").strip().upper()
    return {
        "LIVE_BREAKOUT": "PILOT_READY",
        "ACTIONABLE_LIVE": "PILOT_READY",
        "LATE_SESSION_CONFIRM": "CLOSE_CONFIRM_PENDING",
        "CLOSE_CONFIRM": "CLOSE_CONFIRM_PENDING",
    }.get(state, state or "WAITING")


def _execution_stale_threshold_seconds(manifest: dict[str, Any]) -> int:
    settings = manifest.get("settings") or {}
    raw = settings.get("execution_max_data_age_seconds")
    try:
        return max(int(raw), 30)
    except Exception:
        return 180


def _execution_value(ticker_summary: dict[str, Any], key: str, *, default: str) -> str:
    payload = _execution_payload(ticker_summary)
    value = payload.get(key)
    return default if value in (None, "") else str(value)


def _execution_staleness(ticker_summary: dict[str, Any]) -> str:
    payload = _execution_payload(ticker_summary)
    value = payload.get("staleness_seconds")
    if value is None:
        return "not refreshed"
    try:
        seconds = int(value)
    except Exception:
        return f"{value}s"
    if seconds < 60:
        return f"{seconds}s"
    minutes, remainder = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {remainder}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m {remainder}s"


def _execution_badge_label(ticker_summary: dict[str, Any]) -> str:
    payload = _execution_payload(ticker_summary)
    if payload:
        return "Intraday refreshed"
    return "PRE_OPEN SNAPSHOT"


def _execution_display_state(ticker_summary: dict[str, Any], *, stale_after_seconds: int = 180) -> str:
    payload = _execution_payload(ticker_summary)
    if not payload:
        return "WAIT (not refreshed)"
    state = str(payload.get("decision_state") or "WAIT")
    reason_codes = {str(item) for item in (payload.get("reason_codes") or [])}
    data_health = str(payload.get("data_health") or "").upper()
    if state == "DEGRADED" and ("stale_market_data" in reason_codes or data_health == "STALE"):
        return "DEGRADED (stale market data)"
    staleness = payload.get("staleness_seconds")
    try:
        stale = int(staleness) > max(int(stale_after_seconds), 0)
    except Exception:
        stale = False
    if stale and state == "ACTIONABLE_NOW":
        return "WAIT (stale overlay)"
    return state


def _execution_timing_state_label(ticker_summary: dict[str, Any]) -> str:
    state = _normalize_execution_timing_state(_execution_payload(ticker_summary).get("execution_timing_state"))
    labels = {
        "WAITING": "Waiting",
        "NO_LIVE_DATA": "No live data",
        "PRE_OPEN_THESIS_ONLY": "Pre-open thesis only",
        "PILOT_READY": "Pilot ready",
        "PILOT_BLOCKED_VOLUME": "Pilot blocked by volume",
        "PILOT_BLOCKED_FAILED_BREAKOUT": "Pilot blocked by failed breakout",
        "CLOSE_CONFIRM_PENDING": "Close confirm pending",
        "CLOSE_CONFIRMED": "Close confirmed",
        "NEXT_DAY_FOLLOWTHROUGH_PENDING": "Next day follow-through",
        "FAILED_BREAKOUT": "Failed breakout",
        "SUPPORT_HOLD": "Support hold",
        "SUPPORT_FAIL": "Support fail",
        "STALE_TRIGGERABLE": "Stale triggerable",
        "INVALIDATED": "Invalidated",
        "DEGRADED": "Degraded",
    }
    return labels.get(state, state.title().replace("_", " "))

    state = str(_execution_payload(ticker_summary).get("execution_timing_state") or "").upper()
    mapping = {
        "WAITING": "대기",
        "LIVE_BREAKOUT": "장중 돌파",
        "FAILED_BREAKOUT": "실패 돌파",
        "SUPPORT_HOLD": "지지 확인",
        "SUPPORT_FAIL": "지지 이탈",
        "LATE_SESSION_CONFIRM": "막판 종가 확인",
        "STALE_TRIGGERABLE": "전략 후보 유지",
        "CLOSE_CONFIRM": "종가 확인",
        "ACTIONABLE_LIVE": "장중 실행 가능",
        "INVALIDATED": "무효화",
        "DEGRADED": "자료 저하",
    }
    return mapping.get(state, "미분류")


def _today_summary(
    ticker_summary: dict[str, Any],
    *,
    language: str,
    stale_after_seconds: int = 180,
) -> str:
    payload = _execution_payload(ticker_summary)
    timing_state = _normalize_execution_timing_state(payload.get("execution_timing_state")) if payload else "WAITING"
    is_korean = language.lower().startswith("korean")
    if timing_state in {
        "PILOT_READY",
        "PILOT_BLOCKED_VOLUME",
        "PILOT_BLOCKED_FAILED_BREAKOUT",
        "FAILED_BREAKOUT",
        "CLOSE_CONFIRM_PENDING",
        "CLOSE_CONFIRMED",
        "PRE_OPEN_THESIS_ONLY",
        "NO_LIVE_DATA",
        "STALE_TRIGGERABLE",
    } and payload:
        return _ticker_investor_summary(
            ticker_summary,
            {},
            language=language,
            stale_after_seconds=stale_after_seconds,
        )["today_action"].split(".")[0]
    if not payload:
        return "장 시작 전 스냅샷, 장중 데이터 대기" if is_korean else "Pre-open snapshot; waiting for intraday refresh"

    review_required = bool(payload.get("review_required")) or bool(ticker_summary.get("review_required"))
    decision_source = str(payload.get("decision_source") or ticker_summary.get("decision_source") or "").upper()
    decision_state = str(payload.get("decision_state") or "").upper()
    if review_required:
        return "검토 필요 플래그로 수동 검토 우선" if is_korean else "Manual review required before action"
    if "RULE_ONLY_FALLBACK" in decision_source:
        return "규칙 기반 대체 판단, 데이터 재확인 필요" if is_korean else "Rule fallback; verify data before action"
    if decision_state == "DEGRADED":
        summary = _ticker_investor_summary(
            ticker_summary,
            {},
            language=language,
            stale_after_seconds=stale_after_seconds,
        )["today_action"]
        return f"보수적 관찰: {summary}" if is_korean else f"Conservative watch: {summary}"
    if decision_state == "ACTIONABLE_NOW":
        return "오늘 바로 검토" if language.lower().startswith("korean") else "Review now"
    if decision_state == "TRIGGERED_PENDING_CLOSE":
        return "종가 확인 필요" if language.lower().startswith("korean") else "Await close confirmation"
    display_state = _execution_display_state(ticker_summary, stale_after_seconds=stale_after_seconds)
    if display_state == "WAIT (stale overlay)":
        return _ticker_investor_summary(
            ticker_summary,
            {},
            language=language,
            stale_after_seconds=stale_after_seconds,
        )["today_action"]
    stance = _decision_structured_value(ticker_summary.get("decision"), "portfolio_stance").upper()
    entry_action = _decision_structured_value(ticker_summary.get("decision"), "entry_action").upper()
    if stance == "BULLISH" and entry_action == "WAIT":
        return _ticker_investor_summary(
            ticker_summary,
            {},
            language=language,
            stale_after_seconds=stale_after_seconds,
        )["today_action"]
    if stance in {"NEUTRAL", "BULLISH"} and entry_action in {"WAIT", "NONE"}:
        return "보유 유지, 조건 충족 시 추가 검토" if language.lower().startswith("korean") else "Hold and add if triggered"
    return present_action_summary(ticker_summary.get("decision"), language=language)


def _decision_structured_value(raw_decision: Any, field: str) -> str:
    try:
        parsed = parse_structured_decision(raw_decision)
    except Exception:
        return "-"
    value = getattr(parsed, field, None)
    if hasattr(value, "value"):
        return str(value.value)
    return str(value or "-")


def _decision_source_label(ticker_summary: dict[str, Any]) -> str:
    payload = _execution_payload(ticker_summary)
    return str(payload.get("decision_source") or ticker_summary.get("decision_source") or "analysis")


def _analysis_review_required_label(ticker_summary: dict[str, Any]) -> str:
    value = ticker_summary.get("review_required")
    return "yes" if bool(value) else "no"


def _portfolio_review_required_label(ticker_summary: dict[str, Any]) -> str:
    payload = _execution_payload(ticker_summary)
    value = payload.get("review_required")
    return "yes" if bool(value) else "no"


def _analysis_asof_label(ticker_summary: dict[str, Any]) -> str:
    value = ticker_summary.get("finished_at") or ticker_summary.get("started_at")
    return str(value or "-")


def _published_at_label(manifest: dict[str, Any]) -> str:
    value = manifest.get("finished_at") or manifest.get("started_at")
    return str(value or "-")


def _historical_view_label(manifest: dict[str, Any]) -> str:
    published_raw = manifest.get("finished_at") or manifest.get("started_at")
    if not published_raw:
        return "unknown"
    try:
        published_at = _parse_iso_datetime(str(published_raw))
    except ValueError:
        return "unknown"
    age_seconds = (datetime.now(timezone.utc) - published_at.astimezone(timezone.utc)).total_seconds()
    return "yes" if age_seconds >= 6 * 3600 else "no"


def _parse_iso_datetime(value: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError("missing datetime")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _trigger_summary(ticker_summary: dict[str, Any], *, language: str, stale_after_seconds: int = 180) -> str:
    key = _decision_primary_condition(ticker_summary.get("decision"), language=language)
    state = _execution_display_state(ticker_summary, stale_after_seconds=stale_after_seconds)
    return f"{state} · {key}"


def _portfolio_status_label(status: str) -> str:
    normalized = str(status or "").strip().lower()
    mapping = {
        "success": "Ready",
        "watchlist_only": "Watchlist only",
        "capital_constrained": "Cash constrained",
        "degraded": "Needs review",
        "failed": "Failed",
        "failure": "Failed",
        "disabled": "Disabled",
    }
    return mapping.get(normalized, normalized.replace("_", " ").title() if normalized else "Unknown")


def _portfolio_report_label(portfolio_summary: dict[str, Any]) -> str:
    status = str(portfolio_summary.get("status") or "").strip().lower()
    snapshot_health = str(portfolio_summary.get("snapshot_health") or "").strip().upper()
    if status == "watchlist_only" or snapshot_health == "WATCHLIST_ONLY":
        return "Watchlist report"
    return "Account report"


def _ticker_display_label(ticker_summary: dict[str, Any]) -> str:
    ticker = str(ticker_summary.get("ticker") or "").strip()
    ticker_name = str(ticker_summary.get("ticker_name") or "").strip()
    if ticker_name and ticker and ticker_name.upper() != ticker.upper():
        return f"{ticker_name} ({ticker})"
    return ticker_name or ticker or "-"


def _load_portfolio_summary(run_dir: Path) -> dict[str, Any]:
    private_dir = run_dir / "portfolio-private"
    status_path = private_dir / "status.json"
    if not status_path.exists():
        return {}

    payload = json.loads(status_path.read_text(encoding="utf-8"))
    report_md = private_dir / "portfolio_report.md"
    report_json = private_dir / "portfolio_report.json"
    candidates_json = private_dir / "portfolio_candidates.json"
    action_lift_json = private_dir / "action_lift_audit.json"
    portfolio_action_lift_json = private_dir / "portfolio_action_lift_audit.json"
    summary_svg = private_dir / "summary_card.svg"
    summary_png = private_dir / "summary_card_ai.png"
    summary_spec = private_dir / "summary_image_spec.json"
    summary_metadata = private_dir / "summary_image_metadata.json"
    account_performance_public = private_dir / "account_performance_public.json"
    account_performance_chart_data = private_dir / "account_performance_chart_data.json"
    account_performance_report_md = private_dir / "account_performance_report.md"
    etf_dca_comparison = private_dir / "etf_dca_comparison.json"
    etf_dca_policy = private_dir / "etf_dca_policy_recommendation.json"
    etf_alt_public = private_dir / "etf_alternative_portfolios_public.json"
    private_download_names = {
        "etf_alternative_portfolios_raw.json",
        "etf_dca_cashflows.json",
        "cashflows.json",
        "cashflows_audit.json",
        "etf_dca_benchmark_transactions.json",
        "etf_dca_equity_curves.json",
    }
    files = sorted(path for path in private_dir.iterdir() if path.is_file() and path.name not in private_download_names)
    candidate_symbols: list[str] = []
    candidate_pairs: list[dict[str, str]] = []
    sell_side_counts: dict[str, Any] = {}
    actions_by_ticker: dict[str, dict[str, Any]] = {}
    action_lift_by_ticker: dict[str, dict[str, Any]] = {}
    account_performance: dict[str, Any] = {}
    if report_json.exists():
        try:
            report_payload = json.loads(report_json.read_text(encoding="utf-8"))
            sell_side_counts = (
                (report_payload.get("data_health_summary") or {}).get("sell_side_distribution")
                or report_payload.get("candidate_counts")
                or {}
            )
            for action in report_payload.get("actions") or []:
                if not isinstance(action, dict):
                    continue
                ticker = str(action.get("canonical_ticker") or "").strip()
                if ticker:
                    actions_by_ticker[ticker] = action
        except Exception:
            sell_side_counts = {}
            actions_by_ticker = {}
    lift_source_json = action_lift_json if action_lift_json.exists() else portfolio_action_lift_json
    if lift_source_json.exists():
        try:
            lift_payload = json.loads(lift_source_json.read_text(encoding="utf-8"))
            for entry in lift_payload.get("entries") or []:
                if not isinstance(entry, dict):
                    continue
                ticker = str(entry.get("ticker") or "").strip()
                if ticker:
                    action_lift_by_ticker[ticker] = entry
        except Exception:
            action_lift_by_ticker = {}
    if candidates_json.exists():
        try:
            payload_candidates = json.loads(candidates_json.read_text(encoding="utf-8"))
            for candidate in (payload_candidates.get("candidates") or []):
                if not isinstance(candidate, dict):
                    continue
                instrument = candidate.get("instrument") or {}
                symbol = instrument.get("canonical_ticker") or candidate.get("canonical_ticker")
                broker_symbol = instrument.get("broker_symbol") or candidate.get("broker_symbol")
                if symbol:
                    candidate_symbols.append(str(symbol))
                if symbol or broker_symbol:
                    candidate_pairs.append(
                        {
                            "broker_symbol": str(broker_symbol or ""),
                            "canonical_ticker": str(symbol or ""),
                        }
                    )
        except Exception:
            candidate_symbols = []
    if account_performance_public.exists():
        try:
            parsed = json.loads(account_performance_public.read_text(encoding="utf-8"))
            if isinstance(parsed, dict):
                account_performance = _normalize_account_performance_payload(parsed)
        except Exception:
            account_performance = {}
    return {
        "status_path": status_path,
        "status": str(payload.get("status") or "unknown"),
        "status_class": _status_class(str(payload.get("status") or "unknown")),
        "profile": payload.get("profile"),
        "snapshot_health": payload.get("snapshot_health"),
        "generated_at": payload.get("generated_at"),
        "semantic_health": payload.get("semantic_health") if isinstance(payload, dict) else {},
        "external_signals": payload.get("external_signals") if isinstance(payload, dict) else {},
        "error": payload.get("error"),
        "portfolio_report_md": report_md if report_md.exists() else None,
        "portfolio_report_json": report_json if report_json.exists() else None,
        "action_lift_audit_json": action_lift_json if action_lift_json.exists() else None,
        "portfolio_action_lift_audit_json": portfolio_action_lift_json if portfolio_action_lift_json.exists() else None,
        "summary_image_svg": summary_svg if summary_svg.exists() else None,
        "summary_image_png": summary_png if summary_png.exists() else None,
        "summary_image_spec_json": summary_spec if summary_spec.exists() else None,
        "summary_image_metadata_json": summary_metadata if summary_metadata.exists() else None,
        "account_performance": account_performance,
        "account_performance_public_json": account_performance_public if account_performance_public.exists() else None,
        "account_performance_chart_data_json": account_performance_chart_data if account_performance_chart_data.exists() else None,
        "account_performance_report_md": account_performance_report_md if account_performance_report_md.exists() else None,
        "etf_dca_comparison_json": etf_dca_comparison if etf_dca_comparison.exists() else None,
        "etf_dca_policy_recommendation_json": etf_dca_policy if etf_dca_policy.exists() else None,
        "etf_alternative_portfolios_public_json": etf_alt_public if etf_alt_public.exists() else None,
        "candidate_canonical_symbols": candidate_symbols,
        "candidate_identity_pairs": candidate_pairs,
        "sell_side_counts": sell_side_counts,
        "actions_by_ticker": actions_by_ticker,
        "action_lift_by_ticker": action_lift_by_ticker,
        "downloadable_files": files,
        "artifact_count": len(files),
    }


def _load_execution_summary(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "execution_summary.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _render_execution_summary_section(summary: dict[str, Any]) -> str:
    # Execution overlay raw state is useful for debugging, not for the investor report.
    return ""


def _status_class(status: str) -> str:
    normalized = (status or "").strip().lower()
    if normalized == "success":
        return "success"
    if normalized in {"watchlist_only", "capital_constrained", "degraded"}:
        return "partial_failure"
    if normalized in {"failed", "failure"}:
        return "failed"
    return "pending"


def _render_run_health_section(manifest: dict[str, Any], portfolio_summary: dict[str, Any]) -> str:
    # Suppress engineering health diagnostics from investor-facing pages.
    return ""


def _select_representative_run(manifests: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not manifests:
        return None
    target = manifests[0]
    target_market = _manifest_market(target)
    target_family = _manifest_run_family(target)
    ranked_pool = [
        manifest
        for manifest in manifests
        if _manifest_market(manifest) == target_market and _manifest_run_family(manifest) == target_family
    ]
    if not ranked_pool:
        ranked_pool = [manifest for manifest in manifests if _manifest_market(manifest) == target_market]
    if not ranked_pool:
        ranked_pool = list(manifests)
    qualified = [manifest for manifest in ranked_pool if _representative_run_quality_gate(manifest)]
    if qualified:
        ranked_pool = qualified
    ranked = sorted(ranked_pool, key=_representative_run_sort_key)
    return ranked[0] if ranked else manifests[0]


def _select_latest_daily_run(manifests: list[dict[str, Any]]) -> dict[str, Any] | None:
    for manifest in manifests:
        if _is_daily_analysis_run(manifest):
            return manifest
    return None


def _is_daily_analysis_run(manifest: dict[str, Any]) -> bool:
    run_id = str(manifest.get("run_id") or "").lower()
    if "overlay" in run_id or "watchdog" in run_id:
        return False
    settings = manifest.get("settings") if isinstance(manifest.get("settings"), dict) else {}
    run_mode = str(settings.get("run_mode") or manifest.get("run_mode") or "").strip().lower()
    if run_mode in {"overlay_only", "site_only"}:
        return False
    total, successful, _failed = _run_success_counts(manifest)
    if total <= 0 or successful <= 0:
        return False
    return True


def _representative_run_sort_key(manifest: dict[str, Any]) -> tuple[int, int, int, int, int, int, str]:
    phase = _run_phase_label(manifest)
    phase_rank = {
        "regular_session": 0,
        "in_session": 0,
        "pre_open": 1,
        "post_close": 2,
        "delayed_analysis_only": 3,
        "historical_review": 4,
    }.get(phase, 5)
    stale_ratio = _run_stale_ratio(manifest)
    quality_rank = {
        REALTIME_EXECUTION_READY: 0,
        DELAYED_ANALYSIS_ONLY: 1,
        STALE_INVALID_FOR_EXECUTION: 2,
    }.get(_run_execution_data_quality(manifest), 1)
    representative_rank = _representative_run_quality_rank(manifest)
    failure_rank = int(_run_failure_ratio(manifest) * 1000)
    usefulness_rank = int(((manifest.get("run_quality") or {}).get("usefulness_rank") or manifest.get("usefulness_rank") or 100))
    started_at = str(manifest.get("started_at") or "")
    recency_bias = "".join(chr(255 - ord(ch)) if ord(ch) < 255 else ch for ch in started_at)
    return (representative_rank, phase_rank, quality_rank, failure_rank, int(stale_ratio * 1000), usefulness_rank, recency_bias)


def _representative_run_quality_gate(manifest: dict[str, Any]) -> bool:
    if not _has_portfolio_or_account_report(manifest):
        return False
    total, successful, failed = _run_success_counts(manifest)
    if total <= 0:
        return False
    success_rate = successful / total if total else 0.0
    failure_ratio = failed / total if total else 1.0
    return success_rate >= 0.90 and (failed == 0 or failure_ratio <= 0.05)


def _representative_run_quality_rank(manifest: dict[str, Any]) -> int:
    if _representative_run_quality_gate(manifest):
        return 0
    failure_ratio = _run_failure_ratio(manifest)
    if failure_ratio > 0.05:
        return 3
    if _has_portfolio_or_account_report(manifest):
        return 1
    return 2


def _run_success_counts(manifest: dict[str, Any]) -> tuple[int, int, int]:
    summary = manifest.get("summary") if isinstance(manifest.get("summary"), dict) else {}
    total = int(summary.get("total_tickers") or len(manifest.get("tickers") or []) or 0)
    failed = int(summary.get("failed_tickers") or 0)
    successful = int(summary.get("successful_tickers") or max(total - failed, 0))
    if total <= 0 and successful + failed > 0:
        total = successful + failed
    return total, successful, failed


def _run_failure_ratio(manifest: dict[str, Any]) -> float:
    total, _successful, failed = _run_success_counts(manifest)
    if total <= 0:
        return 0.0
    return failed / total


def _has_portfolio_or_account_report(manifest: dict[str, Any]) -> bool:
    portfolio = manifest.get("portfolio") if isinstance(manifest.get("portfolio"), dict) else {}
    status = str(portfolio.get("status") or "").strip().lower()
    artifacts = portfolio.get("artifacts") if isinstance(portfolio.get("artifacts"), dict) else {}
    if artifacts and any(
        key in artifacts
        for key in {
            "portfolio_report_md",
            "portfolio_report_json",
            "account_performance_public_json",
            "account_performance_chart_data_json",
        }
    ):
        return True
    return bool(portfolio) and status not in {"", "disabled", "failed"}


def _run_phase_label(manifest: dict[str, Any]) -> str:
    phase = str(manifest.get("market_session_phase") or ((manifest.get("execution") or {}).get("overlay_phase") or {}).get("name") or "").upper()
    quality = _run_execution_data_quality(manifest)
    calendar_phase = _manifest_calendar_phase(manifest)
    if phase in {"DELAYED_ANALYSIS_ONLY", "ANALYSIS_ONLY_DELAYED"}:
        return "delayed_analysis_only"
    if phase in {"IN_SESSION", "REGULAR_SESSION"} and calendar_phase in {"pre_open", "post_close", "historical_review"}:
        return calendar_phase
    if phase in {"REGULAR_SESSION", "IN_SESSION"} and quality in {DELAYED_ANALYSIS_ONLY, STALE_INVALID_FOR_EXECUTION}:
        return "delayed_analysis_only"
    if phase in {"REGULAR_SESSION"}:
        return "regular_session"
    if phase in {"HISTORICAL_REVIEW"}:
        return "historical_review"
    if phase.startswith("CHECKPOINT_") and calendar_phase in {"pre_open", "post_close", "historical_review"}:
        return calendar_phase
    if phase.startswith("CHECKPOINT_") and _run_stale_ratio(manifest) >= 0.95:
        return "delayed_analysis_only" if quality == DELAYED_ANALYSIS_ONLY else "post_close"
    if phase.startswith("CHECKPOINT_"):
        return "regular_session" if quality == REALTIME_EXECUTION_READY else "delayed_analysis_only"
    if phase in {"PRE_OPEN", "PRE-OPEN"}:
        return "pre_open"
    if phase in {"POST_RESEARCH", "AFTER_CLOSE", "POST_CLOSE"}:
        return "post_close"
    return "other"


def _manifest_calendar_phase(manifest: dict[str, Any]) -> str:
    started_at = str(manifest.get("started_at") or "").strip()
    if not started_at:
        return "unknown"
    try:
        parsed = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    except ValueError:
        return "unknown"
    market = _manifest_market(manifest).upper()
    timezone_name = "US/Eastern" if market == "US" else "Asia/Seoul"
    try:
        from zoneinfo import ZoneInfo

        local = parsed.astimezone(ZoneInfo(timezone_name)) if parsed.tzinfo else parsed.replace(tzinfo=ZoneInfo(timezone_name))
    except Exception:
        return "unknown"
    if local.weekday() == 5:
        return "post_close"
    if local.weekday() == 6:
        return "historical_review"
    current = local.time()
    if market == "US":
        pre_open = datetime.strptime("04:00", "%H:%M").time()
        open_time = datetime.strptime("09:30", "%H:%M").time()
        close_time = datetime.strptime("16:00", "%H:%M").time()
    else:
        pre_open = datetime.strptime("08:00", "%H:%M").time()
        open_time = datetime.strptime("09:00", "%H:%M").time()
        close_time = datetime.strptime("15:30", "%H:%M").time()
    if current < pre_open:
        return "historical_review"
    if current < open_time:
        return "pre_open"
    if current <= close_time:
        return "regular_session"
    return "post_close"


def _run_phase_display_label(manifest: dict[str, Any]) -> str:
    category = _run_category(manifest)
    display = {
        "LIVE_EXECUTION_READY": "Live execution ready",
        "REGULAR_SESSION_ANALYSIS": "Regular session analysis",
        "POST_CLOSE_REVIEW": "Post-close review",
        "DELAYED_ANALYSIS_ONLY": "Delayed analysis only",
        "NEXT_DAY_PLAN": "Next-day plan",
        "TECHNICAL_ARCHIVE": "Technical archive",
    }.get(category)
    if display:
        return display
    mapping = {
        "regular_session": "Regular session",
        "in_session": "Regular session",
        "delayed_analysis_only": "Delayed analysis only",
        "pre_open": "Pre open",
        "post_close": "Post close",
        "historical_review": "Historical review",
        "other": "Other",
    }
    return mapping.get(_run_phase_label(manifest), "Other")


def _run_category(manifest: dict[str, Any]) -> str:
    if _run_failure_ratio(manifest) > 0.05:
        return "TECHNICAL_ARCHIVE"
    phase = _run_phase_label(manifest)
    quality = _run_execution_data_quality(manifest)
    if phase in {"regular_session", "in_session"} and quality == REALTIME_EXECUTION_READY:
        return "LIVE_EXECUTION_READY"
    if phase in {"regular_session", "in_session"}:
        return "REGULAR_SESSION_ANALYSIS"
    if phase == "post_close":
        return "POST_CLOSE_REVIEW"
    if phase == "delayed_analysis_only":
        return "DELAYED_ANALYSIS_ONLY"
    if phase == "pre_open":
        return "NEXT_DAY_PLAN"
    return "TECHNICAL_ARCHIVE"


def _manifest_market(manifest: dict[str, Any]) -> str:
    settings = manifest.get("settings") or {}
    market = str(settings.get("market") or settings.get("market_scope") or "").strip().lower()
    if market:
        return market
    run_id = str(manifest.get("run_id") or "").lower()
    if "-us" in run_id or run_id.endswith("us"):
        return "us"
    if "-kr" in run_id or run_id.endswith("kr"):
        return "kr"
    return "unknown"


def _manifest_run_family(manifest: dict[str, Any]) -> str:
    portfolio = manifest.get("portfolio") or {}
    status = str(portfolio.get("status") or "").strip().lower()
    if portfolio and status not in {"", "disabled"}:
        return "account-aware"
    if portfolio.get("profile"):
        return "account-aware"
    return "watchlist"


def _run_execution_data_quality(manifest: dict[str, Any]) -> str:
    execution = manifest.get("execution") or {}
    quality = str(execution.get("execution_data_quality") or "").strip().upper()
    if quality in {REALTIME_EXECUTION_READY, DELAYED_ANALYSIS_ONLY, STALE_INVALID_FOR_EXECUTION}:
        return quality
    counts = execution.get("market_data_quality_counts") if isinstance(execution.get("market_data_quality_counts"), dict) else {}
    if int(counts.get(REALTIME_EXECUTION_READY) or 0) and not int(counts.get(DELAYED_ANALYSIS_ONLY) or 0) and not int(counts.get(STALE_INVALID_FOR_EXECUTION) or 0):
        return REALTIME_EXECUTION_READY
    if int(counts.get(DELAYED_ANALYSIS_ONLY) or 0):
        return DELAYED_ANALYSIS_ONLY
    if int(counts.get(STALE_INVALID_FOR_EXECUTION) or 0):
        return STALE_INVALID_FOR_EXECUTION
    for ticker in manifest.get("tickers") or []:
        update = ticker.get("execution_update") if isinstance(ticker.get("execution_update"), dict) else {}
        source = update.get("source") if isinstance(update.get("source"), dict) else {}
        source_quality = str(source.get("execution_data_quality") or update.get("execution_data_quality") or "").strip().upper()
        if source_quality in {DELAYED_ANALYSIS_ONLY, STALE_INVALID_FOR_EXECUTION}:
            return source_quality
        if source.get("provider_realtime_capable") is False:
            return DELAYED_ANALYSIS_ONLY
        try:
            quote_delay = int(source.get("quote_delay_seconds"))
        except (TypeError, ValueError):
            quote_delay = 0
        if quote_delay > _execution_stale_threshold_seconds(manifest):
            return DELAYED_ANALYSIS_ONLY
    return ""


def _run_stale_ratio(manifest: dict[str, Any]) -> float:
    execution = manifest.get("execution") or {}
    degraded = len(execution.get("degraded") or [])
    total = max(int((manifest.get("summary") or {}).get("total_tickers") or 0), 1)
    return degraded / total


def _compute_health_metrics(*, manifest: dict[str, Any], portfolio_summary: dict[str, Any]) -> dict[str, str]:
    execution = manifest.get("execution") or {}
    phase = _run_phase_label(manifest)
    degraded_count = len(execution.get("degraded") or [])
    total_tickers = max(int((manifest.get("summary") or {}).get("total_tickers") or 0), 1)
    quality = _run_execution_data_quality(manifest)
    if phase == "delayed_analysis_only":
        freshness = "delayed analysis only"
    elif quality == STALE_INVALID_FOR_EXECUTION:
        freshness = "stale invalid for execution"
    else:
        freshness = "stale-risk" if phase == "regular_session" and degraded_count > 0 else ("pre-open" if phase == "pre_open" else "ok")
    semantic_health = portfolio_summary.get("semantic_health") or {}
    fallback_ratio = float(semantic_health.get("rule_only_fallback_ratio") or 0.0)
    judge_health = "degraded" if fallback_ratio >= 0.3 else "ok"
    batch_metrics = manifest.get("batch_metrics") or {}
    coverage_ratio = batch_metrics.get("company_news_zero_ratio")
    data_coverage = (
        f"company_news_zero_ratio={coverage_ratio:.0%}" if isinstance(coverage_ratio, (float, int)) else "unknown"
    )
    identity_integrity = "ok"
    manifest_symbols_ok = not any(
        not _looks_like_symbol(str(item.get("ticker") or "")) for item in (manifest.get("tickers") or [])
    )
    portfolio_symbols = [str(value) for value in (portfolio_summary.get("candidate_canonical_symbols") or []) if str(value).strip()]
    portfolio_symbols_ok = not any(not _looks_like_symbol(value) for value in portfolio_symbols)
    candidate_pairs = portfolio_summary.get("candidate_identity_pairs") or []
    canonical_mismatch_count = 0
    for pair in candidate_pairs:
        if not isinstance(pair, dict):
            continue
        broker_symbol = str(pair.get("broker_symbol") or "").strip().upper()
        canonical_ticker = str(pair.get("canonical_ticker") or "").strip().upper()
        if not broker_symbol or not canonical_ticker:
            continue
        if not _looks_like_symbol(broker_symbol) or not _looks_like_symbol(canonical_ticker):
            continue
        if canonical_ticker == broker_symbol:
            continue
        if canonical_ticker.startswith(f"{broker_symbol}."):
            continue
        canonical_mismatch_count += 1
    if not manifest_symbols_ok and not portfolio_symbols_ok:
        identity_integrity = "critical"
    elif not manifest_symbols_ok or not portfolio_symbols_ok or canonical_mismatch_count > 0:
        identity_integrity = "warning"
    return {
        "overlay_health": phase,
        "judge_health": judge_health,
        "data_coverage": data_coverage,
        "prism_coverage": _prism_health_label(portfolio_summary),
        "freshness": f"{freshness} ({degraded_count}/{total_tickers} degraded)",
        "identity_integrity": identity_integrity,
    }


def _prism_health_label(portfolio_summary: dict[str, Any]) -> str:
    external = portfolio_summary.get("external_signals") if isinstance(portfolio_summary, dict) else {}
    if not isinstance(external, dict) or not external:
        return "not configured"
    coverage = external.get("coverage_summary") if isinstance(external.get("coverage_summary"), dict) else {}
    if not coverage:
        summary = external.get("reconciliation_summary") if isinstance(external.get("reconciliation_summary"), dict) else {}
        coverage = summary.get("coverage_summary") if isinstance(summary.get("coverage_summary"), dict) else {}
    if not coverage:
        return "unknown"
    run_market = str(coverage.get("run_market") or "UNKNOWN")
    matching = int(coverage.get("matching_market_signals") or 0)
    total = int(coverage.get("total_signals") or 0)
    cross = int(coverage.get("cross_market_signals") or 0)
    return f"{run_market}: same-market {matching}/{total}, cross-market excluded {cross}"


def _render_health_compact_card(*, manifest: dict[str, Any], portfolio_summary: dict[str, Any]) -> str:
    # Suppress engineering health diagnostics from investor-facing pages.
    return ""


def _render_health_compact_inline(*, manifest: dict[str, Any], portfolio_summary: dict[str, Any]) -> str:
    # Suppress engineering health diagnostics from investor-facing pages.
    return ""


def _health_badges_html(*, manifest: dict[str, Any], portfolio_summary: dict[str, Any]) -> str:
    badges: list[str] = []
    execution = manifest.get("execution") or {}
    phase = ((execution.get("overlay_phase") or {}).get("name") or "").upper()
    if phase == "PRE_OPEN":
        badges.append("오버레이: 장전")
    semantic_health = portfolio_summary.get("semantic_health") or {}
    fallback_ratio = float(semantic_health.get("rule_only_fallback_ratio") or 0.0)
    if fallback_ratio >= 0.3:
        badges.append(f"판단 보강 저하 ({fallback_ratio:.0%})")
    total_candidates = int(semantic_health.get("total_candidates") or 0)
    review_required = int(semantic_health.get("review_required_count") or 0)
    if total_candidates > 0 and review_required / total_candidates >= 0.8:
        badges.append(f"수동 확인 필요 ({review_required}/{total_candidates})")
    if not badges:
        return ""
    return "<div class='pill-row'>" + "".join(
        f"<span class='pill'>{_escape(text)}</span>" for text in badges
    ) + "</div>"


def _looks_like_symbol(value: str) -> bool:
    symbol = str(value or "").strip().upper()
    if not symbol:
        return False
    if " " in symbol:
        return False
    if symbol[0] == "." or symbol[-1] == "." or symbol.count(".") > 1:
        return False
    return all(ch.isalnum() or ch in {".", "-"} for ch in symbol)


def _render_markdown(content: str) -> str:
    content = re.sub(
        r"<details>\s*<summary>.*?JSON.*?</summary>.*?</details>",
        "",
        content or "",
        flags=re.IGNORECASE | re.DOTALL,
    ).strip()
    if _MARKDOWN is None:
        return f"<pre>{_escape(content)}</pre>"
    return _MARKDOWN.render(content)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _escape(value: object) -> str:
    return html.escape(str(value))


_STYLE_CSS = """
:root {
  --bg: #f4efe7;
  --paper: rgba(255, 255, 255, 0.84);
  --ink: #132238;
  --muted: #5d6c7d;
  --line: rgba(19, 34, 56, 0.12);
  --accent: #0f7c82;
  --success: #1f7a4d;
  --warning: #c46a1c;
  --danger: #b23b3b;
  --shadow: 0 18px 45px rgba(17, 34, 51, 0.12);
}

* { box-sizing: border-box; }

body {
  margin: 0;
  color: var(--ink);
  font-family: Aptos, "Segoe UI", "Noto Sans KR", sans-serif;
  background:
    radial-gradient(circle at top right, rgba(15, 124, 130, 0.16), transparent 34%),
    radial-gradient(circle at top left, rgba(196, 106, 28, 0.16), transparent 28%),
    linear-gradient(180deg, #f8f3eb 0%, #eef4f5 100%);
}

a { color: inherit; }

.shell {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
  padding: 24px 0 56px;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(280px, 0.9fr);
  gap: 20px;
  padding: 28px;
  border: 1px solid var(--line);
  border-radius: 28px;
  background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(248,251,252,0.9));
  box-shadow: var(--shadow);
}

.hero h1, .section h2 {
  margin: 0;
  font-family: Georgia, "Times New Roman", serif;
  letter-spacing: -0.03em;
}

.hero h1 {
  font-size: clamp(2.1rem, 4vw, 3.4rem);
  line-height: 0.95;
}

.subtitle, .section-head p, .hero-card p, .run-card p, .ticker-card p, .breadcrumbs, .empty {
  color: var(--muted);
}

.eyebrow {
  margin: 0 0 14px;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.78rem;
  color: var(--accent);
}

.hero-card, .run-card, .ticker-card, .section, .error-block, .prose pre {
  border: 1px solid var(--line);
  border-radius: 22px;
  background: var(--paper);
  box-shadow: var(--shadow);
}

.hero-card, .run-card, .ticker-card, .section { padding: 18px 20px; }

.hero-card p, .ticker-card p {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin: 10px 0;
}

.hero-card p span, .ticker-card p span {
  min-width: 0;
  overflow-wrap: anywhere;
  text-align: right;
}

.ticker-card p.long-field {
  align-items: flex-start;
}

.ticker-card p.long-field strong {
  flex: 0 0 auto;
}

.status {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 12px;
}

.status.success { background: rgba(31, 122, 77, 0.12); color: var(--success); }
.status.partial_failure, .status.pending { background: rgba(196, 106, 28, 0.14); color: var(--warning); }
.status.failed { background: rgba(178, 59, 59, 0.12); color: var(--danger); }

.button, .pill {
  display: inline-flex;
  align-items: center;
  text-decoration: none;
  border-radius: 999px;
  padding: 10px 16px;
  font-weight: 600;
  border: 1px solid rgba(15, 124, 130, 0.22);
  background: rgba(15, 124, 130, 0.12);
}

.section { margin-top: 20px; }

.section-head, .run-card-header, .ticker-card-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: baseline;
}

.warning-banner {
  margin: 1rem 0;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  border: 1px solid rgba(196, 106, 28, 0.4);
  background: rgba(196, 106, 28, 0.12);
  color: #7a3f0b;
}

.run-grid, .ticker-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

.breadcrumbs {
  display: flex;
  gap: 12px;
  margin: 0 0 12px;
}

.breadcrumbs a::after {
  content: "/";
  margin-left: 12px;
  opacity: 0.4;
}

.breadcrumbs a:last-child::after { display: none; }

.pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.advanced-diagnostics {
  margin-top: 12px;
}

.advanced-diagnostics summary {
  cursor: pointer;
  font-weight: 700;
}

.advanced-diagnostics p {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.account-performance .run-card p {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin: 10px 0;
}

.account-performance .run-card p span {
  text-align: right;
  overflow-wrap: anywhere;
}

.account-profit-calendar {
  margin: 18px 0;
}

.account-profit-calendar > h3 {
  margin: 0 0 12px;
  font-size: 1.05rem;
  letter-spacing: 0;
}

.profit-kpi-card.profit-positive strong,
.profit-positive {
  color: #0f7c82;
}

.profit-kpi-card.profit-negative strong,
.profit-negative {
  color: #a43d3d;
}

.profit-kpi-card.profit-neutral strong,
.profit-neutral {
  color: var(--text);
}

.profit-calendar-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 14px;
  margin: 14px 0;
}

.profit-panel h3 {
  margin-top: 0;
}

.profit-week-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(128px, 1fr));
  gap: 8px;
}

.profit-week-item {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 10px;
  background: #fbfdfd;
}

.profit-week-item strong,
.profit-week-item span,
.profit-week-item em {
  display: block;
  overflow-wrap: anywhere;
}

.profit-week-item strong {
  color: var(--text);
  font-size: 0.9rem;
}

.profit-week-item span {
  margin-top: 6px;
  font-weight: 700;
}

.profit-week-item em {
  margin-top: 4px;
  color: var(--muted);
  font-size: 0.82rem;
  font-style: normal;
}

.profit-month-bars {
  display: grid;
  gap: 10px;
}

.profit-month-row {
  display: grid;
  grid-template-columns: 76px minmax(120px, 1fr) minmax(116px, auto);
  align-items: center;
  gap: 10px;
}

.profit-month-label {
  color: var(--muted);
  font-size: 0.9rem;
}

.profit-month-track {
  height: 10px;
  border-radius: 8px;
  background: #eef3f2;
  overflow: hidden;
}

.profit-month-track i {
  display: block;
  width: var(--profit-width);
  min-width: 2px;
  height: 100%;
  border-radius: inherit;
  background: currentColor;
}

.profit-month-row strong {
  text-align: right;
  overflow-wrap: anywhere;
}

.profit-detail-table table {
  min-width: 940px;
}

.profit-detail-table h3 {
  margin: 0 0 10px;
  font-size: 1rem;
  letter-spacing: 0;
}

.account-period-tabs {
  margin: 16px 0;
}

.account-chart {
  margin: 16px 0;
  overflow: hidden;
}

.account-chart-title {
  margin: 0 0 8px;
  font-size: 1rem;
  letter-spacing: 0;
}

.account-chart-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
  margin: 0 0 10px;
  color: var(--muted);
  font-size: 0.92rem;
}

.account-chart svg {
  width: 100%;
  height: auto;
  border: 1px solid var(--line);
  border-radius: 14px;
}

.account-etf-curve {
  margin: 18px 0;
}

.account-etf-curve svg {
  width: 100%;
  height: auto;
  border: 1px solid var(--line);
  border-radius: 12px;
}

.etf-curve-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 8px;
  color: var(--muted);
}

.etf-curve-legend span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.etf-curve-legend i {
  width: 18px;
  height: 3px;
  border-radius: 999px;
  display: inline-block;
}

.account-chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 8px;
  color: var(--muted);
}

.account-chart-legend span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.account-chart-legend i {
  width: 18px;
  height: 3px;
  border-radius: 999px;
  display: inline-block;
}

.account-table-wrap {
  overflow-x: auto;
  margin: 16px 0;
}

.account-table-wrap table {
  width: 100%;
  min-width: 780px;
  border-collapse: collapse;
}

.account-table-wrap th,
.account-table-wrap td {
  border: 1px solid var(--line);
  padding: 10px;
  text-align: left;
  vertical-align: top;
}

.account-period-note {
  color: var(--muted);
  font-size: 0.86rem;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.prose { line-height: 1.65; }
.prose h1, .prose h2, .prose h3 { font-family: Georgia, "Times New Roman", serif; }
.prose pre, .error-block {
  padding: 16px;
  overflow: auto;
  white-space: pre-wrap;
  font-family: Consolas, "Courier New", monospace;
}

.prose table {
  width: 100%;
  border-collapse: collapse;
}

.prose th, .prose td {
  border: 1px solid var(--line);
  padding: 10px;
  text-align: left;
}

.summary-image-frame {
  margin: 16px 0 0;
  display: flex;
  justify-content: center;
}

.summary-image-frame img {
  width: min(100%, 760px);
  height: auto;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: white;
  box-shadow: 0 12px 32px rgba(17, 34, 51, 0.12);
}

@media (max-width: 840px) {
  .hero { grid-template-columns: 1fr; }
  .shell { width: min(100% - 20px, 1180px); }
  .profit-calendar-grid { grid-template-columns: 1fr; }
  .profit-month-row { grid-template-columns: 64px minmax(90px, 1fr); }
  .profit-month-row strong {
    grid-column: 1 / -1;
    text-align: left;
  }
}
"""
