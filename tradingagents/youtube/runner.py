from __future__ import annotations

import argparse
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
import inspect
import json
import os
from pathlib import Path
import re
import shutil
from time import perf_counter
from typing import Any, Callable, Iterable
from zoneinfo import ZoneInfo

from tradingagents.dataflows.youtube_video import YouTubeVideoBundle, assess_transcript_reliability, fetch_youtube_video
from tradingagents.youtube.channel import (
    YouTubeVideoReference,
    dedupe_video_references,
    filter_references_by_window,
    list_channel_video_references,
)
from tradingagents.youtube.config import ASRSettings, YouTubeDailyConfig, load_youtube_config, with_youtube_overrides
from tradingagents.youtube.research import public_evidence_summary
from tradingagents.youtube.site import build_youtube_site
from tradingagents.youtube.verifier import RESEARCH_PIPELINE_VERSION, VerifiedVideoReport, verify_youtube_bundle
from tradingagents.youtube_report import build_youtube_video_report


ReferenceLister = Callable[[Iterable[str], int], tuple[YouTubeVideoReference, ...]]
VideoFetcher = Callable[..., YouTubeVideoBundle]
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
    parser.add_argument("--max-entries-per-url", type=int, help="Maximum flat-list entries to inspect per channel tab URL.")
    parser.add_argument("--max-parallel-videos", type=int, help="Maximum YouTube videos to process concurrently.")
    parser.add_argument("--publish", dest="publish", action="store_true", default=True, help="Build public site after run.")
    parser.add_argument("--no-publish", dest="publish", action="store_false", help="Skip public site build after run.")
    args = parser.parse_args(argv)

    config = with_youtube_overrides(
        load_youtube_config(args.config),
        archive_dir=args.archive_dir,
        site_dir=args.site_dir,
        lookback_hours=args.lookback_hours,
        max_videos=args.max_videos,
        max_entries_per_url=args.max_entries_per_url,
        max_parallel_videos=args.max_parallel_videos,
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
    _apply_asr_environment(config.asr)
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

    raw_references = lister(config.channel.urls, max(1, int(config.channel.max_entries_per_url or 1)))
    references = filter_references_by_window(
        dedupe_video_references(raw_references),
        now=started_at,
        lookback_hours=config.channel.lookback_hours,
        include_unknown_dates=True,
    )

    video_results = _run_video_workers(
        config=config,
        references=references,
        run_dir=run_dir,
        window_start=window_start,
        window_end=window_end,
        started_at=started_at,
        fetcher=fetcher,
        verifier=verifier,
    )
    video_summaries = [
        result["manifest_item"]
        for _, result in sorted(video_results.items())
        if isinstance(result.get("manifest_item"), dict)
    ]
    selected_count = sum(int(result.get("selected", 0)) for result in video_results.values())
    failed_count = sum(int(result.get("failed", 0)) for result in video_results.values())
    skipped_count = sum(int(result.get("skipped_out_of_window", 0)) for result in video_results.values())
    reused_count = sum(int(result.get("reused", 0)) for result in video_results.values())
    metadata_fetch_failures = sum(int(result.get("metadata_fetch_failures", 0)) for result in video_results.values())
    transcript_fetch_failures = sum(int(result.get("transcript_fetch_failures", 0)) for result in video_results.values())
    skipped_no_transcript = sum(int(result.get("skipped_no_transcript", 0)) for result in video_results.values())

    successful_count = sum(1 for item in video_summaries if item.get("status") not in {"failed"})
    manifest = {
        "version": 1,
        "run_id": run_id,
        "status": "success" if failed_count == 0 else "partial_failure",
        "channel_name": config.channel.name,
        "channel_urls": list(config.channel.urls),
        "timezone": config.channel.timezone,
        "lookback_hours": config.channel.lookback_hours,
        "max_entries_per_url": config.channel.max_entries_per_url,
        "started_at": started_at.isoformat(),
        "finished_at": datetime.now(tz).isoformat(),
        "duration_seconds": round(perf_counter() - timer_start, 3),
        "window_start": window_start.isoformat(),
        "window_end": window_end.isoformat(),
        "summary": {
            "raw_references": len(raw_references),
            "candidate_references": len(references),
            "selected_videos": selected_count,
            "total_videos": len(video_summaries),
            "successful_videos": successful_count,
            "failed_videos": failed_count,
            "reused_videos": reused_count,
            "skipped_out_of_window": skipped_count,
            "metadata_fetch_failures": metadata_fetch_failures,
            "transcript_fetch_failures": transcript_fetch_failures,
            "skipped_no_transcript": skipped_no_transcript,
        },
        "parallel_video_execution": {
            "enabled": config.channel.max_parallel_videos > 1,
            "max_parallel_videos": max(1, int(config.channel.max_parallel_videos or 1)),
        },
        "videos": video_summaries,
        "source_policy": {
            "raw_transcript_archived": False,
            "raw_transcript_published": False,
            "research_pipeline_version": RESEARCH_PIPELINE_VERSION,
            "public_artifacts": ["html_report", "public_summary_json", "evidence_excerpts"],
        },
    }
    _write_json(run_dir / "youtube_run.json", manifest)
    _write_json(config.storage.archive_dir / "latest-youtube-run.json", manifest)
    if publish:
        build_youtube_site(config.storage.archive_dir, config.storage.site_dir, config.site)
    return manifest


def _run_video_workers(
    *,
    config: YouTubeDailyConfig,
    references: list[YouTubeVideoReference],
    run_dir: Path,
    window_start: datetime,
    window_end: datetime,
    started_at: datetime,
    fetcher: VideoFetcher,
    verifier: BundleVerifier,
) -> dict[int, dict[str, Any]]:
    max_workers = min(max(1, int(config.channel.max_parallel_videos or 1)), max(1, config.channel.max_videos))
    if not references:
        return {}
    pending: list[tuple[int, YouTubeVideoReference]] = list(enumerate(references))
    running: dict[Future[dict[str, Any]], int] = {}
    results: dict[int, dict[str, Any]] = {}
    selected_count = 0
    print(
        f"Starting YouTube video execution: max_parallel_videos={max_workers}, "
        f"max_videos={config.channel.max_videos}",
        flush=True,
    )
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="youtube-report") as executor:
        while pending or running:
            while pending and len(running) < max_workers and selected_count + len(running) < config.channel.max_videos:
                index, reference = pending.pop(0)
                future = executor.submit(
                    _process_video_reference,
                    config=config,
                    reference=reference,
                    run_dir=run_dir,
                    window_start=window_start,
                    window_end=window_end,
                    started_at=started_at,
                    fetcher=fetcher,
                    verifier=verifier,
                )
                running[future] = index
            if not running:
                break
            done, _ = wait(running.keys(), return_when=FIRST_COMPLETED)
            for future in done:
                index = running.pop(future)
                try:
                    result = future.result()
                except Exception as exc:
                    reference = references[index]
                    video_dir = run_dir / "videos" / reference.video_id
                    result = _video_worker_crash_result(reference, video_dir=video_dir, run_dir=run_dir, error=str(exc))
                results[index] = result
                selected_count += int(result.get("selected", 0))
                status = result.get("status") or result.get("reason") or "unknown"
                print(
                    f"Finished YouTube candidate {index + 1}/{len(references)}: "
                    f"{references[index].video_id} status={status}",
                    flush=True,
                )
            if selected_count >= config.channel.max_videos:
                pending.clear()
    return results


