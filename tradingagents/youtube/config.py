from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore


DEFAULT_CHANNEL_URLS = (
    "https://www.youtube.com/@kpunch/videos",
    "https://www.youtube.com/@sosumonkey/videos",
    "https://www.youtube.com/@%EA%B2%BD%EC%A0%9C%EC%82%AC%EB%83%A5%EA%BE%BC/videos",
    "https://www.youtube.com/@%EA%B2%BD%EC%A0%9C%EC%82%AC%EB%83%A5%EA%BE%BC/shorts",
    "https://www.youtube.com/@815moneytalk/videos",
    "https://www.youtube.com/@supe-tv/videos",
    "https://www.youtube.com/@3protv/videos",
    "https://www.youtube.com/@plus_tv_official/videos",
)
@dataclass(frozen=True)
class ChannelSettings:
    name: str
    urls: tuple[str, ...]
    lookback_hours: int
    timezone: str
    max_videos: int
    max_entries_per_url: int = 25
    max_parallel_videos: int = 4


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
    quick_model: str | None = None
    output_model: str | None = None
    codex_quick_reasoning_effort: str | None = None
    codex_deep_reasoning_effort: str | None = None
    codex_output_reasoning_effort: str | None = None


@dataclass(frozen=True)
class VerificationSettings:
    mode: str
    publish_unverified: bool
    max_claims_per_video: int
    strict_llm: bool
    research_enabled: bool = True
    max_research_queries: int = 10
    max_evidence_items: int = 24
    max_evidence_per_claim: int = 3
    fetch_web_pages: bool = True
    max_web_pages: int = 4
    max_transcript_chars_for_llm: int = 24000
    adaptive_transcript_budget_enabled: bool = True
    extended_transcript_chars_for_llm: int = 48000
    evidence_relevance_gate_enabled: bool = True
    min_evidence_relevance_score: float = 0.12


@dataclass(frozen=True)
class ASRSettings:
    enabled: bool = True
    model: str = "auto"
    device: str = "auto"
    compute_type: str = "auto"
    fallback_models: tuple[str, ...] = ("distil-large-v3", "small", "base")
    beam_size: int = 5
    best_of: int = 5
    temperature: str = "0.0,0.2,0.4"
    condition_on_previous_text: bool = False
    repetition_penalty: float = 1.05
    no_repeat_ngram_size: int = 3
    word_timestamps: bool = True
    hallucination_silence_threshold: float = 1.0
    vad_filter: bool = True
    vad_min_silence_ms: int = 500
    vad_speech_pad_ms: int = 300
    vad_threshold: float = 0.5
    min_quality: str = "usable"
    recheck_automatic: bool = True
    chunk_chars: int = 3200
    max_chunks: int = 12
    min_coverage_chunks: int = 5
    hotwords: tuple[str, ...] = ()
    initial_prompt: str = ""


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
    asr: ASRSettings = field(default_factory=ASRSettings)


