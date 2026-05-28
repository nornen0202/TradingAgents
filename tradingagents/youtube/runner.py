from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Iterable
from zoneinfo import ZoneInfo

from tradingagents.dataflows.youtube_video import YouTubeVideoBundle, fetch_youtube_video
from tradingagents.youtube.channel import (
    YouTubeVideoReference,
    dedupe_video_references,
    filter_references_by_window,
    list_channel_video_references,
)
from tradingagents.youtube.config import YouTubeDailyConfig, load_youtube_config, with_youtube_overrides
from tradingagents.youtube.site import build_youtube_site
from tradingagents.youtube.verifier import VerifiedVideoReport, verify_youtube_bundle
from tradingagents.youtube_report import build_youtube_video_report


ReferenceLister = Callable[[Iterable[str], int], tuple[YouTubeVideoReference, ...]]
VideoFetcher = Callable[[str], YouTubeVideoBundle]
BundleVerifier = Callable[[YouTubeVideoBundle, str, datetime], VerifiedVideoReport]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Collect YouTube videos, verify investor-facing claims, and publish static report pages."
    )
    parser.add_argument("--config", default="config/youtube_daily.toml", help="Path to YouTube daily TOML config.")
    parser.add_argument("--archive-dir", help="Override YouTube archive directory.")
    parser.add_argument("--site-dir", help="Override generated site output directory.")
    parser.add_argument("--site-only", action="store_true", help="Only rebuild /youtube from archived YouTube runs.")
    parser.add_argument("--video-url", help="Single YouTube video URL or id for ad-hoc report generation.")
    parser.add_argument("--verify", action="store_true", help="Run LLM verification/refinement for --video-url.")
    parser.add_argument("--out", help="Output markdown path for --video-url.")
    parser.add_argument("--lookback-hours", type=int, help="Override channel lookback window in hours.")
    parser.add_argument("--channel-urls", help="Comma-separated channel tab URLs override.")
    parser.add_argument("--max-videos", type=int, help="Maximum videos to process.")
    parser.add_argument("--publish", dest="publish", action="store_true", default=True, help="Build public site after run.")
    parser.add_argument("--no-publish", dest="publish", action="store_false", help="Skip public site build after run.")
    args = parser.parse_args(argv)

    config = with_youtube_overrides(
        load_youtube_config(args.config),
        archive_dir=args.archive_dir,
        site_dir=args.site_dir,
        lookback_hours=args.lookback_hours,
        max_videos=args.max_videos,
        channel_urls=_split_csv(args.channel_urls),
    )

    if args.site_only:
        manifests = build_youtube_site(config.storage.archive_dir, config.storage.site_dir, config.site)
        print(f"Rebuilt YouTube site at {config.storage.site_dir / 'youtube'} from {len(manifests)} archived run(s).")
        return 0

    if args.video_url:
        output_path = execute_single_video(config, args.video_url, verify=args.verify, out=args.out)
        print(f"Wrote YouTube report to {output_path}")
        return 0

    manifest = execute_youtube_run(config, publish=args.publish)
    summary = manifest.get("summary") or {}
    print(
        f"Completed YouTube run {manifest['run_id']} with status {manifest['status']} "
        f"({summary.get('successful_videos', 0)} success / {summary.get('failed_videos', 0)} failed)."
    )
    return 0