def _process_video_reference(
    *,
    config: YouTubeDailyConfig,
    reference: YouTubeVideoReference,
    run_dir: Path,
    window_start: datetime,
    window_end: datetime,
    started_at: datetime,
    fetcher: VideoFetcher,
    verifier: BundleVerifier,
) -> dict[str, Any]:
    video_dir = run_dir / "videos" / reference.video_id
    video_dir.mkdir(parents=True, exist_ok=True)
    metadata_bundle: YouTubeVideoBundle | None = None
    result = _empty_video_worker_result()
    try:
        should_fetch_transcript_first = _reference_in_window(
            reference,
            window_start=window_start,
            window_end=window_end,
        )
        if should_fetch_transcript_first:
            result["selected"] = 1
            reused_result = _reuse_video_result_if_possible(
                result=result,
                config=config,
                reference=reference,
                run_dir=run_dir,
                video_dir=video_dir,
            )
            if reused_result is not None:
                return reused_result
        else:
            metadata_bundle = _call_video_fetcher(fetcher, reference.url, fetch_transcript=False)
            if not _bundle_in_window(metadata_bundle, window_start=window_start, window_end=window_end):
                result["skipped_out_of_window"] = 1
                result["status"] = "skipped_out_of_window"
                return result
            result["selected"] = 1
            reused_result = _reuse_video_result_if_possible(
                result=result,
                config=config,
                reference=reference,
                run_dir=run_dir,
                video_dir=video_dir,
            )
            if reused_result is not None:
                return reused_result

        if should_fetch_transcript_first:
            try:
                metadata_bundle = _call_video_fetcher(fetcher, reference.url, fetch_transcript=True)
            except Exception:
                result["metadata_fetch_failures"] = 1
                raise
        if not _bundle_in_window(metadata_bundle, window_start=window_start, window_end=window_end):
            result["selected"] = 0
            result["skipped_out_of_window"] = 1
            result["status"] = "skipped_out_of_window"
            return result
        try:
            bundle = (
                metadata_bundle
                if metadata_bundle.transcript is not None and metadata_bundle.transcript_status == "available"
                else _call_video_fetcher(fetcher, reference.url, fetch_transcript=True)
            )
        except Exception:
            result["transcript_fetch_failures"] = 1
            bundle = metadata_bundle
        if not _bundle_has_usable_transcript(bundle):
            result["skipped_no_transcript"] = 1
            result["status"] = "skipped_no_transcript"
            _write_json(video_dir / "metadata.json", _metadata_payload(bundle))
            _write_json(
                video_dir / "collection_status.json",
                {
                    "video_id": bundle.metadata.video_id,
                    "title": bundle.metadata.title,
                    "video_url": bundle.metadata.url,
                    "status": "skipped_no_transcript",
                    "reason": "usable transcript or ASR text was not available",
                    "transcript_status": bundle.transcript_status,
                    "transcript_chars": len(bundle.transcript.raw_text) if bundle.transcript else 0,
                    "minimum_transcript_chars": _minimum_transcript_chars(),
                },
            )
            return result
        draft_report = build_youtube_video_report(bundle, generated_at=started_at.replace(tzinfo=None))
        verified = verifier(bundle, draft_report, started_at)
        _write_text(video_dir / "draft_report.md", draft_report)
        _write_text(video_dir / "final_report.md", verified.final_report_markdown)
        _write_json(video_dir / "metadata.json", _metadata_payload(bundle))
        _write_json(video_dir / "verification.json", verified.verification)
        _write_json(video_dir / "research_plan.json", verified.verification.get("research_plan") or {})
        _write_json(video_dir / "evidence.json", verified.verification.get("evidence") or {})
        _write_json(video_dir / "claim_verification.json", verified.verification.get("claim_verification") or {})
        public_summary = _public_summary(bundle, verified)
        _write_json(video_dir / "public_summary.json", public_summary)
        result["status"] = verified.status
        result["manifest_item"] = _manifest_video_item(
            bundle=bundle,
            status=verified.status,
            video_dir=video_dir,
            run_dir=run_dir,
            error=None,
            reused_from_run=None,
        )
        return result
    except Exception as exc:
        if metadata_bundle is None:
            result["metadata_fetch_failures"] = 1
        result["selected"] = 1
        result["failed"] = 1
        result["status"] = "failed"
        result["manifest_item"] = _write_failed_video_artifacts(
            reference,
            video_dir=video_dir,
            run_dir=run_dir,
            error=str(exc),
        )
        return result


