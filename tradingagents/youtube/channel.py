from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

from tradingagents.dataflows.youtube_video import YOUTUBE_VIDEO_URL, extract_youtube_video_id


@dataclass(frozen=True)
class YouTubeVideoReference:
    video_id: str
    url: str
    title: str
    source_url: str
    published_at: datetime | None = None


def list_channel_video_references(
    channel_urls: Iterable[str],
    *,
    max_entries_per_url: int = 100,
) -> tuple[YouTubeVideoReference, ...]:
    yt_dlp = _import_ytdlp()
    references: list[YouTubeVideoReference] = []
    for channel_url in channel_urls:
        url = str(channel_url or "").strip()
        if not url:
            continue
        options = {
            "extract_flat": True,
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
            "playlistend": max_entries_per_url,
            "ignoreerrors": True,
        }
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
        references.extend(_references_from_entries(info, source_url=url))
    return tuple(dedupe_video_references(references))


def dedupe_video_references(references: Iterable[YouTubeVideoReference]) -> list[YouTubeVideoReference]:
    deduped: list[YouTubeVideoReference] = []
    seen: set[str] = set()
    for reference in references:
        if not reference.video_id or reference.video_id in seen:
            continue
        seen.add(reference.video_id)
        deduped.append(reference)
    return deduped


def filter_references_by_window(
    references: Iterable[YouTubeVideoReference],
    *,
    now: datetime,
    lookback_hours: int,
    include_unknown_dates: bool = True,
) -> list[YouTubeVideoReference]:
    window_start = now - timedelta(hours=max(1, int(lookback_hours)))
    selected: list[YouTubeVideoReference] = []
    for reference in references:
        published_at = reference.published_at
        if published_at is None:
            if include_unknown_dates:
                selected.append(reference)
            continue
        comparable = published_at
        if comparable.tzinfo is None and now.tzinfo is not None:
            comparable = comparable.replace(tzinfo=now.tzinfo)
        elif comparable.tzinfo is not None and now.tzinfo is not None:
            comparable = comparable.astimezone(now.tzinfo)
        if window_start <= comparable <= now:
            selected.append(reference)
    return selected


def _references_from_entries(info: dict[str, Any] | None, *, source_url: str) -> list[YouTubeVideoReference]:
    entries = (info or {}).get("entries") or []
    references: list[YouTubeVideoReference] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        reference = _reference_from_entry(entry, source_url=source_url)
        if reference is not None:
            references.append(reference)
    return references


def _reference_from_entry(entry: dict[str, Any], *, source_url: str) -> YouTubeVideoReference | None:
    video_id = ""
    for candidate in (entry.get("id"), entry.get("url"), entry.get("webpage_url")):
        if not candidate:
            continue
        try:
            video_id = extract_youtube_video_id(str(candidate))
            break
        except ValueError:
            if isinstance(candidate, str) and len(candidate) == 11:
                video_id = candidate
                break
    if not video_id:
        return None
    return YouTubeVideoReference(
        video_id=video_id,
        url=YOUTUBE_VIDEO_URL.format(video_id=video_id),
        title=str(entry.get("title") or ""),
        source_url=source_url,
        published_at=_entry_datetime(entry),
    )


def _entry_datetime(entry: dict[str, Any]) -> datetime | None:
    for key in ("timestamp", "release_timestamp", "modified_timestamp"):
        value = entry.get(key)
        if value not in (None, ""):
            try:
                return datetime.fromtimestamp(float(value), tz=timezone.utc)
            except (OSError, OverflowError, TypeError, ValueError):
                pass
    upload_date = str(entry.get("upload_date") or "").strip()
    if len(upload_date) == 8 and upload_date.isdigit():
        try:
                return datetime.strptime(upload_date, "%Y%m%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def _import_ytdlp() -> Any:
    try:
        import yt_dlp  # type: ignore
    except ImportError as exc:
        raise RuntimeError("yt-dlp is required for YouTube channel collection.") from exc
    return yt_dlp
