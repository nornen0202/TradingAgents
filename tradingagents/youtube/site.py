from __future__ import annotations

from datetime import datetime, timezone
from html import escape
import json
import re
import shutil
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import unquote, urlparse

from tradingagents.youtube.config import YouTubeSiteSettings


def build_youtube_site(
    archive_dir: Path,
    site_dir: Path,
    settings: YouTubeSiteSettings,
) -> list[dict[str, Any]]:
    """Render archived YouTube verification runs under site/youtube."""

    archive_dir = Path(archive_dir)
    site_dir = Path(site_dir)
    youtube_dir = site_dir / "youtube"
    if youtube_dir.exists():
        shutil.rmtree(youtube_dir)
    youtube_dir.mkdir(parents=True, exist_ok=True)

    manifests = _discover_manifests(archive_dir, max_runs=settings.max_runs)
    for manifest in manifests:
        run_dir = _manifest_run_dir(manifest)
        run_site_dir = youtube_dir / "runs" / _safe_segment(str(manifest.get("run_id") or "run"))
        run_site_dir.mkdir(parents=True, exist_ok=True)
        _write_text(run_site_dir / "index.html", _render_run_page(manifest, settings))
        for video in _public_report_videos(manifest):
            final_report = _read_run_artifact(run_dir, video.get("final_report_path"))
            public_summary = _read_json_run_artifact(run_dir, video.get("public_summary_path"))
            page = _render_video_page(manifest, video, final_report, public_summary, settings)
            _write_text(run_site_dir / f"{_safe_segment(str(video.get('video_id') or 'video'))}.html", page)
            summary_path = run_site_dir / f"{_safe_segment(str(video.get('video_id') or 'video'))}.json"
            _write_json(summary_path, public_summary or _public_summary_from_video(video))

    _write_text(youtube_dir / "index.html", _render_index_page(manifests, settings))
    _write_json(youtube_dir / "feed.json", _render_feed(manifests, settings))
    return manifests


def _discover_manifests(archive_dir: Path, *, max_runs: int) -> list[dict[str, Any]]:
    candidates = sorted(archive_dir.glob("runs/*/*/youtube_run.json"), key=lambda path: path.stat().st_mtime, reverse=True)
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


def _render_index_page(manifests: list[dict[str, Any]], settings: YouTubeSiteSettings) -> str:
    latest_videos: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for manifest in manifests:
        for video in _public_report_videos(manifest):
            latest_videos.append((manifest, video))
            if len(latest_videos) >= settings.max_videos_on_index:
                break
        if len(latest_videos) >= settings.max_videos_on_index:
            break

    run_cards = "\n".join(_run_card(manifest) for manifest in manifests[: settings.max_runs])
    video_cards = "\n".join(_video_card(manifest, video) for manifest, video in latest_videos)
    if not run_cards:
        run_cards = '<p class="muted">아직 공개 가능한 YouTube 리포트 실행 기록이 없습니다.</p>'
    if not video_cards:
        video_cards = '<p class="muted">최근 공개 리포트가 없습니다.</p>'

    return _page(
        title=settings.title,
        body=f"""
<header class="hero">
  <p class="eyebrow">TradingAgents YouTube</p>
  <h1>{escape(settings.title)}</h1>
  <p>최근 24시간 업로드 영상을 수집해 영상 주장과 공개 데이터 검증 결과를 분리한 투자자용 리포트입니다.</p>
</header>
<section>
  <h2>최근 리포트</h2>
  <div class="grid">{video_cards}</div>
</section>
<section>
  <h2>실행 기록</h2>
  <div class="runs">{run_cards}</div>
</section>
""",
    )