def _reuse_video_result_if_possible(
    *,
    result: dict[str, Any],
    config: YouTubeDailyConfig,
    reference: YouTubeVideoReference,
    run_dir: Path,
    video_dir: Path,
) -> dict[str, Any] | None:
    reused = _copy_reusable_video_artifacts(
        archive_dir=config.storage.archive_dir,
        video_id=reference.video_id,
        current_run_dir=run_dir,
        target_video_dir=video_dir,
    )
    if reused is None:
        return None
    result["reused"] = 1
    status = str(reused.get("status") or "reused")
    result["status"] = status
    result["manifest_item"] = _manifest_video_item_from_reused_artifacts(
        reference,
        status=status,
        video_dir=video_dir,
        run_dir=run_dir,
        reused_from_run=str(reused.get("run_id") or ""),
    )
    return result


def _empty_video_worker_result() -> dict[str, Any]:
    return {
        "selected": 0,
        "failed": 0,
        "skipped_out_of_window": 0,
        "reused": 0,
        "metadata_fetch_failures": 0,
        "transcript_fetch_failures": 0,
        "skipped_no_transcript": 0,
        "status": "",
        "manifest_item": None,
    }


def _video_worker_crash_result(
    reference: YouTubeVideoReference,
    *,
    video_dir: Path,
    run_dir: Path,
    error: str,
) -> dict[str, Any]:
    result = _empty_video_worker_result()
    result["selected"] = 1
    result["failed"] = 1
    result["metadata_fetch_failures"] = 1
    result["status"] = "failed"
    result["manifest_item"] = _write_failed_video_artifacts(reference, video_dir=video_dir, run_dir=run_dir, error=error)
    return result


