from __future__ import annotations

import html
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import SiteSettings
from tradingagents.presentation import (
    present_action_summary,
    present_data_status,
    present_decision_payload,
    present_investment_view,
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
            _render_run_page(manifest, settings, portfolio_summary=portfolio_summary),
        )
        if portfolio_summary.get("status_path"):
            _write_text(
                site_dir / "runs" / manifest["run_id"] / "portfolio.html",
                _render_portfolio_page(manifest, settings, portfolio_summary=portfolio_summary),
            )
        for ticker_summary in manifest.get("tickers", []):
            _write_text(
                site_dir / "runs" / manifest["run_id"] / f"{ticker_summary['ticker']}.html",
                _render_ticker_page(manifest, ticker_summary, settings),
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
        return

    for source in portfolio_summary.get("downloadable_files", []):
        if not isinstance(source, Path) or not source.is_file():
            continue
        download_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, download_dir / source.name)


def _resolve_artifact_source(run_dir: Path, path_value: Any) -> Path:
    candidate = Path(str(path_value))
    if candidate.is_absolute():
        return candidate
    return run_dir / candidate


def _render_index_page(manifests: list[dict[str, Any]], settings: SiteSettings) -> str:
    latest = manifests[0] if manifests else None
    latest_portfolio = _load_portfolio_summary(Path(latest["_run_dir"])) if latest else {}
    latest_portfolio_link = (
        f"<a class=\"button\" href=\"runs/{_escape(latest['run_id'])}/portfolio.html\">Open account report</a>"
        if latest and latest_portfolio.get("status_path")
        else ""
    )
    latest_html = (
        f"""
        <section class="hero">
          <div>
            <p class="eyebrow">Latest automated run</p>
            <h1>{_escape(settings.title)}</h1>
            <p class="subtitle">{_escape(settings.subtitle)}</p>
          </div>
          <div class="hero-card">
            <div class="status {latest['status']}">{_escape(latest['status'].replace('_', ' '))}</div>
            <p><strong>Run ID</strong><span>{_escape(latest['run_id'])}</span></p>
            <p><strong>Started</strong><span>{_escape(latest['started_at'])}</span></p>
            <p><strong>Tickers</strong><span>{latest['summary']['total_tickers']}</span></p>
            <p><strong>Success</strong><span>{latest['summary']['successful_tickers']}</span></p>
            <p><strong>Failed</strong><span>{latest['summary']['failed_tickers']}</span></p>
            <a class="button" href="runs/{_escape(latest['run_id'])}/index.html">Open latest run</a>
            {latest_portfolio_link}
          </div>
        </section>
        """
        if latest
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
        portfolio_link = (
            f"<p><a href=\"runs/{_escape(manifest['run_id'])}/portfolio.html\">Account report</a></p>"
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
    if latest and latest.get("warnings"):
        warning_html = "".join(
            f"<div class='warning-banner'>{_escape(warning)}</div>" for warning in latest.get("warnings", [])
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
) -> str:
    portfolio_summary = portfolio_summary or {}
    portfolio_status = manifest.get("portfolio") or {}
    portfolio_status_value = str(
        portfolio_status.get("status") or portfolio_summary.get("status") or "unknown"
    ).strip()
    portfolio_status_class = _status_class(portfolio_status_value)
    portfolio_status_label = _portfolio_status_label(portfolio_status_value)
    portfolio_profile = portfolio_status.get("profile") or portfolio_summary.get("profile") or "-"
    language = _manifest_language(manifest)

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
        ticker_cards.append(
            f"""
            <article class="ticker-card">
              <div class="ticker-card-header">
                <a href="{_escape(ticker_summary['ticker'])}.html">{_escape(ticker_summary['ticker'])}</a>
                <span class="status {ticker_summary['status']}">{_escape(ticker_summary['status'])}</span>
              </div>
              <p><strong>Company</strong><span>{_escape(_ticker_display_label(ticker_summary))}</span></p>
              <p><strong>Analysis date</strong><span>{_escape(ticker_summary.get('analysis_date') or '-')}</span></p>
              <p><strong>Trade date</strong><span>{_escape(ticker_summary.get('trade_date') or '-')}</span></p>
              <p><strong>Investment view</strong><span>{_escape(present_investment_view(ticker_summary.get('decision') or ticker_summary.get('error'), language=language))}</span></p>
              <p><strong>Today</strong><span>{_escape(present_action_summary(ticker_summary.get('decision'), language=language))}</span></p>
              <p><strong>Source status</strong><span>{_escape(present_data_status(ticker_summary.get('decision'), quality_flags=ticker_summary.get('quality_flags'), language=language))}</span></p>
            </article>
            """
        )

    portfolio_html = ""
    if portfolio_status or portfolio_summary:
        rendered_page = (
            "<a class='pill' href='portfolio.html'>portfolio.html</a>"
            if portfolio_summary.get("status_path")
            else "<span class='empty'>No published account report</span>"
        )
        portfolio_html = f"""
    <section class="section">
      <div class="section-head">
        <h2>Account report</h2>
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
    {portfolio_html}
    <section class="section">
      <div class="section-head">
        <h2>Tickers</h2>
        <p>{manifest['summary']['successful_tickers']} success / {manifest['summary']['failed_tickers']} failed</p>
      </div>
      <div class="ticker-grid">
        {''.join(ticker_cards)}
      </div>
    </section>
    """
    return _page_template(f"{manifest['run_id']} | {settings.title}", body, prefix="../../")


def _render_portfolio_page(
    manifest: dict[str, Any],
    settings: SiteSettings,
    *,
    portfolio_summary: dict[str, Any],
) -> str:
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
        summary="Source files",
        empty_text="No downloadable files",
    )
    status_label = _portfolio_status_label(str(portfolio_summary.get("status") or "unknown"))
    snapshot_mode = (
        present_snapshot_mode(str(portfolio_summary.get("snapshot_health")), language="English")
        if portfolio_summary.get("snapshot_health")
        else "Account report"
    )

    body = f"""
    <nav class="breadcrumbs">
      <a href="../../index.html">Home</a>
      <a href="index.html">{_escape(manifest['run_id'])}</a>
    </nav>
    <section class="hero compact">
      <div>
        <p class="eyebrow">Account report</p>
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
    <section class="section prose">
      <div class="section-head">
        <h2>Account report</h2>
      </div>
      {report_html}
    </section>
    {downloads_html}
    """
    return _page_template(f"{manifest['run_id']} account report | {settings.title}", body, prefix="../../")


def _render_ticker_page(
    manifest: dict[str, Any],
    ticker_summary: dict[str, Any],
    settings: SiteSettings,
) -> str:
    run_dir = Path(manifest["_run_dir"])
    language = _manifest_language(manifest)
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
        summary="Source files",
        empty_text="No downloadable files",
    )

    failure_html = ""
    if ticker_summary["status"] != "success":
        failure_html = (
            "<section class='section'>"
            "<div class='section-head'><h2>Failure</h2></div>"
            f"<pre class='error-block'>{_escape(ticker_summary.get('error') or 'Unknown error')}</pre>"
            "</section>"
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
        <p><strong>Analysis date</strong><span>{_escape(ticker_summary.get('analysis_date') or '-')}</span></p>
        <p><strong>Trade date</strong><span>{_escape(ticker_summary.get('trade_date') or '-')}</span></p>
        <p><strong>Investment view</strong><span>{_escape(present_investment_view(ticker_summary.get('decision'), language=language))}</span></p>
        <p><strong>Today</strong><span>{_escape(present_action_summary(ticker_summary.get('decision'), language=language))}</span></p>
        <p><strong>Market view</strong><span>{_escape(_decision_market_view(ticker_summary.get('decision'), language=language))}</span></p>
        <p><strong>Key condition</strong><span>{_escape(_decision_primary_condition(ticker_summary.get('decision'), language=language))}</span></p>
        <p><strong>Source status</strong><span>{_escape(present_data_status(ticker_summary.get('decision'), quality_flags=ticker_summary.get('quality_flags'), language=language))}</span></p>
      </div>
    </section>
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
    if not isinstance(raw_decision, str) or not raw_decision.strip().startswith("{"):
        return "-"
    try:
        decision = parse_structured_decision(raw_decision)
    except Exception:
        return "-"
    for values in (decision.watchlist_triggers, decision.catalysts, decision.invalidators):
        for value in values:
            text = sanitize_investor_text(value, language=language)
            if text and text not in {"-", "없음", "None"}:
                return text
    return "-"


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
    files = sorted(path for path in private_dir.iterdir() if path.is_file())
    return {
        "status_path": status_path,
        "status": str(payload.get("status") or "unknown"),
        "status_class": _status_class(str(payload.get("status") or "unknown")),
        "profile": payload.get("profile"),
        "snapshot_health": payload.get("snapshot_health"),
        "generated_at": payload.get("generated_at"),
        "error": payload.get("error"),
        "portfolio_report_md": report_md if report_md.exists() else None,
        "portfolio_report_json": report_json if report_json.exists() else None,
        "downloadable_files": files,
        "artifact_count": len(files),
    }


def _status_class(status: str) -> str:
    normalized = (status or "").strip().lower()
    if normalized == "success":
        return "success"
    if normalized in {"watchlist_only", "capital_constrained", "degraded"}:
        return "partial_failure"
    if normalized in {"failed", "failure"}:
        return "failed"
    return "pending"


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
