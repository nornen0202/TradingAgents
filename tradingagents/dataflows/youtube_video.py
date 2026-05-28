from __future__ import annotations

from http.cookiejar import MozillaCookieJar
from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
import json
import os
import re
import time
from typing import Any, Iterable
from urllib.parse import parse_qs, urlparse

import requests


YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v={video_id}"
_VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
_CAPTION_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}
_CAPTION_LAST_REQUEST_AT = 0.0
_CAPTION_SESSIONS: dict[str, requests.Session] = {}


@dataclass(frozen=True)
class YouTubeTranscriptSegment:
    start_seconds: float
    duration_seconds: float
    text: str


@dataclass(frozen=True)
class YouTubeTranscript:
    language: str
    language_name: str
    source: str
    segments: tuple[YouTubeTranscriptSegment, ...]
    raw_text: str
    track_ext: str = ""


@dataclass(frozen=True)
class YouTubeVideoMetadata:
    video_id: str
    url: str
    title: str
    channel: str
    channel_id: str
    upload_date: str | None
    published_at: datetime | None
    duration_seconds: int | None
    view_count: int | None
    like_count: int | None
    description: str
    thumbnail_url: str
    tags: tuple[str, ...]
    categories: tuple[str, ...]


@dataclass(frozen=True)
class YouTubeVideoBundle:
    metadata: YouTubeVideoMetadata
    transcript: YouTubeTranscript | None
    transcript_status: str
    available_manual_caption_languages: tuple[str, ...]
    available_auto_caption_languages: tuple[str, ...]


class YouTubeCollectionError(RuntimeError):
    """Raised when a YouTube video cannot be collected."""


def extract_youtube_video_id(value: str) -> str:
    text = str(value or "").strip()
    if _VIDEO_ID_RE.match(text):
        return text

    parsed = urlparse(text)
    if not parsed.netloc:
        raise ValueError(f"Unsupported YouTube video reference: {value!r}")

    host = parsed.netloc.lower().removeprefix("www.")
    if host == "youtu.be":
        candidate = parsed.path.strip("/").split("/", 1)[0]
        if _VIDEO_ID_RE.match(candidate):
            return candidate

    if "youtube.com" in host:
        query_id = parse_qs(parsed.query).get("v", [""])[0]
        if _VIDEO_ID_RE.match(query_id):
            return query_id
        parts = [part for part in parsed.path.split("/") if part]
        for marker in ("shorts", "embed", "live"):
            if marker in parts:
                index = parts.index(marker)
                if index + 1 < len(parts) and _VIDEO_ID_RE.match(parts[index + 1]):
                    return parts[index + 1]

    raise ValueError(f"Unsupported YouTube video reference: {value!r}")


def fetch_youtube_video(
    url_or_id: str,
    *,
    transcript_languages: Iterable[str] = ("ko", "en"),
    include_auto_captions: bool = True,
    fetch_transcript: bool = True,
    timeout_seconds: float = 30.0,
) -> YouTubeVideoBundle:
    """Fetch metadata and the best available transcript for one YouTube video.

    The implementation uses yt-dlp when it is installed. Public videos often
    expose automatic captions but not owner-managed caption tracks; the caller
    can disable automatic captions if they want a stricter evidence source.
    """

    yt_dlp = _import_ytdlp()
    video_id = extract_youtube_video_id(url_or_id)
    url = YOUTUBE_VIDEO_URL.format(video_id=video_id)
    options = _youtube_dl_options(
        skip_download=True,
        quiet=True,
        no_warnings=True,
        noplaylist=True,
    )

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as exc:  # pragma: no cover - exercised only by live IO
        raise YouTubeCollectionError(f"Failed to fetch YouTube metadata for {url}: {exc}") from exc

    subtitles = info.get("subtitles") or {}
    automatic_captions = info.get("automatic_captions") or {}
    manual_languages = tuple(sorted(str(key) for key in subtitles.keys()))
    auto_languages = tuple(sorted(str(key) for key in automatic_captions.keys()))

    transcript = None
    if fetch_transcript:
        transcript = _fetch_best_transcript(
            subtitles=subtitles,
            automatic_captions=automatic_captions if include_auto_captions else {},
            transcript_languages=tuple(transcript_languages),
            timeout_seconds=timeout_seconds,
        )
    transcript_status = "available" if transcript and transcript.raw_text else "unavailable"
    if not fetch_transcript:
        transcript_status = "skipped"

    return YouTubeVideoBundle(
        metadata=_metadata_from_info(info, video_id=video_id, fallback_url=url),
        transcript=transcript if transcript and transcript.raw_text else None,
        transcript_status=transcript_status,
        available_manual_caption_languages=manual_languages,
        available_auto_caption_languages=auto_languages,
    )