def _write_failed_video_artifacts(
    reference: YouTubeVideoReference,
    *,
    video_dir: Path,
    run_dir: Path,
    error: str,
) -> dict[str, Any]:
    video_dir.mkdir(parents=True, exist_ok=True)
    error_summary = {
        "video_id": reference.video_id,
        "title": reference.title,
        "video_url": reference.url,
        "published_at": reference.published_at.isoformat() if reference.published_at else None,
        "status": "failed",
        "error": error,
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
            "collection_error": error,
        },
    )
    _write_json(video_dir / "public_summary.json", error_summary)
    return error_summary


def execute_single_video(
    config: YouTubeDailyConfig,
    video_url: str,
    *,
    verify: bool,
    out: str | None = None,
) -> Path:
    _apply_asr_environment(config.asr)
    generated_at = datetime.now(ZoneInfo(config.channel.timezone))
    bundle = fetch_youtube_video(video_url)
    if not _bundle_has_usable_transcript(bundle):
        raise RuntimeError(
            "Usable transcript or ASR text was not available; report generation was skipped for this video."
        )
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
        _write_json(output.with_name(output.stem + "_research_plan.json"), verified.verification.get("research_plan") or {})
        _write_json(output.with_name(output.stem + "_evidence.json"), verified.verification.get("evidence") or {})
        _write_json(output.with_name(output.stem + "_claim_verification.json"), verified.verification.get("claim_verification") or {})
        _write_json(output.with_name(output.stem + "_public_summary.json"), _public_summary(bundle, verified))
    return output


def _default_reference_lister(channel_urls: Iterable[str], max_entries_per_url: int) -> tuple[YouTubeVideoReference, ...]:
    return list_channel_video_references(channel_urls, max_entries_per_url=max_entries_per_url)


def _apply_asr_environment(settings: ASRSettings) -> None:
    values = {
        "TRADINGAGENTS_YOUTUBE_ASR_FALLBACK": "1" if settings.enabled else "0",
        "TRADINGAGENTS_YOUTUBE_ASR_MODEL": settings.model,
        "TRADINGAGENTS_YOUTUBE_ASR_DEVICE": settings.device,
        "TRADINGAGENTS_YOUTUBE_ASR_COMPUTE_TYPE": settings.compute_type,
        "TRADINGAGENTS_YOUTUBE_ASR_FALLBACK_MODELS": ",".join(settings.fallback_models),
        "TRADINGAGENTS_YOUTUBE_ASR_BEAM_SIZE": str(settings.beam_size),
        "TRADINGAGENTS_YOUTUBE_ASR_BEST_OF": str(settings.best_of),
        "TRADINGAGENTS_YOUTUBE_ASR_TEMPERATURE": settings.temperature,
        "TRADINGAGENTS_YOUTUBE_ASR_CONDITION_ON_PREVIOUS_TEXT": "1" if settings.condition_on_previous_text else "0",
        "TRADINGAGENTS_YOUTUBE_ASR_REPETITION_PENALTY": str(settings.repetition_penalty),
        "TRADINGAGENTS_YOUTUBE_ASR_NO_REPEAT_NGRAM_SIZE": str(settings.no_repeat_ngram_size),
        "TRADINGAGENTS_YOUTUBE_ASR_WORD_TIMESTAMPS": "1" if settings.word_timestamps else "0",
        "TRADINGAGENTS_YOUTUBE_ASR_HALLUCINATION_SILENCE_THRESHOLD": str(settings.hallucination_silence_threshold),
        "TRADINGAGENTS_YOUTUBE_ASR_VAD_FILTER": "1" if settings.vad_filter else "0",
        "TRADINGAGENTS_YOUTUBE_ASR_VAD_MIN_SILENCE_MS": str(settings.vad_min_silence_ms),
        "TRADINGAGENTS_YOUTUBE_ASR_VAD_SPEECH_PAD_MS": str(settings.vad_speech_pad_ms),
        "TRADINGAGENTS_YOUTUBE_ASR_VAD_THRESHOLD": str(settings.vad_threshold),
        "TRADINGAGENTS_YOUTUBE_ASR_MIN_QUALITY": settings.min_quality,
        "TRADINGAGENTS_YOUTUBE_ASR_RECHECK_AUTOMATIC": "1" if settings.recheck_automatic else "0",
        "TRADINGAGENTS_YOUTUBE_TRANSCRIPT_CHUNK_CHARS": str(settings.chunk_chars),
        "TRADINGAGENTS_YOUTUBE_TRANSCRIPT_MAX_CHUNKS": str(settings.max_chunks),
        "TRADINGAGENTS_YOUTUBE_TRANSCRIPT_MIN_COVERAGE_CHUNKS": str(settings.min_coverage_chunks),
    }
    if settings.hotwords:
        values["TRADINGAGENTS_YOUTUBE_ASR_HOTWORDS"] = ",".join(settings.hotwords)
    if settings.initial_prompt:
        values["TRADINGAGENTS_YOUTUBE_ASR_INITIAL_PROMPT"] = settings.initial_prompt
    for key, value in values.items():
        if str(value).strip():
            os.environ.setdefault(key, str(value))