def _render_run_page(manifest: Mapping[str, Any], settings: YouTubeSiteSettings) -> str:
    videos = "\n".join(_video_card(dict(manifest), video) for video in _public_report_videos(manifest))
    if not videos:
        videos = '<p class="muted">이 실행에서 공개할 영상 리포트가 없습니다.</p>'
    run_id = str(manifest.get("run_id") or "run")
    summary = manifest.get("summary") if isinstance(manifest.get("summary"), Mapping) else {}
    return _page(
        title=f"{settings.title} - {run_id}",
        body=f"""
<nav class="topnav"><a href="../../index.html">YouTube 홈</a><a href="../../../index.html">TradingAgents 홈</a></nav>
<header class="hero compact">
  <p class="eyebrow">{escape(str(manifest.get('channel_name') or 'YouTube'))}</p>
  <h1>{escape(run_id)}</h1>
  <p>{escape(_format_window(manifest))}</p>
</header>
<section class="stats">
  <span>총 {escape(str(summary.get('total_videos', 0)))}개</span>
  <span>성공 {escape(str(summary.get('successful_videos', 0)))}개</span>
  <span>실패 {escape(str(summary.get('failed_videos', 0)))}개</span>
</section>
<section>
  <h2>영상별 리포트</h2>
  <div class="grid">{videos}</div>
</section>
""",
    )


def _render_video_page(
    manifest: Mapping[str, Any],
    video: Mapping[str, Any],
    final_report: str,
    public_summary: Mapping[str, Any] | None,
    settings: YouTubeSiteSettings,
) -> str:
    title = str(video.get("title") or video.get("video_id") or "YouTube report")
    status = str(video.get("status") or (public_summary or {}).get("status") or "unknown")
    video_url = str(video.get("video_url") or (public_summary or {}).get("url") or "")
    report_html = _markdown_to_html(final_report or "# 리포트 생성 실패\n\n공개 가능한 최종 리포트 본문을 찾지 못했습니다.")
    summary_json = escape(json.dumps(public_summary or _public_summary_from_video(video), ensure_ascii=False, indent=2))
    return _page(
        title=f"{settings.title} - {title}",
        body=f"""
<nav class="topnav"><a href="index.html">실행 목록</a><a href="../../index.html">YouTube 홈</a></nav>
<article class="report">
  <header class="report-head">
    <p class="eyebrow">{escape(str(manifest.get('run_id') or 'run'))}</p>
    <h1>{escape(title)}</h1>
    <div class="meta">
      <span class="badge status-{escape(_safe_segment(status))}">{escape(status)}</span>
      <a href="{escape(video_url)}">원본 영상</a>
    </div>
  </header>
  {report_html}
  <details>
    <summary>공개 요약 JSON</summary>
    <pre>{summary_json}</pre>
  </details>
</article>
""",
    )


def _render_feed(manifests: list[dict[str, Any]], settings: YouTubeSiteSettings) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for manifest in manifests:
        run_id = str(manifest.get("run_id") or "")
        for video in _public_report_videos(manifest):
            video_id = str(video.get("video_id") or "")
            items.append(
                {
                    "run_id": run_id,
                    "video_id": video_id,
                    "title": video.get("title"),
                    "channel": video.get("channel"),
                    "source_url": video.get("source_url"),
                    "thumbnail_url": video.get("thumbnail_url"),
                    "status": video.get("status"),
                    "published_at": video.get("published_at"),
                    "video_url": video.get("video_url"),
                    "report_url": f"runs/{_safe_segment(run_id)}/{_safe_segment(video_id)}.html",
                }
            )
    return {
        "version": 1,
        "title": settings.title,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "items": items[: settings.max_videos_on_index],
    }


def _run_card(manifest: Mapping[str, Any]) -> str:
    run_id = str(manifest.get("run_id") or "run")
    summary = manifest.get("summary") if isinstance(manifest.get("summary"), Mapping) else {}
    return f"""
<a class="run" href="runs/{escape(_safe_segment(run_id))}/index.html">
  <strong>{escape(run_id)}</strong>
  <span>{escape(_format_window(manifest))}</span>
  <small>{escape(str(summary.get('total_videos', 0)))} videos · {escape(str(manifest.get('status') or 'unknown'))}</small>
</a>
"""


