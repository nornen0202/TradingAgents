from __future__ import annotations

import html
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import SiteSettings
from tradingagents.dataflows.intraday_market import DELAYED_ANALYSIS_ONLY, REALTIME_EXECUTION_READY, STALE_INVALID_FOR_EXECUTION
from tradingagents.presentation import (
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

    if site_dir.exists():
        shutil.rmtree(site_dir)
    (site_dir / "assets").mkdir(parents=True, exist_ok=True)
    _write_text(site_dir / "assets" / "style.css", _STYLE_CSS)

    for manifest in manifests:
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
        for ticker_summary in manifest.get("tickers", []):
            _write_text(
                site_dir / "runs" / manifest["run_id"] / f"{ticker_summary['ticker']}.html",
                _render_ticker_page(manifest, ticker_summary, settings, manifests=manifests),
            )

    _write_text(site_dir / "index.html", _render_index_page(manifests, settings))
    _write_json(
        site_dir / "feed.json",
        {
            "generated_at": datetime.now().isoformat(),
            "runs": [
                {key: value for key, value in manifest.items() if key != "_run_dir"}
                for manifest in manifests
            ],
        },
    )
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

    download_dir = site_dir / "downloads" / manifest["run_id"] / "portfolio"
    copied_any = False
    for artifact_path in ((manifest.get("portfolio") or {}).get("artifacts") or {}).values():
        if not artifact_path:
            continue
        source = _resolve_artifact_source(run_dir, artifact_path)
        if source.is_file():
            download_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, download_dir / source.name)
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
        return

    for source in portfolio_summary.get("downloadable_files", []):
        if not isinstance(source, Path) or not source.is_file():
            continue
        download_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, download_dir / source.name)

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


def _resolve_artifact_source(run_dir: Path, path_value: Any) -> Path:
    candidate = Path(str(path_value))
    if candidate.is_absolute():
        return candidate
    return run_dir / candidate