def execute_youtube_run(
    config: YouTubeDailyConfig,
    *,
    publish: bool = True,
    reference_lister: ReferenceLister | None = None,
    video_fetcher: VideoFetcher | None = None,
    bundle_verifier: BundleVerifier | None = None,
) -> dict[str, Any]:
    tz = ZoneInfo(config.channel.timezone)
    started_at = datetime.now(tz)
    timer_start = perf_counter()
    run_id = _build_run_id(started_at)
    run_dir = config.storage.archive_dir / "runs" / started_at.strftime("%Y") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    window_end = started_at
    window_start = window_end - timedelta(hours=config.channel.lookback_hours)

    lister = reference_lister or _default_reference_lister
    fetcher = video_fetcher or fetch_youtube_video
    verifier = bundle_verifier or _default_bundle_verifier(config)

    raw_references = lister(config.channel.urls, max(config.channel.max_videos * 3, config.channel.max_videos))
    references = filter_references_by_window(
        dedupe_video_references(raw_references),
        now=started_at,
        lookback_hours=config.channel.lookback_hours,
        include_unknown_dates=True,
    )

    video_summaries: list[dict[str, Any]] = []
    selected_count = 0
    failed_count = 0
    skipped_count = 0
    for reference in references:
        if selected_count >= config.channel.max_videos:
            break
        video_dir = run_dir / "videos" / reference.video_id
        video_dir.mkdir(parents=True, exist_ok=True)
        try:
            bundle = fetcher(reference.url)
            if not _bundle_in_window(bundle, window_start=window_start, window_end=window_end):
                skipped_count += 1
                continue
            selected_count += 1
            draft_report = build_youtube_video_report(bundle, generated_at=started_at.replace(tzinfo=None))
            verified = verifier(bundle, draft_report, started_at)
            _write_text(video_dir / "draft_report.md", draft_report)
            _write_text(video_dir / "final_report.md", verified.final_report_markdown)
            _write_json(video_dir / "metadata.json", _metadata_payload(bundle))
            _write_json(video_dir / "verification.json", verified.verification)
            public_summary = _public_summary(bundle, verified)
            _write_json(video_dir / "public_summary.json", public_summary)
            video_summaries.append(
                _manifest_video_item(
                    bundle=bundle,
                    status=verified.status,
                    video_dir=video_dir,
                    run_dir=run_dir,
                    error=None,
                )
            )
        except Exception as exc:
            failed_count += 1
            selected_count += 1
            error_summary = {
                "video_id": reference.video_id,
                "title": reference.title,
                "video_url": reference.url,
                "published_at": reference.published_at.isoformat() if reference.published_at else None,
                "status": "failed",
                "error": str(exc),
                "metadata_path": _relative_artifact_path(video_dir / "metadata.json", run_dir),
                "public_summary_path": _relative_artifact_path(video_dir / "public_summary.json", run_dir),
            }
            _write_json(
                video_dir / "metadata.json",
                {
                    "video_id": reference.video_id,
                    "url": reference.url,
                    "title": reference.title,
                    "source_url": reference.source_url,
                    "published_at": reference.published_at.isoformat() if reference.published_at else None,
                    "collection_error": str(exc),
                },
            )
            _write_json(video_dir / "public_summary.json", error_summary)
            video_summaries.append(error_summary)

    successful_count = sum(1 for item in video_summaries if item.get("status") not in {"failed"})
    manifest = {
        "version": 1,
        "run_id": run_id,
        "status": "success" if failed_count == 0 else "partial_failure",
        "channel_name": config.channel.name,
        "channel_urls": list(config.channel.urls),
        "timezone": config.channel.timezone,
        "lookback_hours": config.channel.lookback_hours,
        "started_at": started_at.isoformat(),
        "finished_at": datetime.now(tz).isoformat(),
        "duration_seconds": round(perf_counter() - timer_start, 3),
        "window_start": window_start.isoformat(),
        "window_end": window_end.isoformat(),
        "summary": {
            "raw_references": len(raw_references),
            "candidate_references": len(references),
            "total_videos": len(video_summaries),
            "successful_videos": successful_count,
            "failed_videos": failed_count,
            "skipped_out_of_window": skipped_count,
        },
        "videos": video_summaries,
        "source_policy": {
            "raw_transcript_archived": False,
            "raw_transcript_published": False,
            "public_artifacts": ["html_report", "public_summary_json"],
        },
    }
    _write_json(run_dir / "youtube_run.json", manifest)
    _write_json(config.storage.archive_dir / "latest-youtube-run.json", manifest)
    if publish:
        build_youtube_site(config.storage.archive_dir, config.storage.site_dir, config.site)
    return manifest


def execute_single_video(
    config: YouTubeDailyConfig,
    video_url: str,
    *,
    verify: bool,
    out: str | None = None,
) -> Path:
    generated_at = datetime.now(ZoneInfo(config.channel.timezone))
    bundle = fetch_youtube_video(video_url)
    draft_report = build_youtube_video_report(bundle, generated_at=generated_at.replace(tzinfo=None))
    if verify:
        verified = verify_youtube_bundle(
            bundle,
            draft_report,
            llm_settings=config.llm,
            verification_settings=config.verification,
            generated_at=generated_at,
        )
        markdown = verified.final_report_markdown
    else:
        verified = None
        markdown = draft_report

    output = Path(out) if out else Path("reports") / "youtube" / f"{bundle.metadata.video_id}_{'final' if verify else 'draft'}_report.md"
    _write_text(output, markdown)
    if verified is not None:
        _write_json(output.with_name(output.stem + "_verification.json"), verified.verification)
        _write_json(output.with_name(output.stem + "_public_summary.json"), _public_summary(bundle, verified))
    return output


def _default_reference_lister(channel_urls: Iterable[str], max_entries_per_url: int) -> tuple[YouTubeVideoReference, ...]:
    return list_channel_video_references(channel_urls, max_entries_per_url=max_entries_per_url)


def _default_bundle_verifier(config: YouTubeDailyConfig) -> BundleVerifier:
    def verify(bundle: YouTubeVideoBundle, draft_report: str, generated_at: datetime) -> VerifiedVideoReport:
        return verify_youtube_bundle(
            bundle,
            draft_report,
            llm_settings=config.llm,
            verification_settings=config.verification,
            generated_at=generated_at,
        )

    return verify