def _video_card(manifest: Mapping[str, Any], video: Mapping[str, Any]) -> str:
    run_id = _safe_segment(str(manifest.get("run_id") or "run"))
    video_id = _safe_segment(str(video.get("video_id") or "video"))
    title = str(video.get("title") or video.get("video_id") or "YouTube report")
    status = str(video.get("status") or "unknown")
    published = str(video.get("published_at") or "")
    channel = _first_text(video.get("channel"), video.get("channel_name"))
    source_url = _first_text(video.get("source_url"))
    source_label = _source_label_from_url(source_url)
    thumbnail_url = _first_text(video.get("thumbnail_url"))
    source_parts = []
    if channel:
        source_parts.append(f"채널: {channel}")
    if source_label:
        source_parts.append(f"출처: {source_label}")
    source_text = " · ".join(source_parts) or "채널 정보 없음"
    thumb = (
        f'<span class="thumb"><img src="{escape(thumbnail_url)}" alt="{escape(title)}" loading="lazy" referrerpolicy="no-referrer"></span>'
        if thumbnail_url
        else f'<span class="thumb thumb-empty"><span>{escape(channel or "YouTube")}</span></span>'
    )
    return f"""
<a class="card" href="runs/{escape(run_id)}/{escape(video_id)}.html">
  {thumb}
  <span class="card-body">
    <span class="badge status-{escape(_safe_segment(status))}">{escape(status)}</span>
    <strong>{escape(title)}</strong>
    <small class="source-line">{escape(source_text)}</small>
    <small>{escape(published)}</small>
  </span>
</a>
"""


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


def _markdown_to_html(markdown: str) -> str:
    html_parts: list[str] = []
    in_list = False
    in_code = False
    code_lines: list[str] = []

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            html_parts.append("</ul>")
            in_list = False

    for raw_line in str(markdown or "").splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            if in_code:
                html_parts.append(f"<pre><code>{escape(chr(10).join(code_lines))}</code></pre>")
                code_lines = []
                in_code = False
            else:
                close_list()
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        stripped = line.strip()
        if not stripped:
            close_list()
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            close_list()
            level = min(4, len(heading.group(1)) + 1)
            html_parts.append(f"<h{level}>{_inline_markdown(heading.group(2))}</h{level}>")
            continue
        if stripped.startswith(("- ", "* ")):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{_inline_markdown(stripped[2:].strip())}</li>")
            continue
        close_list()
        html_parts.append(f"<p>{_inline_markdown(stripped)}</p>")
    close_list()
    if in_code:
        html_parts.append(f"<pre><code>{escape(chr(10).join(code_lines))}</code></pre>")
    return "\n".join(html_parts)


def _inline_markdown(text: str) -> str:
    value = escape(text)
    value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', value)
    return value