def _render_index_page(manifests: list[dict[str, Any]], settings: SiteSettings) -> str:
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
    if latest and representative and latest["run_id"] != representative["run_id"]:
        latest_technical_html = (
            "<p class='empty'>"
            f"가장 최근 기술 run: <a href='runs/{_escape(latest['run_id'])}/index.html'>{_escape(latest['run_id'])}</a>"
            f" ({_escape(_run_phase_display_label(latest))})"
            "</p>"
        )
    if latest_technical_run:
        latest_technical_html = (
            "<p class='empty'>"
            f"가장 최근 기술 run / Latest technical run: <a href='runs/{_escape(latest_technical_run['run_id'])}/index.html'>{_escape(latest_technical_run['run_id'])}</a>"
            f" ({_escape(_run_phase_display_label(latest_technical_run))})"
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
            {latest_portfolio_link}
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
              {portfolio_link}
            </article>
            """
        )

    warning_html = ""
    if representative and representative.get("warnings"):
        warning_html = "".join(
            f"<div class='warning-banner'>{_escape(warning)}</div>" for warning in representative.get("warnings", [])
        )

    body = latest_html + warning_html + f"""
    <section class="section">
      <div class="section-head">
        <h2>Recent runs</h2>
        <p>{len(manifests)} archived run(s)</p>
      </div>
      <div class="run-grid">
        {''.join(cards) if cards else '<p class="empty">No archived runs were found.</p>'}
      </div>
    </section>
    """
    return _page_template(settings.title, body, prefix="")


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
        portfolio_links.append(
            f"<a class='pill' href='../../downloads/{_escape(manifest['run_id'])}/portfolio/{_escape(artifact_name)}'>{_escape(artifact_name)}</a>"
        )
    if not portfolio_links:
        for source in portfolio_summary.get("downloadable_files", []):
            if not isinstance(source, Path):
                continue
            portfolio_links.append(
                f"<a class='pill' href='../../downloads/{_escape(manifest['run_id'])}/portfolio/{_escape(source.name)}'>{_escape(source.name)}</a>"
            )

    ticker_cards = []
    for ticker_summary in manifest.get("tickers", []):
        investor_summary = _ticker_investor_summary(
            ticker_summary,
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
              <p><strong>투자판단</strong><span>{_escape(investor_summary['investment_view'])}</span></p>
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
        rendered_page = (
            "<a class='pill' href='portfolio.html'>portfolio.html</a>"
            if portfolio_summary.get("status_path")
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
    {live_delta_html}
    {timeline_html}
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
        return (
            "<section class='section'>"
            "<div class='section-head'><h2>Report vs latest intraday reanalysis</h2></div>"
            "<article class='run-card'>"
            "<p>Latest intraday reanalysis not run.</p>"
            "</article>"
            "</section>"
        )

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
        return (
            "<section class='section'>"
            "<div class='section-head'><h2>Latest intraday reanalysis</h2></div>"
            "<article class='run-card'><p>Latest intraday reanalysis not run.</p></article>"
            "</section>"
        )
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
    execution_summary = _load_execution_summary(run_dir)
    report_html = "<p class='empty'>No portfolio markdown report was generated.</p>"
    report_path = portfolio_summary.get("portfolio_report_md")
    if isinstance(report_path, Path) and report_path.exists():
        report_html = _render_markdown(report_path.read_text(encoding="utf-8"))

    download_links = []
    for source in portfolio_summary.get("downloadable_files", []):
        if not isinstance(source, Path):
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
    {_render_live_context_delta_section(manifest)}
    <section class="section prose">
      <div class="section-head">
        <h2>{_escape(portfolio_label)}</h2>
      </div>
      {report_html}
    </section>
    {_render_execution_summary_section(execution_summary)}
    {downloads_html}
    """
    return _page_template(f"{manifest['run_id']} {portfolio_label.lower()} | {settings.title}", body, prefix="../../")


def _render_ticker_page(
    manifest: dict[str, Any],
    ticker_summary: dict[str, Any],
    settings: SiteSettings,
    *,
    manifests: list[dict[str, Any]] | None = None,
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

    investor_summary = _ticker_investor_summary(
        ticker_summary,
        manifest,
        language=language,
        stale_after_seconds=stale_after_seconds,
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
        <p><strong>투자판단</strong><span>{_escape(investor_summary['investment_view'])}</span></p>
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
    {live_ticker_delta_html}
    {ticker_delta_html}
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


def _manifest_language(manifest: dict[str, Any]) -> str:
    return str((manifest.get("settings") or {}).get("output_language") or "English")


def _decision_market_view(raw_decision: Any, *, language: str) -> str:
    presentation = present_decision_payload(raw_decision, language=language)
    return presentation.market_view if presentation else "-"


def _decision_primary_condition(raw_decision: Any, *, language: str) -> str:
    return present_primary_condition(raw_decision, language=language)


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
    rows = [
        ("분석 기준시각", _analysis_asof_label(ticker_summary)),
        ("실행 기준시각", _execution_value(ticker_summary, "execution_asof", default="미갱신")),
        ("판단 상태", _execution_display_state(ticker_summary, stale_after_seconds=stale_after_seconds)),
        ("실행 타이밍", _execution_timing_state_label(ticker_summary)),
        ("신선도", _execution_staleness(ticker_summary)),
        ("판단 출처", _decision_source_label(ticker_summary)),
        ("분석 검토", _analysis_review_required_label(ticker_summary)),
        ("계좌 검토", _portfolio_review_required_label(ticker_summary)),
        ("자료 상태", present_data_status(ticker_summary.get("decision"), quality_flags=ticker_summary.get("quality_flags"), language=_manifest_language(manifest))),
        ("발행 시각", _published_at_label(manifest)),
        ("과거 리포트 여부", _historical_view_label(manifest)),
    ]
    if compact:
        rows = rows[:4]
    row_html = "".join(
        f"<p><strong>{_escape(label)}</strong><span>{_escape(value)}</span></p>"
        for label, value in rows
    )
    return f"""
      <details class="advanced-diagnostics">
        <summary>고급 진단</summary>
        {row_html}
      </details>
    """


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
    files = sorted(path for path in private_dir.iterdir() if path.is_file())
    candidate_symbols: list[str] = []
    candidate_pairs: list[dict[str, str]] = []
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
    return {
        "status_path": status_path,
        "status": str(payload.get("status") or "unknown"),
        "status_class": _status_class(str(payload.get("status") or "unknown")),
        "profile": payload.get("profile"),
        "snapshot_health": payload.get("snapshot_health"),
        "generated_at": payload.get("generated_at"),
        "semantic_health": payload.get("semantic_health") if isinstance(payload, dict) else {},
        "error": payload.get("error"),
        "portfolio_report_md": report_md if report_md.exists() else None,
        "portfolio_report_json": report_json if report_json.exists() else None,
        "candidate_canonical_symbols": candidate_symbols,
        "candidate_identity_pairs": candidate_pairs,
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
    if not summary:
        return ""
    pilot_ready = ", ".join(summary.get("pilot_ready") or []) or "-"
    close_confirm = ", ".join(summary.get("close_confirm") or summary.get("triggered_pending_close") or []) or "-"
    pilot_blocked_volume = ", ".join(summary.get("pilot_blocked_volume") or []) or "-"
    next_day = ", ".join(summary.get("next_day_followthrough_pending") or []) or "-"
    return f"""
    <section class="section">
      <div class="section-head">
        <h2>Advanced diagnostics</h2>
      </div>
      <details class="run-card advanced-diagnostics">
        <summary>Execution overlay details</summary>
        <p><strong>Checkpoint</strong><span>{_escape(summary.get('refresh_checkpoint') or '-')}</span></p>
        <p><strong>Overlay phase</strong><span>{_escape(((summary.get('overlay_phase') or {}).get('name')) or '-')}</span></p>
        <p><strong>Execution as of</strong><span>{_escape(summary.get('execution_asof') or '-')}</span></p>
        <p><strong>Pilot ready</strong><span>{_escape(pilot_ready)}</span></p>
        <p><strong>Close confirm</strong><span>{_escape(close_confirm)}</span></p>
        <p><strong>Pilot blocked by volume</strong><span>{_escape(pilot_blocked_volume)}</span></p>
        <p><strong>Next day follow-through</strong><span>{_escape(next_day)}</span></p>
        <p><strong>Failed breakout</strong><span>{_escape(', '.join(summary.get('failed_breakout') or []) or '-')}</span></p>
        <p><strong>Stale triggerable</strong><span>{_escape(', '.join(summary.get('stale_triggerable') or []) or '-')}</span></p>
      </details>
    </section>
    """
    def _join(values: Any) -> str:
        if not isinstance(values, list) or not values:
            return "-"
        return ", ".join(str(item) for item in values)
    return f"""
    <section class="section">
      <div class="section-head">
        <h2>고급 진단</h2>
      </div>
      <details class="run-card advanced-diagnostics">
        <summary>실행 오버레이 원자료</summary>
        <p><strong>체크포인트</strong><span>{_escape(summary.get('refresh_checkpoint') or '-')}</span></p>
        <p><strong>오버레이 단계</strong><span>{_escape(((summary.get('overlay_phase') or {}).get('name')) or '-')}</span></p>
        <p><strong>실행 기준시각</strong><span>{_escape(summary.get('execution_asof') or '-')}</span></p>
        <p><strong>즉시 검토</strong><span>{_escape(_join(summary.get('actionable_now')))}</span></p>
        <p><strong>종가 확인 대기</strong><span>{_escape(_join(summary.get('triggered_pending_close')))}</span></p>
        <p><strong>관찰</strong><span>{_escape(_join(summary.get('wait')))}</span></p>
        <p><strong>무효화</strong><span>{_escape(_join(summary.get('invalidated')))}</span></p>
        <p><strong>자료 저하</strong><span>{_escape(_join(summary.get('degraded')))}</span></p>
      </details>
    </section>
    """


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
    metrics = _compute_health_metrics(manifest=manifest, portfolio_summary=portfolio_summary)
    return (
        "<details class='advanced-diagnostics run-card'>"
        "<summary>고급 진단</summary>"
        f"<p><strong>오버레이 상태</strong><span>{_escape(metrics['overlay_health'])}</span></p>"
        f"<p><strong>판단 보강 상태</strong><span>{_escape(metrics['judge_health'])}</span></p>"
        f"<p><strong>자료 커버리지</strong><span>{_escape(metrics['data_coverage'])}</span></p>"
        f"<p><strong>신선도</strong><span>{_escape(metrics['freshness'])}</span></p>"
        f"<p><strong>종목 식별</strong><span>{_escape(metrics['identity_integrity'])}</span></p>"
        "</details>"
    )


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
    ranked = sorted(ranked_pool, key=_representative_run_sort_key)
    return ranked[0] if ranked else manifests[0]


def _representative_run_sort_key(manifest: dict[str, Any]) -> tuple[int, int, int, int, str]:
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
    usefulness_rank = int(((manifest.get("run_quality") or {}).get("usefulness_rank") or manifest.get("usefulness_rank") or 100))
    started_at = str(manifest.get("started_at") or "")
    recency_bias = "".join(chr(255 - ord(ch)) if ord(ch) < 255 else ch for ch in started_at)
    return (phase_rank, quality_rank, int(stale_ratio * 1000), usefulness_rank, recency_bias)


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
        "freshness": f"{freshness} ({degraded_count}/{total_tickers} degraded)",
        "identity_integrity": identity_integrity,
    }


def _render_health_compact_card(*, manifest: dict[str, Any], portfolio_summary: dict[str, Any]) -> str:
    metrics = _compute_health_metrics(manifest=manifest, portfolio_summary=portfolio_summary)
    rows = "".join(
        f"<li><strong>{_escape(key.replace('_', ' '))}</strong>: {_escape(value)}</li>"
        for key, value in metrics.items()
    )
    return f"<details class='run-health-compact advanced-diagnostics'><summary>고급 진단</summary><ul>{rows}</ul></details>"


def _render_health_compact_inline(*, manifest: dict[str, Any], portfolio_summary: dict[str, Any]) -> str:
    metrics = _compute_health_metrics(manifest=manifest, portfolio_summary=portfolio_summary)
    compact = " · ".join(f"{key.replace('_', ' ')}={value}" for key, value in metrics.items())
    return f"<p class='empty'>{_escape(compact)}</p>"


def _health_badges_html(*, manifest: dict[str, Any], portfolio_summary: dict[str, Any]) -> str:
    badges: list[str] = []
    execution = manifest.get("execution") or {}
    phase = ((execution.get("overlay_phase") or {}).get("name") or "").upper()
    if phase == "PRE_OPEN":
        badges.append("overlay: pre-open")
    semantic_health = portfolio_summary.get("semantic_health") or {}
    fallback_ratio = float(semantic_health.get("rule_only_fallback_ratio") or 0.0)
    if fallback_ratio >= 0.3:
        badges.append(f"judge degraded ({fallback_ratio:.0%})")
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

@media (max-width: 840px) {
  .hero { grid-template-columns: 1fr; }
  .shell { width: min(100% - 20px, 1180px); }
}
"""