def _call_video_fetcher(fetcher: VideoFetcher, url: str, *, fetch_transcript: bool) -> YouTubeVideoBundle:
    try:
        signature = inspect.signature(fetcher)
    except (TypeError, ValueError):
        signature = None
    if signature is not None:
        accepts_fetch_transcript = "fetch_transcript" in signature.parameters or any(
            parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in signature.parameters.values()
        )
        if not accepts_fetch_transcript:
            return fetcher(url)
    try:
        return fetcher(url, fetch_transcript=fetch_transcript)
    except TypeError as exc:
        if "fetch_transcript" not in str(exc):
            raise
        return fetcher(url)


def _default_bundle_verifier(config: YouTubeDailyConfig) -> BundleVerifier:
    def verify(bundle: YouTubeVideoBundle, draft_report: str, generated_at: datetime) -> VerifiedVideoReport:
        return verify_youtube_bundle(
            bundle,
            draft_report,
            llm_settings=_llm_settings_for_video(config, bundle.metadata.video_id),
            verification_settings=config.verification,
            generated_at=generated_at,
        )

    return verify


def _llm_settings_for_video(config: YouTubeDailyConfig, video_id: str) -> Any:
    workspace = str(config.llm.codex_workspace_dir or "").strip()
    if not workspace:
        return config.llm
    video_workspace = Path(workspace) / "youtube-videos" / _safe_segment(video_id or "video")
    return replace(config.llm, codex_workspace_dir=str(video_workspace))


def _safe_segment(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(value or "").strip()).strip(".-")
    return text[:80] or "video"


def _reference_in_window(reference: YouTubeVideoReference, *, window_start: datetime, window_end: datetime) -> bool:
    published_at = reference.published_at
    if published_at is None:
        return False
    comparable = _to_timezone(published_at, window_end.tzinfo)
    return window_start <= comparable <= window_end


def _bundle_in_window(bundle: YouTubeVideoBundle, *, window_start: datetime, window_end: datetime) -> bool:
    published_at = bundle.metadata.published_at
    if published_at is None:
        return False
    comparable = _to_timezone(published_at, window_end.tzinfo)
    return window_start <= comparable <= window_end


def _bundle_has_usable_transcript(bundle: YouTubeVideoBundle) -> bool:
    text = bundle.transcript.raw_text if bundle.transcript else ""
    return len(" ".join(str(text or "").split())) >= _minimum_transcript_chars()


def _minimum_transcript_chars() -> int:
    try:
        return max(1, int(float(os.getenv("TRADINGAGENTS_YOUTUBE_MIN_TRANSCRIPT_CHARS", "120"))))
    except (TypeError, ValueError):
        return 120


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
    reused_from_run: str | None = None,
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
        "transcript_status": bundle.transcript_status,
        "transcript_source": getattr(bundle.transcript, "source", None),
        "transcript_chars": len(bundle.transcript.raw_text) if bundle.transcript else 0,
        "metadata_path": _relative_artifact_path(video_dir / "metadata.json", run_dir),
        "draft_report_path": _relative_artifact_path(video_dir / "draft_report.md", run_dir),
        "verification_path": _relative_artifact_path(video_dir / "verification.json", run_dir),
        "research_plan_path": _relative_artifact_path(video_dir / "research_plan.json", run_dir),
        "evidence_path": _relative_artifact_path(video_dir / "evidence.json", run_dir),
        "claim_verification_path": _relative_artifact_path(video_dir / "claim_verification.json", run_dir),
        "final_report_path": _relative_artifact_path(video_dir / "final_report.md", run_dir),
        "public_summary_path": _relative_artifact_path(video_dir / "public_summary.json", run_dir),
    }
    if error:
        item["error"] = error
    if reused_from_run:
        item["reused_from_run"] = reused_from_run
    return item