def _bundle_in_window(bundle: YouTubeVideoBundle, *, window_start: datetime, window_end: datetime) -> bool:
    published_at = bundle.metadata.published_at
    if published_at is None:
        return False
    comparable = _to_timezone(published_at, window_end.tzinfo)
    return window_start <= comparable <= window_end


def _to_timezone(value: datetime, tzinfo: Any) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    if tzinfo is not None:
        value = value.astimezone(tzinfo)
    return value


def _manifest_video_item(
    *,
    bundle: YouTubeVideoBundle,
    status: str,
    video_dir: Path,
    run_dir: Path,
    error: str | None,
) -> dict[str, Any]:
    metadata = bundle.metadata
    item = {
        "video_id": metadata.video_id,
        "title": metadata.title,
        "channel": metadata.channel,
        "video_url": metadata.url,
        "published_at": metadata.published_at.isoformat() if metadata.published_at else metadata.upload_date,
        "duration_seconds": metadata.duration_seconds,
        "view_count": metadata.view_count,
        "status": status,
        "metadata_path": _relative_artifact_path(video_dir / "metadata.json", run_dir),
        "draft_report_path": _relative_artifact_path(video_dir / "draft_report.md", run_dir),
        "verification_path": _relative_artifact_path(video_dir / "verification.json", run_dir),
        "final_report_path": _relative_artifact_path(video_dir / "final_report.md", run_dir),
        "public_summary_path": _relative_artifact_path(video_dir / "public_summary.json", run_dir),
    }
    if error:
        item["error"] = error
    return item


def _metadata_payload(bundle: YouTubeVideoBundle) -> dict[str, Any]:
    metadata = asdict(bundle.metadata)
    published_at = bundle.metadata.published_at
    metadata["published_at"] = published_at.isoformat() if published_at else None
    return {
        "metadata": metadata,
        "transcript_status": bundle.transcript_status,
        "transcript_source": getattr(bundle.transcript, "source", None),
        "transcript_language": getattr(bundle.transcript, "language_name", None),
        "available_manual_caption_languages": list(bundle.available_manual_caption_languages),
        "available_auto_caption_languages": list(bundle.available_auto_caption_languages),
        "raw_transcript_archived": False,
    }


def _public_summary(bundle: YouTubeVideoBundle, verified: VerifiedVideoReport) -> dict[str, Any]:
    verification = verified.verification
    entities = []
    for item in verification.get("entity_results") or []:
        if not isinstance(item, dict):
            continue
        entities.append(
            {
                "ticker": item.get("ticker"),
                "name": item.get("name"),
                "status": item.get("status"),
                "claims": [_short_text(value, 220) for value in (item.get("claims") or [])[:3]],
                "numeric_claims": [_short_text(value, 220) for value in (item.get("numeric_claims") or [])[:3]],
                "verification_notes": [_short_text(value, 220) for value in (item.get("verification_notes") or [])[:4]],
                "market_snapshot": _public_market_snapshot(item.get("market_snapshot") or {}),
                "external_context_status": (item.get("external_context") or {}).get("status")
                if isinstance(item.get("external_context"), dict)
                else None,
            }
        )
    return {
        "version": 1,
        "video_id": bundle.metadata.video_id,
        "title": bundle.metadata.title,
        "url": bundle.metadata.url,
        "channel": bundle.metadata.channel,
        "published_at": bundle.metadata.published_at.isoformat() if bundle.metadata.published_at else bundle.metadata.upload_date,
        "status": verified.status,
        "generated_at": verification.get("generated_at"),
        "llm_status": verification.get("llm_status"),
        "entities": entities,
        "source_policy": verification.get("source_policy"),
    }


def _public_market_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    allowed = (
        "ticker",
        "as_of",
        "current_price",
        "market_cap",
        "forward_pe",
        "trailing_pe",
        "fifty_two_week_high",
        "fifty_two_week_low",
        "average_target_price",
        "source",
        "status",
    )
    return {key: snapshot.get(key) for key in allowed if key in snapshot}


def _relative_artifact_path(path: Path, run_dir: Path) -> str:
    return path.resolve().relative_to(run_dir.resolve()).as_posix()


def _build_run_id(started_at: datetime) -> str:
    return f"youtube_{started_at.strftime('%Y%m%d_%H%M%S')}"


def _split_csv(value: str | None) -> tuple[str, ...] | None:
    if not value:
        return None
    items = tuple(item.strip() for item in value.split(",") if item.strip())
    return items or None


def _short_text(value: Any, limit: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_safe(payload), ensure_ascii=False, indent=2), encoding="utf-8")


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value


if __name__ == "__main__":
    raise SystemExit(main())