def _import_ytdlp() -> Any:
    try:
        import yt_dlp  # type: ignore
    except ImportError as exc:
        raise YouTubeCollectionError(
            "yt-dlp is required for public YouTube video collection. "
            "Install it in the active environment with: python -m pip install yt-dlp"
        ) from exc
    return yt_dlp


def _youtube_dl_options(**base_options: Any) -> dict[str, Any]:
    options = dict(base_options)
    cookie_file = _youtube_cookie_file()
    if cookie_file:
        options["cookiefile"] = cookie_file
    return options


def _metadata_from_info(info: dict[str, Any], *, video_id: str, fallback_url: str) -> YouTubeVideoMetadata:
    upload_date = _text_or_none(info.get("upload_date"))
    return YouTubeVideoMetadata(
        video_id=str(info.get("id") or video_id),
        url=str(info.get("webpage_url") or fallback_url),
        title=str(info.get("title") or ""),
        channel=str(info.get("channel") or info.get("uploader") or ""),
        channel_id=str(info.get("channel_id") or info.get("uploader_id") or ""),
        upload_date=upload_date,
        published_at=_published_at_from_info(info, upload_date),
        duration_seconds=_optional_int(info.get("duration")),
        view_count=_optional_int(info.get("view_count")),
        like_count=_optional_int(info.get("like_count")),
        description=str(info.get("description") or ""),
        thumbnail_url=str(info.get("thumbnail") or ""),
        tags=tuple(str(item) for item in (info.get("tags") or []) if str(item).strip()),
        categories=tuple(str(item) for item in (info.get("categories") or []) if str(item).strip()),
    )


def _published_at_from_info(info: dict[str, Any], upload_date: str | None) -> datetime | None:
    timestamp = info.get("timestamp") or info.get("release_timestamp")
    if timestamp is not None:
        try:
            return datetime.fromtimestamp(float(timestamp), tz=timezone.utc)
        except (OSError, OverflowError, TypeError, ValueError):
            pass
    if upload_date and re.match(r"^\d{8}$", upload_date):
        try:
            return datetime.strptime(upload_date, "%Y%m%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def _fetch_best_transcript(
    *,
    subtitles: dict[str, list[dict[str, Any]]],
    automatic_captions: dict[str, list[dict[str, Any]]],
    transcript_languages: tuple[str, ...],
    timeout_seconds: float,
) -> YouTubeTranscript | None:
    language_priority = _expand_language_priority(transcript_languages)
    for source, tracks_by_language in (("manual", subtitles), ("automatic", automatic_captions)):
        for language in language_priority:
            tracks = tracks_by_language.get(language)
            if not tracks:
                continue
            track = _select_track_format(tracks)
            if track is None:
                continue
            transcript = _download_transcript_track(
                track,
                language=language,
                source=source,
                timeout_seconds=timeout_seconds,
            )
            if transcript and transcript.raw_text:
                return transcript
    return None


def _expand_language_priority(languages: tuple[str, ...]) -> tuple[str, ...]:
    expanded: list[str] = []
    for language in languages:
        normalized = str(language or "").strip()
        if not normalized:
            continue
        candidates = [normalized]
        if "-" in normalized:
            candidates.append(normalized.split("-", 1)[0])
        if normalized == "ko":
            candidates.extend(["ko-KR", "ko-orig"])
        if normalized == "en":
            candidates.extend(["en-US", "en-orig"])
        for candidate in candidates:
            if candidate not in expanded:
                expanded.append(candidate)
    return tuple(expanded or ["ko", "en"])


def _select_track_format(tracks: list[dict[str, Any]]) -> dict[str, Any] | None:
    preferred_exts = ("json3", "vtt", "srt", "ttml", "srv3", "srv2", "srv1")
    for ext in preferred_exts:
        for track in tracks:
            if str(track.get("ext") or "").lower() == ext and track.get("url"):
                return track
    for track in tracks:
        if track.get("url"):
            return track
    return None


def _download_transcript_track(
    track: dict[str, Any],
    *,
    language: str,
    source: str,
    timeout_seconds: float,
) -> YouTubeTranscript | None:
    url = str(track.get("url") or "")
    if not url:
        return None
    response = _download_caption_response(url, timeout_seconds=timeout_seconds)
    if response is None:
        return None
    payload = response.text
    ext = str(track.get("ext") or "").lower()
    language_name = str(track.get("name") or language)

    if ext == "json3" or payload.lstrip().startswith("{"):
        try:
            segments = _parse_json3_segments(response.json())
        except json.JSONDecodeError:
            segments = ()
    else:
        segments = _parse_text_caption_segments(payload)

    raw_text = clean_transcript_text(" ".join(segment.text for segment in segments))
    if not raw_text:
        return None
    return YouTubeTranscript(
        language=language,
        language_name=language_name,
        source=source,
        segments=segments,
        raw_text=raw_text,
        track_ext=ext,
    )


