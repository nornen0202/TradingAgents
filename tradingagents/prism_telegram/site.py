from __future__ import annotations

from datetime import datetime, timezone
from html import escape
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Mapping

from tradingagents.prism_telegram.config import PrismTelegramSiteSettings


def build_prism_telegram_site(
    archive_dir: Path,
    site_dir: Path,
    settings: PrismTelegramSiteSettings,
) -> list[dict[str, Any]]:
    archive_dir = Path(archive_dir)
    site_dir = Path(site_dir)
    output_dir = site_dir / "prism-telegram"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifests = _discover_manifests(archive_dir, max_runs=settings.max_runs)
    for manifest in manifests:
        run_dir = _manifest_run_dir(manifest)
        run_site_dir = output_dir / "runs" / _safe_segment(str(manifest.get("run_id") or "run"))
        run_site_dir.mkdir(parents=True, exist_ok=True)
        _write_text(run_site_dir / "index.html", _render_run_page(manifest, settings))
        for message in _public_messages(manifest):
            metadata = _read_json_run_artifact(run_dir, message.get("metadata_path")) or {}
            signals = _read_json_run_artifact(run_dir, message.get("signals_path")) or {}
            message_id = _safe_segment(str(message.get("message_id") or "message"))
            _write_text(
                run_site_dir / f"{message_id}.html",
                _render_message_page(manifest, message, metadata, signals, settings),
            )
            _write_json(
                run_site_dir / f"{message_id}.json",
                _public_message_summary(manifest, message, signals),
            )
    _write_text(output_dir / "index.html", _render_index_page(manifests, settings))
    _write_json(output_dir / "feed.json", _render_feed(manifests, settings))
    return manifests