def _manifest_videos(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    videos = manifest.get("videos")
    if not isinstance(videos, list):
        return []
    return [dict(item) for item in videos if isinstance(item, Mapping)]


def _public_report_videos(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    run_dir = _manifest_run_dir(manifest)
    return [video for video in _manifest_videos(manifest) if _is_public_report_video(video, run_dir)]


def _is_public_report_video(video: Mapping[str, Any], run_dir: Path) -> bool:
    if str(video.get("status") or "") in {"failed", "skipped_no_transcript"}:
        return False
    has_available_transcript = False
    for payload in (video, _read_json_run_artifact(run_dir, video.get("public_summary_path")), _read_json_run_artifact(run_dir, video.get("metadata_path"))):
        if not isinstance(payload, Mapping):
            continue
        transcript_status = payload.get("transcript_status")
        if transcript_status == "available":
            has_available_transcript = True
            continue
        if transcript_status and transcript_status != "available":
            return False
    return has_available_transcript


def _manifest_run_dir(manifest: Mapping[str, Any]) -> Path:
    manifest_path = manifest.get("_manifest_path")
    if manifest_path:
        return Path(str(manifest_path)).parent
    return Path(".")


def _read_run_artifact(run_dir: Path, relative_path: Any) -> str:
    if not relative_path:
        return ""
    path = (run_dir / str(relative_path)).resolve()
    try:
        if not _is_relative_to(path, run_dir.resolve()):
            return ""
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _read_json_run_artifact(run_dir: Path, relative_path: Any) -> dict[str, Any] | None:
    text = _read_run_artifact(run_dir, relative_path)
    if not text:
        return None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _public_summary_from_video(video: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "video_id": video.get("video_id"),
        "title": video.get("title"),
        "url": video.get("video_url"),
        "channel": video.get("channel"),
        "source_url": video.get("source_url"),
        "thumbnail_url": video.get("thumbnail_url"),
        "published_at": video.get("published_at"),
        "status": video.get("status"),
    }


def _first_text(*values: Any) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _source_label_from_url(url: str) -> str:
    text = str(url or "").strip()
    if not text:
        return ""
    parsed = urlparse(text)
    if not parsed.netloc:
        return text
    parts = [unquote(part) for part in parsed.path.strip("/").split("/") if part]
    handle = next((part for part in parts if part.startswith("@")), "")
    tab = parts[-1] if parts and parts[-1] in {"videos", "shorts", "streams"} else ""
    tab_label = {"videos": "동영상", "shorts": "쇼츠", "streams": "라이브"}.get(tab, tab)
    base = handle or parsed.netloc
    return f"{base} / {tab_label}" if tab_label else base


def _format_window(manifest: Mapping[str, Any]) -> str:
    start = str(manifest.get("window_start") or "")
    end = str(manifest.get("window_end") or "")
    if start and end:
        return f"{start} - {end}"
    return str(manifest.get("started_at") or "")


def _safe_segment(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(value or "").strip())
    return safe.strip(".-") or "item"


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


_STYLE = """
:root {
  color-scheme: light;
  --bg: #f7f8fb;
  --panel: #ffffff;
  --text: #172033;
  --muted: #667085;
  --line: #d9dee8;
  --accent: #0f766e;
  --accent-2: #2563eb;
  --warn: #b45309;
  --bad: #b42318;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); font: 16px/1.6 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
main { width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0 56px; }
a { color: var(--accent-2); text-decoration: none; }
a:hover { text-decoration: underline; }
.hero { padding: 28px 0 22px; border-bottom: 1px solid var(--line); margin-bottom: 28px; }
.hero.compact { padding-top: 12px; }
.hero h1 { margin: 0; font-size: clamp(28px, 4vw, 44px); line-height: 1.15; letter-spacing: 0; }
.hero p { max-width: 760px; color: var(--muted); margin: 12px 0 0; }
.eyebrow { color: var(--accent); font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0; margin: 0 0 8px; }
section { margin: 28px 0; }
h2, h3, h4, h5 { letter-spacing: 0; line-height: 1.25; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }
.card, .run { display: flex; flex-direction: column; gap: 8px; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; color: var(--text); min-height: 128px; }
.run { padding: 16px; }
.card:hover, .run:hover { border-color: var(--accent-2); text-decoration: none; }
.thumb { display: flex; align-items: center; justify-content: center; width: 100%; aspect-ratio: 16 / 9; overflow: hidden; background: #e9edf5; border-radius: 8px 8px 0 0; color: var(--muted); font-size: 13px; font-weight: 700; }
.thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
.thumb-empty span { padding: 0 14px; text-align: center; }
.card-body { display: flex; flex-direction: column; gap: 8px; padding: 14px 16px 16px; }
.card strong { line-height: 1.35; }
.source-line { color: #3f4a5f; font-weight: 600; }
.runs { display: grid; gap: 10px; }
.badge { display: inline-flex; width: fit-content; border-radius: 999px; padding: 2px 9px; background: #e6f4f1; color: var(--accent); font-size: 12px; font-weight: 700; }
.status-contradicted, .status-llm_failed { background: #fee4e2; color: var(--bad); }
.status-unverified, .status-stale { background: #fff4d6; color: var(--warn); }
small, .muted { color: var(--muted); }
.topnav { display: flex; gap: 14px; margin-bottom: 16px; font-size: 14px; }
.stats { display: flex; flex-wrap: wrap; gap: 10px; }
.stats span { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 8px 12px; }
.report { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: min(5vw, 36px); }
.report-head { border-bottom: 1px solid var(--line); margin-bottom: 24px; padding-bottom: 20px; }
.report-head h1 { margin: 0; font-size: clamp(24px, 3.5vw, 38px); line-height: 1.2; }
.meta { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin-top: 12px; }
pre { overflow: auto; background: #111827; color: #f9fafb; border-radius: 8px; padding: 14px; }
code { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }
details { margin-top: 28px; border-top: 1px solid var(--line); padding-top: 18px; }
@media (max-width: 640px) {
  main { width: min(100% - 20px, 1120px); padding-top: 18px; }
  .report { padding: 18px; }
}
"""
