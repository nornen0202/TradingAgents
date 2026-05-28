from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore


DEFAULT_CHANNEL_URLS = (
    "https://www.youtube.com/@%EA%B2%BD%EC%A0%9C%EC%82%AC%EB%83%A5%EA%BE%BC/videos",
    "https://www.youtube.com/@%EA%B2%BD%EC%A0%9C%EC%82%AC%EB%83%A5%EA%BE%BC/shorts",
)


@dataclass(frozen=True)
class ChannelSettings:
    name: str
    urls: tuple[str, ...]
    lookback_hours: int
    timezone: str
    max_videos: int


@dataclass(frozen=True)
class LLMSettings:
    provider: str
    deep_model: str
    codex_binary: str | None
    codex_reasoning_effort: str
    codex_summary: str
    codex_personality: str
    codex_workspace_dir: str | None
    codex_request_timeout: float
    codex_max_retries: int
    codex_cleanup_threads: bool
    codex_preflight_mode: str


@dataclass(frozen=True)
class VerificationSettings:
    mode: str
    publish_unverified: bool
    max_claims_per_video: int
    strict_llm: bool


@dataclass(frozen=True)
class StorageSettings:
    archive_dir: Path
    site_dir: Path


@dataclass(frozen=True)
class YouTubeSiteSettings:
    title: str
    max_runs: int
    max_videos_on_index: int


@dataclass(frozen=True)
class YouTubeDailyConfig:
    channel: ChannelSettings
    llm: LLMSettings
    verification: VerificationSettings
    storage: StorageSettings
    site: YouTubeSiteSettings


def load_youtube_config(path: str | Path = "config/youtube_daily.toml") -> YouTubeDailyConfig:
    config_path = Path(path)
    raw: dict[str, Any] = {}
    if config_path.exists():
        raw = tomllib.loads(config_path.read_text(encoding="utf-8"))

    channel_raw = raw.get("channel") or {}
    llm_raw = raw.get("llm") or {}
    verification_raw = raw.get("verification") or {}
    storage_raw = raw.get("storage") or {}
    site_raw = raw.get("site") or {}

    archive_dir = _youtube_archive_path(storage_raw.get("archive_dir"))
    site_dir = _path_from_env(
        "TRADINGAGENTS_SITE_DIR",
        storage_raw.get("site_dir") or "./site",
    )

    return YouTubeDailyConfig(
        channel=ChannelSettings(
            name=str(channel_raw.get("name") or "경제사냥꾼"),
            urls=tuple(str(item).strip() for item in (channel_raw.get("urls") or DEFAULT_CHANNEL_URLS) if str(item).strip()),
            lookback_hours=max(1, int(channel_raw.get("lookback_hours") or 24)),
            timezone=str(channel_raw.get("timezone") or "Asia/Seoul"),
            max_videos=max(1, int(channel_raw.get("max_videos") or 50)),
        ),
        llm=LLMSettings(
            provider=str(llm_raw.get("provider") or "codex"),
            deep_model=str(llm_raw.get("deep_model") or "gpt-5.5"),
            codex_binary=_optional_text(os.getenv("CODEX_BINARY") or llm_raw.get("codex_binary")),
            codex_reasoning_effort=str(llm_raw.get("codex_reasoning_effort") or "medium"),
            codex_summary=str(llm_raw.get("codex_summary") or "none"),
            codex_personality=str(llm_raw.get("codex_personality") or "none"),
            codex_workspace_dir=_optional_text(
                os.getenv("TRADINGAGENTS_CODEX_WORKSPACE_DIR") or llm_raw.get("codex_workspace_dir")
            ),
            codex_request_timeout=float(llm_raw.get("codex_request_timeout") or 180.0),
            codex_max_retries=int(llm_raw.get("codex_max_retries") or 2),
            codex_cleanup_threads=bool(llm_raw.get("codex_cleanup_threads", True)),
            codex_preflight_mode=str(llm_raw.get("codex_preflight_mode") or "workflow_once"),
        ),
        verification=VerificationSettings(
            mode=str(verification_raw.get("mode") or "external_full"),
            publish_unverified=bool(verification_raw.get("publish_unverified", True)),
            max_claims_per_video=max(1, int(verification_raw.get("max_claims_per_video") or 12)),
            strict_llm=bool(verification_raw.get("strict_llm", True)),
        ),
        storage=StorageSettings(archive_dir=archive_dir, site_dir=site_dir),
        site=YouTubeSiteSettings(
            title=str(site_raw.get("title") or "YouTube 투자자용 검증 리포트"),
            max_runs=max(1, int(site_raw.get("max_runs") or 30)),
            max_videos_on_index=max(1, int(site_raw.get("max_videos_on_index") or 50)),
        ),
    )


def with_youtube_overrides(
    config: YouTubeDailyConfig,
    *,
    channel_urls: tuple[str, ...] | None = None,
    lookback_hours: int | None = None,
    max_videos: int | None = None,
    archive_dir: str | Path | None = None,
    site_dir: str | Path | None = None,
) -> YouTubeDailyConfig:
    channel = config.channel
    storage = config.storage
    return YouTubeDailyConfig(
        channel=ChannelSettings(
            name=channel.name,
            urls=tuple(item for item in (channel_urls or channel.urls) if item),
            lookback_hours=max(1, int(lookback_hours or channel.lookback_hours)),
            timezone=channel.timezone,
            max_videos=max(1, int(max_videos or channel.max_videos)),
        ),
        llm=config.llm,
        verification=config.verification,
        storage=StorageSettings(
            archive_dir=Path(archive_dir) if archive_dir else storage.archive_dir,
            site_dir=Path(site_dir) if site_dir else storage.site_dir,
        ),
        site=config.site,
    )


def _path_from_env(env_name: str, fallback: Any) -> Path:
    value = os.getenv(env_name) or fallback
    return Path(str(value))


def _youtube_archive_path(configured_value: Any) -> Path:
    explicit_youtube_archive = os.getenv("TRADINGAGENTS_YOUTUBE_ARCHIVE_DIR")
    if explicit_youtube_archive and explicit_youtube_archive.strip():
        return Path(explicit_youtube_archive)

    configured_text = str(configured_value or "./.runtime/youtube-archive").strip()
    shared_archive = os.getenv("TRADINGAGENTS_ARCHIVE_DIR")
    default_texts = {
        "./.runtime/youtube-archive",
        ".runtime/youtube-archive",
        ".\\.runtime\\youtube-archive",
    }
    if shared_archive and shared_archive.strip() and configured_text in default_texts:
        return Path(shared_archive) / "youtube-archive"
    return Path(configured_text)


def _optional_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None