def _discover_manifests(archive_dir: Path, *, max_runs: int) -> list[dict[str, Any]]:
    candidates = sorted(
        archive_dir.glob("runs/*/*/prism_telegram_run.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    manifests: list[dict[str, Any]] = []
    for path in candidates:
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(manifest, dict):
            continue
        manifest["_manifest_path"] = str(path)
        manifests.append(manifest)
    manifests.sort(key=lambda item: str(item.get("started_at") or item.get("run_id") or ""), reverse=True)
    return manifests[:max_runs]


def _render_index_page(manifests: list[dict[str, Any]], settings: PrismTelegramSiteSettings) -> str:
    latest_messages: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for manifest in manifests:
        for message in _public_messages(manifest):
            latest_messages.append((manifest, message))
            if len(latest_messages) >= settings.max_messages_on_index:
                break
        if len(latest_messages) >= settings.max_messages_on_index:
            break

    run_cards = "\n".join(_run_card(manifest) for manifest in manifests[: settings.max_runs])
    message_cards = "\n".join(_message_card(manifest, message) for manifest, message in latest_messages)
    if not run_cards:
        run_cards = '<p class="muted">아직 공개 가능한 PRISM Telegram 실행 기록이 없습니다.</p>'
    if not message_cards:
        message_cards = '<p class="muted">최근 공개 메시지 리포트가 없습니다.</p>'

    return _page(
        title=settings.title,
        body=f"""
<header class="hero">
  <p class="eyebrow">TradingAgents PRISM Telegram</p>
  <h1>{escape(settings.title)}</h1>
  <p>텔레그램 PRISM 메시지를 보조 신호로 수집해 ticker-level 근거와 공개 가능한 요약만 보여줍니다.</p>
</header>
<section>
  <h2>최근 메시지</h2>
  <div class="grid">{message_cards}</div>
</section>
<section>
  <h2>실행 기록</h2>
  <div class="runs">{run_cards}</div>
</section>
""",
    )


def _render_run_page(manifest: Mapping[str, Any], settings: PrismTelegramSiteSettings) -> str:
    messages = "\n".join(_message_card(dict(manifest), message) for message in _public_messages(manifest))
    if not messages:
        messages = '<p class="muted">이 실행에서 공개할 메시지 리포트가 없습니다.</p>'
    summary = manifest.get("summary") if isinstance(manifest.get("summary"), Mapping) else {}
    run_id = str(manifest.get("run_id") or "run")
    return _page(
        title=f"{settings.title} - {run_id}",
        body=f"""
<nav class="topnav"><a href="../../index.html">PRISM Telegram 홈</a><a href="../../../index.html">TradingAgents 홈</a></nav>
<header class="hero compact">
  <p class="eyebrow">{escape(str((manifest.get('source') or {}).get('channel') or 'stock_ai_agent'))}</p>
  <h1>{escape(run_id)}</h1>
  <p>{escape(str(manifest.get('started_at') or ''))}</p>
</header>
<section class="stats">
  <span>메시지 {escape(str(summary.get('messages', 0)))}개</span>
  <span>신호 {escape(str(summary.get('signals', 0)))}개</span>
  <span>{escape(str(manifest.get('status') or 'unknown'))}</span>
</section>
<section>
  <h2>메시지별 요약</h2>
  <div class="grid">{messages}</div>
</section>
""",
    )


def _render_message_page(
    manifest: Mapping[str, Any],
    message: Mapping[str, Any],
    metadata: Mapping[str, Any],
    signals: Mapping[str, Any],
    settings: PrismTelegramSiteSettings,
) -> str:
    message_id = str(message.get("message_id") or metadata.get("message_id") or "message")
    text = str(metadata.get("text") or message.get("text_preview") or "")
    signal_rows = "\n".join(_signal_row(signal) for signal in (signals.get("signals") or []))
    if not signal_rows:
        signal_rows = "<tr><td colspan='4'>ticker-level 신호 없음</td></tr>"
    documents = "\n".join(_document_item(item) for item in (metadata.get("documents") or []))
    if not documents:
        documents = "<li>첨부 문서 없음</li>"
    return _page(
        title=f"{settings.title} - {message_id}",
        body=f"""
<nav class="topnav"><a href="index.html">실행 목록</a><a href="../../index.html">PRISM Telegram 홈</a></nav>
<article class="report">
  <header class="report-head">
    <p class="eyebrow">{escape(str(manifest.get('run_id') or 'run'))}</p>
    <h1>Telegram message {escape(message_id)}</h1>
    <div class="meta">
      <span class="badge">{escape(str(message.get('posted_at') or metadata.get('posted_at') or ''))}</span>
      <a href="{escape(str(message.get('url') or metadata.get('url') or '#'))}">원본 메시지</a>
    </div>
  </header>
  <section>
    <h2>메시지 요약</h2>
    <pre>{escape(text)}</pre>
  </section>
  <section>
    <h2>첨부 문서</h2>
    <ul>{documents}</ul>
  </section>
  <section>
    <h2>ticker-level 신호</h2>
    <table>
      <thead><tr><th>Ticker</th><th>Action</th><th>Trigger</th><th>Confidence</th></tr></thead>
      <tbody>{signal_rows}</tbody>
    </table>
  </section>
</article>
""",
    )


def _render_feed(manifests: list[dict[str, Any]], settings: PrismTelegramSiteSettings) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for manifest in manifests:
        run_id = str(manifest.get("run_id") or "")
        run_dir = _manifest_run_dir(manifest)
        for message in _public_messages(manifest):
            message_id = str(message.get("message_id") or "")
            signals = _read_json_run_artifact(run_dir, message.get("signals_path")) or {}
            public_summary = _public_message_summary(manifest, message, signals)
            content_sha256 = hashlib.sha256(
                json.dumps(public_summary, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            items.append(
                {
                    "run_id": run_id,
                    "message_id": message_id,
                    "posted_at": message.get("posted_at"),
                    "url": message.get("url"),
                    "text_preview": message.get("text_preview"),
                    "signals_count": message.get("signals_count"),
                    "report_url": f"runs/{_safe_segment(run_id)}/{_safe_segment(message_id)}.html",
                    "summary_url": f"runs/{_safe_segment(run_id)}/{_safe_segment(message_id)}.json",
                    "content_sha256": content_sha256,
                }
            )
    published_items = items[: settings.max_messages_on_index]
    occurred = sorted(str(item.get("posted_at") or "") for item in published_items if item.get("posted_at"))
    return {
        "version": 2,
        "title": settings.title,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "total_items": len(items),
        "truncated": len(published_items) < len(items),
        "oldest_occurred_at": occurred[0] if occurred else None,
        "newest_occurred_at": occurred[-1] if occurred else None,
        "items": published_items,
    }


def _public_message_summary(
    manifest: Mapping[str, Any],
    message: Mapping[str, Any],
    signals_payload: Mapping[str, Any],
) -> dict[str, Any]:
    preview = str(message.get("text_preview") or "")[:1200]
    simulation_only = "시뮬" in preview or "simulation" in preview.lower()
    signals = []
    for signal in signals_payload.get("signals") or []:
        if not isinstance(signal, Mapping):
            continue
        signals.append(
            {
                key: signal.get(key)
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
    return {
        "version": 1,
        "run_id": manifest.get("run_id"),
        "channel": (manifest.get("source") or {}).get("channel") if isinstance(manifest.get("source"), Mapping) else None,
        "message_id": str(message.get("message_id") or ""),
        "posted_at": message.get("posted_at"),
        "source_url": message.get("url"),
        "preview": preview,
        "signals": signals,
        "simulation_only": simulation_only,
        "actionability": "research_only",
        "execution_eligible": False,
    }


def _run_card(manifest: Mapping[str, Any]) -> str:
    run_id = str(manifest.get("run_id") or "run")
    summary = manifest.get("summary") if isinstance(manifest.get("summary"), Mapping) else {}
    return f"""
<a class="run" href="runs/{escape(_safe_segment(run_id))}/index.html">
  <strong>{escape(run_id)}</strong>
  <span>{escape(str(manifest.get('started_at') or ''))}</span>
  <small>{escape(str(summary.get('messages', 0)))} messages · {escape(str(summary.get('signals', 0)))} signals</small>
</a>
"""


def _message_card(manifest: Mapping[str, Any], message: Mapping[str, Any]) -> str:
    run_id = _safe_segment(str(manifest.get("run_id") or "run"))
    message_id = _safe_segment(str(message.get("message_id") or "message"))
    text = str(message.get("text_preview") or "Telegram message")
    return f"""
<a class="card" href="runs/{escape(run_id)}/{escape(message_id)}.html">
  <span class="badge">{escape(str(message.get('signals_count') or 0))} signals</span>
  <strong>{escape(str(message.get('message_id') or '-'))}</strong>
  <p>{escape(text)}</p>
  <small>{escape(str(message.get('posted_at') or ''))}</small>
</a>
"""


def _signal_row(signal: Mapping[str, Any]) -> str:
    return (
        "<tr>"
        f"<td>{escape(str(signal.get('canonical_ticker') or '-'))}</td>"
        f"<td>{escape(str(signal.get('signal_action') or '-'))}</td>"
        f"<td>{escape(str(signal.get('trigger_type') or '-'))}</td>"
        f"<td>{escape(str(signal.get('confidence') or '-'))}</td>"
        "</tr>"
    )


def _document_item(document: Mapping[str, Any]) -> str:
    name = str(document.get("filename") or "document")
    summary = document.get("text_summary") if isinstance(document.get("text_summary"), Mapping) else {}
    status = str(summary.get("status") or document.get("mime_type") or "")
    excerpt = str(summary.get("excerpt") or "")
    excerpt_html = f"<p>{escape(excerpt[:600])}</p>" if excerpt else ""
    return f"<li><strong>{escape(name)}</strong> <span>{escape(status)}</span>{excerpt_html}</li>"


def _public_messages(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [item for item in (manifest.get("messages") or []) if isinstance(item, dict)]


def _manifest_run_dir(manifest: Mapping[str, Any]) -> Path:
    try:
        return Path(str(manifest["_manifest_path"])).parent
    except KeyError:
        return Path(".")


def _read_json_run_artifact(run_dir: Path, relative_path: Any) -> dict[str, Any] | None:
    if not relative_path:
        return None
    path = run_dir / str(relative_path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _page(*, title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>{_STYLE}</style>
</head>
<body>
  <main>{body}</main>
</body>
</html>
"""


def _safe_segment(value: str) -> str:
    text = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in str(value or "").strip())
    return text.strip(".-")[:100] or "item"


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


_STYLE = """
:root { color-scheme: light; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
body { margin: 0; background: #f7f8fa; color: #111827; }
main { max-width: 1120px; margin: 0 auto; padding: 32px 20px 56px; }
a { color: inherit; }
.hero { display: grid; gap: 8px; margin-bottom: 28px; }
.hero.compact { margin-bottom: 18px; }
.eyebrow { margin: 0; color: #386641; font-size: 13px; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; }
h1 { margin: 0; font-size: clamp(30px, 5vw, 54px); line-height: 1.02; }
h2 { margin-top: 30px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }
.card, .run { display: block; background: #fff; border: 1px solid #d7dde5; border-radius: 8px; padding: 16px; text-decoration: none; }
.card p { color: #374151; min-height: 52px; }
.runs { display: grid; gap: 10px; }
.run span, .run small { display: block; margin-top: 4px; color: #4b5563; }
.badge { display: inline-flex; width: fit-content; padding: 4px 8px; border-radius: 999px; background: #e8f3ec; color: #22543d; font-size: 12px; font-weight: 700; }
.muted { color: #6b7280; }
.topnav { display: flex; gap: 12px; margin-bottom: 20px; }
.topnav a { padding: 8px 10px; background: #fff; border: 1px solid #d7dde5; border-radius: 6px; text-decoration: none; }
.stats { display: flex; flex-wrap: wrap; gap: 10px; }
.stats span { background: #fff; border: 1px solid #d7dde5; border-radius: 6px; padding: 10px 12px; }
.report { background: #fff; border: 1px solid #d7dde5; border-radius: 8px; padding: 22px; }
.report-head { display: grid; gap: 8px; margin-bottom: 18px; }
.meta { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
pre { white-space: pre-wrap; background: #f3f4f6; border-radius: 6px; padding: 14px; overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { border-bottom: 1px solid #e5e7eb; padding: 10px; text-align: left; vertical-align: top; }
li { margin: 10px 0; }
""".strip()