def load_youtube_config(
    path: str | Path = "config/youtube_daily.toml",
) -> YouTubeDailyConfig:
    config_path = Path(path)
    raw: dict[str, Any] = {}
    if config_path.exists():
        raw = tomllib.loads(config_path.read_text(encoding="utf-8"))

    channel_raw = raw.get("channel") or {}
    llm_raw = raw.get("llm") or {}
    verification_raw = raw.get("verification") or {}
    asr_raw = raw.get("asr") or {}
    storage_raw = raw.get("storage") or {}
    site_raw = raw.get("site") or {}

    archive_dir = _youtube_archive_path(storage_raw.get("archive_dir"))
    site_dir = _path_from_env(
        "TRADINGAGENTS_SITE_DIR",
        storage_raw.get("site_dir") or "./site",
    )

    return YouTubeDailyConfig(
        channel=ChannelSettings(
            name=str(channel_raw.get("name") or "투자 유튜브 채널"),
            urls=tuple(
                str(item).strip()
                for item in (channel_raw.get("urls") or DEFAULT_CHANNEL_URLS)
                if str(item).strip()
            ),
            lookback_hours=max(1, int(channel_raw.get("lookback_hours") or 24)),
            timezone=str(channel_raw.get("timezone") or "Asia/Seoul"),
            max_videos=max(1, int(channel_raw.get("max_videos") or 100)),
            max_entries_per_url=max(
                1, int(channel_raw.get("max_entries_per_url") or 25)
            ),
            max_parallel_videos=max(
                1, int(channel_raw.get("max_parallel_videos") or 4)
            ),
        ),
        llm=LLMSettings(
            provider=str(llm_raw.get("provider") or "codex"),
            deep_model=_first_text(
                os.getenv("TRADINGAGENTS_YOUTUBE_DEEP_MODEL"),
                os.getenv("TRADINGAGENTS_CODEX_JUDGE_MODEL"),
                os.getenv("TRADINGAGENTS_CODEX_DEEP_MODEL"),
                llm_raw.get("deep_model"),
                default="gpt-5.6-sol",
            ),
            codex_binary=_optional_text(
                os.getenv("CODEX_BINARY") or llm_raw.get("codex_binary")
            ),
            codex_reasoning_effort=_first_text(
                os.getenv("TRADINGAGENTS_CODEX_REASONING_EFFORT"),
                llm_raw.get("codex_reasoning_effort"),
                default="medium",
            ),
            codex_summary=str(llm_raw.get("codex_summary") or "none"),
            codex_personality=str(llm_raw.get("codex_personality") or "none"),
            codex_workspace_dir=_optional_text(
                os.getenv("TRADINGAGENTS_CODEX_WORKSPACE_DIR")
                or llm_raw.get("codex_workspace_dir")
            ),
            codex_request_timeout=float(llm_raw.get("codex_request_timeout") or 180.0),
            codex_max_retries=int(llm_raw.get("codex_max_retries") or 2),
            codex_cleanup_threads=bool(llm_raw.get("codex_cleanup_threads", True)),
            codex_preflight_mode=str(
                llm_raw.get("codex_preflight_mode") or "workflow_once"
            ),
            quick_model=_first_text(
                os.getenv("TRADINGAGENTS_YOUTUBE_QUICK_MODEL"),
                os.getenv("TRADINGAGENTS_CODEX_QUICK_MODEL"),
                llm_raw.get("quick_model"),
                default="gpt-5.6-terra",
            ),
            output_model=_first_text(
                os.getenv("TRADINGAGENTS_YOUTUBE_OUTPUT_MODEL"),
                os.getenv("TRADINGAGENTS_CODEX_WRITER_MODEL"),
                os.getenv("TRADINGAGENTS_CODEX_OUTPUT_MODEL"),
                llm_raw.get("output_model"),
                default="gpt-5.6-luna",
            ),
            codex_quick_reasoning_effort=_first_text(
                os.getenv("TRADINGAGENTS_YOUTUBE_QUICK_REASONING_EFFORT"),
                os.getenv("TRADINGAGENTS_CODEX_QUICK_REASONING_EFFORT"),
                llm_raw.get("codex_quick_reasoning_effort"),
                default="low",
            ),
            codex_deep_reasoning_effort=_first_text(
                os.getenv("TRADINGAGENTS_YOUTUBE_DEEP_REASONING_EFFORT"),
                os.getenv("TRADINGAGENTS_CODEX_DEEP_REASONING_EFFORT"),
                llm_raw.get("codex_deep_reasoning_effort"),
                llm_raw.get("codex_reasoning_effort"),
                default="medium",
            ),
            codex_output_reasoning_effort=_first_text(
                os.getenv("TRADINGAGENTS_YOUTUBE_OUTPUT_REASONING_EFFORT"),
                os.getenv("TRADINGAGENTS_CODEX_OUTPUT_REASONING_EFFORT"),
                llm_raw.get("codex_output_reasoning_effort"),
                default="low",
            ),
        ),
        verification=VerificationSettings(
            mode=str(verification_raw.get("mode") or "external_full"),
            publish_unverified=bool(verification_raw.get("publish_unverified", True)),
            max_claims_per_video=max(
                1, int(verification_raw.get("max_claims_per_video") or 12)
            ),
            strict_llm=bool(verification_raw.get("strict_llm", True)),
            research_enabled=bool(verification_raw.get("research_enabled", True)),
            max_research_queries=max(
                1, int(verification_raw.get("max_research_queries") or 10)
            ),
            max_evidence_items=max(
                1, int(verification_raw.get("max_evidence_items") or 24)
            ),
            max_evidence_per_claim=max(
                1, int(verification_raw.get("max_evidence_per_claim") or 3)
            ),
            fetch_web_pages=bool(verification_raw.get("fetch_web_pages", True)),
            max_web_pages=max(0, int(verification_raw.get("max_web_pages") or 4)),
            max_transcript_chars_for_llm=max(
                1000, int(verification_raw.get("max_transcript_chars_for_llm") or 24000)
            ),
            adaptive_transcript_budget_enabled=bool(
                verification_raw.get("adaptive_transcript_budget_enabled", True)
            ),
            extended_transcript_chars_for_llm=max(
                1000,
                int(verification_raw.get("extended_transcript_chars_for_llm") or 48000),
            ),
            evidence_relevance_gate_enabled=bool(
                verification_raw.get("evidence_relevance_gate_enabled", True)
            ),
            min_evidence_relevance_score=min(
                1.0,
                max(
                    0.0,
                    float(verification_raw.get("min_evidence_relevance_score") or 0.12),
                ),
            ),
        ),
        asr=ASRSettings(
            enabled=bool(asr_raw.get("enabled", True)),
            model=str(asr_raw.get("model") or "auto"),
            device=str(asr_raw.get("device") or "auto"),
            compute_type=str(asr_raw.get("compute_type") or "auto"),
            fallback_models=tuple(
                str(item).strip()
                for item in (
                    asr_raw.get("fallback_models")
                    or ("distil-large-v3", "small", "base")
                )
                if str(item).strip()
            ),
            beam_size=max(1, int(asr_raw.get("beam_size") or 5)),
            best_of=max(1, int(asr_raw.get("best_of") or 5)),
            temperature=str(asr_raw.get("temperature") or "0.0,0.2,0.4"),
            condition_on_previous_text=bool(
                asr_raw.get("condition_on_previous_text", False)
            ),
            repetition_penalty=max(
                1.0, float(asr_raw.get("repetition_penalty") or 1.05)
            ),
            no_repeat_ngram_size=max(0, int(asr_raw.get("no_repeat_ngram_size") or 3)),
            word_timestamps=bool(asr_raw.get("word_timestamps", True)),
            hallucination_silence_threshold=max(
                0.0, float(asr_raw.get("hallucination_silence_threshold") or 1.0)
            ),
            vad_filter=bool(asr_raw.get("vad_filter", True)),
            vad_min_silence_ms=max(0, int(asr_raw.get("vad_min_silence_ms") or 500)),
            vad_speech_pad_ms=max(0, int(asr_raw.get("vad_speech_pad_ms") or 300)),
            vad_threshold=min(
                max(0.0, float(asr_raw.get("vad_threshold") or 0.5)), 1.0
            ),
            min_quality=str(asr_raw.get("min_quality") or "usable"),
            recheck_automatic=bool(asr_raw.get("recheck_automatic", True)),
            chunk_chars=max(1000, int(asr_raw.get("chunk_chars") or 3200)),
            max_chunks=max(4, int(asr_raw.get("max_chunks") or 12)),
            min_coverage_chunks=max(1, int(asr_raw.get("min_coverage_chunks") or 5)),
            hotwords=tuple(
                str(item).strip()
                for item in (asr_raw.get("hotwords") or ())
                if str(item).strip()
            ),
            initial_prompt=str(asr_raw.get("initial_prompt") or ""),
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
    max_entries_per_url: int | None = None,
    max_parallel_videos: int | None = None,
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
            max_entries_per_url=max(
                1, int(max_entries_per_url or channel.max_entries_per_url)
            ),
            max_parallel_videos=max(
                1, int(max_parallel_videos or channel.max_parallel_videos)
            ),
        ),
        llm=config.llm,
        verification=config.verification,
        asr=config.asr,
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


def _first_text(*values: Any, default: str) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return default