def _download_caption_response(url: str, *, timeout_seconds: float) -> requests.Response | None:
    max_retries = _env_int("TRADINGAGENTS_YOUTUBE_CAPTION_MAX_RETRIES", 2)
    for attempt in range(max(0, max_retries) + 1):
        _respect_caption_throttle()
        try:
            response = _caption_session().get(url, timeout=timeout_seconds)
        except requests.RequestException:
            return None
        if response.status_code == 429:
            if attempt >= max_retries:
                return None
            time.sleep(_caption_retry_delay(response, attempt))
            continue
        try:
            response.raise_for_status()
        except requests.RequestException:
            return None
        return response
    return None


def _caption_session() -> requests.Session:
    cookie_file = _youtube_cookie_file() or ""
    session = _CAPTION_SESSIONS.get(cookie_file)
    if session is not None:
        return session
    session = requests.Session()
    session.headers.update(_CAPTION_HEADERS)
    if cookie_file:
        try:
            jar = MozillaCookieJar(cookie_file)
            jar.load(ignore_discard=True, ignore_expires=True)
            session.cookies = jar
        except (OSError, ValueError):
            pass
    _CAPTION_SESSIONS[cookie_file] = session
    return session


def _respect_caption_throttle() -> None:
    global _CAPTION_LAST_REQUEST_AT
    interval = _env_float("TRADINGAGENTS_YOUTUBE_CAPTION_INTERVAL_SECONDS", 1.0)
    if interval <= 0:
        _CAPTION_LAST_REQUEST_AT = time.monotonic()
        return
    elapsed = time.monotonic() - _CAPTION_LAST_REQUEST_AT
    if _CAPTION_LAST_REQUEST_AT and elapsed < interval:
        time.sleep(interval - elapsed)
    _CAPTION_LAST_REQUEST_AT = time.monotonic()


def _caption_retry_delay(response: requests.Response, attempt: int) -> float:
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            delay = float(retry_after)
        except ValueError:
            delay = 0.0
        if delay > 0:
            return min(delay, _env_float("TRADINGAGENTS_YOUTUBE_CAPTION_MAX_RETRY_DELAY_SECONDS", 20.0))
    return min(
        2.0 * (attempt + 1),
        _env_float("TRADINGAGENTS_YOUTUBE_CAPTION_MAX_RETRY_DELAY_SECONDS", 20.0),
    )


def _parse_json3_segments(payload: dict[str, Any]) -> tuple[YouTubeTranscriptSegment, ...]:
    segments: list[YouTubeTranscriptSegment] = []
    for event in payload.get("events") or []:
        pieces = event.get("segs") or []
        text = clean_transcript_text("".join(str(piece.get("utf8") or "") for piece in pieces))
        if not text:
            continue
        start_ms = _optional_float(event.get("tStartMs")) or 0.0
        duration_ms = _optional_float(event.get("dDurationMs")) or 0.0
        segments.append(
            YouTubeTranscriptSegment(
                start_seconds=start_ms / 1000.0,
                duration_seconds=duration_ms / 1000.0,
                text=text,
            )
        )
    return tuple(segments)


def _parse_text_caption_segments(payload: str) -> tuple[YouTubeTranscriptSegment, ...]:
    lines = []
    for line in payload.splitlines():
        text = line.strip()
        if not text or "-->" in text or text.isdigit() or text.upper().startswith("WEBVTT"):
            continue
        text = re.sub(r"<[^>]+>", " ", text)
        text = clean_transcript_text(unescape(text))
        if text:
            lines.append(text)
    if not lines:
        return ()
    return (YouTubeTranscriptSegment(start_seconds=0.0, duration_seconds=0.0, text=" ".join(lines)),)


def clean_transcript_text(value: str) -> str:
    text = unescape(str(value or ""))
    text = text.replace("\ufeff", " ")
    text = re.sub(r"\[(?:음악|박수|Music|Applause)\]", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _optional_int(value: Any) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _text_or_none(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _youtube_cookie_file() -> str | None:
    value = os.getenv("YOUTUBE_COOKIES_FILE") or os.getenv("TRADINGAGENTS_YOUTUBE_COOKIES_FILE")
    text = str(value or "").strip()
    return text if text and os.path.isfile(text) else None


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(float(os.getenv(name, default)))
    except (TypeError, ValueError):
        return default