def _manifest_video_item_from_reused_artifacts(
    reference: YouTubeVideoReference,
    *,
    status: str,
    video_dir: Path,
    run_dir: Path,
    reused_from_run: str | None,
) -> dict[str, Any]:
    summary = _read_json_if_exists(video_dir / "public_summary.json") or {}
    metadata_payload = _read_json_if_exists(video_dir / "metadata.json") or {}
    metadata = metadata_payload.get("metadata") if isinstance(metadata_payload.get("metadata"), dict) else {}
    item = {
        "video_id": summary.get("video_id") or metadata.get("video_id") or reference.video_id,
        "title": summary.get("title") or metadata.get("title") or reference.title,
        "channel": summary.get("channel") or metadata.get("channel"),
        "video_url": summary.get("url") or metadata.get("url") or reference.url,
        "published_at": summary.get("published_at")
        or metadata.get("published_at")
        or (reference.published_at.isoformat() if reference.published_at else None),
        "duration_seconds": metadata.get("duration_seconds"),
        "view_count": metadata.get("view_count"),
        "status": status,
        "transcript_status": summary.get("transcript_status") or metadata_payload.get("transcript_status"),
        "transcript_source": summary.get("transcript_source") or metadata_payload.get("transcript_source"),
        "transcript_chars": summary.get("transcript_chars") or metadata_payload.get("transcript_chars") or 0,
        "metadata_path": _relative_artifact_path(video_dir / "metadata.json", run_dir),
        "draft_report_path": _relative_artifact_path(video_dir / "draft_report.md", run_dir),
        "verification_path": _relative_artifact_path(video_dir / "verification.json", run_dir),
        "research_plan_path": _relative_artifact_path(video_dir / "research_plan.json", run_dir),
        "evidence_path": _relative_artifact_path(video_dir / "evidence.json", run_dir),
        "claim_verification_path": _relative_artifact_path(video_dir / "claim_verification.json", run_dir),
        "final_report_path": _relative_artifact_path(video_dir / "final_report.md", run_dir),
        "public_summary_path": _relative_artifact_path(video_dir / "public_summary.json", run_dir),
    }
    if reused_from_run:
        item["reused_from_run"] = reused_from_run
    return item


def _copy_reusable_video_artifacts(
    *,
    archive_dir: Path,
    video_id: str,
    current_run_dir: Path,
    target_video_dir: Path,
) -> dict[str, Any] | None:
    candidates = sorted(
        Path(archive_dir).glob(f"runs/*/*/videos/{video_id}/public_summary.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for summary_path in candidates:
        source_video_dir = summary_path.parent
        if source_video_dir.resolve() == target_video_dir.resolve():
            continue
        if _is_relative_to(source_video_dir.resolve(), current_run_dir.resolve()):
            continue
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(summary, dict) or summary.get("status") == "failed":
            continue
        if not _archived_summary_has_usable_transcript(source_video_dir, summary):
            continue
        required = (
            "metadata.json",
            "draft_report.md",
            "verification.json",
            "research_plan.json",
            "evidence.json",
            "claim_verification.json",
            "final_report.md",
            "public_summary.json",
        )
        if not all((source_video_dir / name).is_file() for name in required):
            continue
        verification = _read_json_if_exists(source_video_dir / "verification.json")
        if not _archived_verification_is_current(verification):
            continue
        if target_video_dir.exists():
            shutil.rmtree(target_video_dir)
        shutil.copytree(source_video_dir, target_video_dir)
        return {
            "status": summary.get("status"),
            "run_id": _run_id_from_video_dir(source_video_dir),
        }
    return None


def _archived_summary_has_usable_transcript(video_dir: Path, summary: dict[str, Any]) -> bool:
    for payload in (summary, _read_json_if_exists(video_dir / "metadata.json")):
        if not isinstance(payload, dict):
            continue
        status = payload.get("transcript_status")
        if status == "available":
            chars = payload.get("transcript_chars")
            if chars is None:
                metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
                chars = metadata.get("transcript_chars") if isinstance(metadata, dict) else None
            try:
                return chars is None or int(chars) >= _minimum_transcript_chars()
            except (TypeError, ValueError):
                return True
        if status and status != "available":
            return False
    return False


def _archived_verification_is_current(verification: dict[str, Any] | None) -> bool:
    if not isinstance(verification, dict):
        return False
    try:
        version = int(verification.get("version") or 0)
    except (TypeError, ValueError):
        return False
    return version >= RESEARCH_PIPELINE_VERSION and isinstance(verification.get("evidence"), dict)


def _read_json_if_exists(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _run_id_from_video_dir(video_dir: Path) -> str:
    try:
        return video_dir.parents[1].name
    except IndexError:
        return ""


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _metadata_payload(bundle: YouTubeVideoBundle) -> dict[str, Any]:
    metadata = asdict(bundle.metadata)
    published_at = bundle.metadata.published_at
    metadata["published_at"] = published_at.isoformat() if published_at else None
    transcript_quality = assess_transcript_reliability(bundle.transcript, duration_seconds=bundle.metadata.duration_seconds)
    return {
        "metadata": metadata,
        "transcript_status": bundle.transcript_status,
        "transcript_source": getattr(bundle.transcript, "source", None),
        "transcript_language": getattr(bundle.transcript, "language_name", None),
        "transcript_chars": len(bundle.transcript.raw_text) if bundle.transcript else 0,
        "transcript_quality": transcript_quality,
        "available_manual_caption_languages": list(bundle.available_manual_caption_languages),
        "available_auto_caption_languages": list(bundle.available_auto_caption_languages),
        "raw_transcript_archived": False,
    }


def _public_summary(bundle: YouTubeVideoBundle, verified: VerifiedVideoReport) -> dict[str, Any]:
    verification = verified.verification
    claim_verification = verification.get("claim_verification") if isinstance(verification.get("claim_verification"), dict) else {}
    evidence = verification.get("evidence") if isinstance(verification.get("evidence"), dict) else {}
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
    claims = []
    for item in claim_verification.get("claims") or []:
        if not isinstance(item, dict):
            continue
        claims.append(
            {
                "claim_id": item.get("claim_id"),
                "claim_text": _short_text(item.get("claim_text"), 260),
                "status": item.get("status"),
                "confidence": item.get("confidence"),
                "supporting_evidence_ids": list(item.get("supporting_evidence_ids") or [])[:4],
                "manual_check_required": item.get("manual_check_required"),
                "timestamp": item.get("timestamp"),
                "source_confidence": item.get("source_confidence"),
                "asr_confidence": item.get("asr_confidence"),
                "numeric_parse": item.get("numeric_parse") if isinstance(item.get("numeric_parse"), dict) else {},
                "investor_implication": _short_text(item.get("investor_implication"), 260),
            }
        )
    return {
        "version": RESEARCH_PIPELINE_VERSION,
        "video_id": bundle.metadata.video_id,
        "title": bundle.metadata.title,
        "url": bundle.metadata.url,
        "channel": bundle.metadata.channel,
        "published_at": bundle.metadata.published_at.isoformat() if bundle.metadata.published_at else bundle.metadata.upload_date,
        "status": verified.status,
        "transcript_status": bundle.transcript_status,
        "transcript_source": getattr(bundle.transcript, "source", None),
        "transcript_chars": len(bundle.transcript.raw_text) if bundle.transcript else 0,
        "transcript_quality": assess_transcript_reliability(bundle.transcript, duration_seconds=bundle.metadata.duration_seconds),
        "generated_at": verification.get("generated_at"),
        "llm_status": verification.get("llm_status"),
        "research_status": verification.get("research_status"),
        "claim_verification_status": verification.get("claim_verification_status"),
        "research_pipeline_version": verification.get("version"),
        "evidence_count": evidence.get("evidence_count"),
        "claim_status_summary": _claim_status_summary(claims),
        "claims": claims[:12],
        "entities": entities,
        "evidence": public_evidence_summary(evidence, per_claim_limit=2)[:12],
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


def _claim_status_summary(claims: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for claim in claims:
        status = str(claim.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


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
