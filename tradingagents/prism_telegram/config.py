from __future__ import annotations

from dataclasses import dataclass, replace
import os
from pathlib import Path
from typing import Any

from tradingagents.external.prism_telegram_common import (
    DEFAULT_TELEGRAM_CHANNEL,
    PrismTelegramRuntimeConfig,
)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore


@dataclass(frozen=True)
class PrismTelegramSourceSettings:
    enabled: bool = True
    mode: str = "public_preview"
    channel: str = DEFAULT_TELEGRAM_CHANNEL
    public_preview_url: str | None = None
    lookback_minutes: int = 180
    max_messages: int = 50
    timeout_seconds: float = 8.0
    max_payload_bytes: int = 5_000_000
    download_pdfs: bool = False
    private_archive_dir: Path | None = None
    state_path: Path | None = None
    session_path: Path | None = None
    session_string: str | None = None
    api_id: str | None = None
    api_hash: str | None = None
    bot_token: str | None = None
    max_pdf_bytes: int = 20_000_000
    fallback_to_public_preview: bool = True

    def runtime_config(self) -> PrismTelegramRuntimeConfig:
        return PrismTelegramRuntimeConfig(
            enabled=self.enabled,
            mode=self.mode,
            channel=self.channel,
            public_preview_url=self.public_preview_url,
            lookback_minutes=self.lookback_minutes,
            max_messages=self.max_messages,
            timeout_seconds=self.timeout_seconds,
            max_payload_bytes=self.max_payload_bytes,
            download_pdfs=self.download_pdfs,
            private_archive_dir=self.private_archive_dir,
            state_path=self.state_path,
            session_path=self.session_path,
            session_string=self.session_string,
            api_id=self.api_id,
            api_hash=self.api_hash,
            bot_token=self.bot_token,
            max_pdf_bytes=self.max_pdf_bytes,
            fallback_to_public_preview=self.fallback_to_public_preview,
        )


@dataclass(frozen=True)
class PrismTelegramStorageSettings:
    archive_dir: Path
    site_dir: Path


@dataclass(frozen=True)
class PrismTelegramSiteSettings:
    title: str = "PRISM Telegram 리포트"
    max_runs: int = 30
    max_messages_on_index: int = 80


@dataclass(frozen=True)
class PrismTelegramDailyConfig:
    source: PrismTelegramSourceSettings
    storage: PrismTelegramStorageSettings
    site: PrismTelegramSiteSettings


def load_prism_telegram_config(path: str | Path = "config/prism_telegram_daily.toml") -> PrismTelegramDailyConfig:
    config_path = Path(path)
    raw: dict[str, Any] = {}
    if config_path.exists():
        raw = tomllib.loads(config_path.read_text(encoding="utf-8"))

    source_raw = raw.get("source") or {}
    storage_raw = raw.get("storage") or {}
    site_raw = raw.get("site") or {}
    base_dir = config_path.parent if config_path.parent != Path("") else Path(".")

    source = PrismTelegramSourceSettings(
        enabled=_env_bool("PRISM_TELEGRAM_ENABLED", bool(source_raw.get("enabled", True))),
        mode=(_env_text("PRISM_TELEGRAM_MODE", source_raw.get("mode")) or "public_preview").strip().lower(),
        channel=_env_text("PRISM_TELEGRAM_CHANNEL", source_raw.get("channel")) or DEFAULT_TELEGRAM_CHANNEL,
        public_preview_url=_env_text("PRISM_TELEGRAM_PUBLIC_PREVIEW_URL", source_raw.get("public_preview_url")),
        lookback_minutes=max(
            0,
            _env_int("PRISM_TELEGRAM_LOOKBACK_MINUTES", int(source_raw.get("lookback_minutes", 180) or 180)),
        ),
        max_messages=max(
            1,
            _env_int("PRISM_TELEGRAM_MAX_MESSAGES", int(source_raw.get("max_messages", 50) or 50)),
        ),
        timeout_seconds=max(
            1.0,
            _env_float("PRISM_TELEGRAM_TIMEOUT_SECONDS", float(source_raw.get("timeout_seconds", 8.0) or 8.0)),
        ),
        max_payload_bytes=max(
            1024,
            _env_int("PRISM_TELEGRAM_MAX_PAYLOAD_BYTES", int(source_raw.get("max_payload_bytes", 5_000_000) or 5_000_000)),
        ),
        download_pdfs=_env_bool("PRISM_TELEGRAM_DOWNLOAD_PDFS", bool(source_raw.get("download_pdfs", False))),
        private_archive_dir=_env_path("PRISM_TELEGRAM_PRIVATE_ARCHIVE_DIR", source_raw.get("private_archive_dir"), base_dir),
        state_path=_env_path("PRISM_TELEGRAM_STATE_PATH", source_raw.get("state_path"), base_dir),
        session_path=_env_path("TELEGRAM_SESSION_PATH", source_raw.get("session_path"), base_dir),
        session_string=_env_text("TELEGRAM_SESSION_STRING", source_raw.get("session_string")),
        api_id=_env_text("TELEGRAM_API_ID", source_raw.get("api_id")),
        api_hash=_env_text("TELEGRAM_API_HASH", source_raw.get("api_hash")),
        bot_token=_env_text("TELEGRAM_BOT_TOKEN", source_raw.get("bot_token")),
        max_pdf_bytes=max(
            1024,
            _env_int("PRISM_TELEGRAM_MAX_PDF_BYTES", int(source_raw.get("max_pdf_bytes", 20_000_000) or 20_000_000)),
        ),
        fallback_to_public_preview=_env_bool(
            "PRISM_TELEGRAM_FALLBACK_TO_PUBLIC_PREVIEW",
            bool(source_raw.get("fallback_to_public_preview", True)),
        ),
    )
    return PrismTelegramDailyConfig(
        source=source,
        storage=PrismTelegramStorageSettings(
            archive_dir=_prism_telegram_archive_path(storage_raw.get("archive_dir")),
            site_dir=_env_path("TRADINGAGENTS_SITE_DIR", storage_raw.get("site_dir") or "./site", base_dir)
            or Path("./site"),
        ),
        site=PrismTelegramSiteSettings(
            title=str(site_raw.get("title") or "PRISM Telegram 리포트"),
            max_runs=max(1, int(site_raw.get("max_runs") or 30)),
            max_messages_on_index=max(1, int(site_raw.get("max_messages_on_index") or 80)),
        ),
    )


def with_prism_telegram_overrides(
    config: PrismTelegramDailyConfig,
    *,
    archive_dir: str | Path | None = None,
    site_dir: str | Path | None = None,
    mode: str | None = None,
    channel: str | None = None,
    lookback_minutes: int | None = None,
    max_messages: int | None = None,
    download_pdfs: bool | None = None,
) -> PrismTelegramDailyConfig:
    source = config.source
    storage = config.storage
    if mode:
        source = replace(source, mode=str(mode).strip().lower())
    if channel:
        source = replace(source, channel=str(channel).strip() or source.channel)
    if lookback_minutes is not None:
        source = replace(source, lookback_minutes=max(0, int(lookback_minutes or 0)))
    if max_messages is not None:
        source = replace(source, max_messages=max(1, int(max_messages or 1)))
    if download_pdfs is not None:
        source = replace(source, download_pdfs=bool(download_pdfs))
    if archive_dir:
        storage = replace(storage, archive_dir=Path(archive_dir))
    if site_dir:
        storage = replace(storage, site_dir=Path(site_dir))
    return replace(config, source=source, storage=storage)


def _prism_telegram_archive_path(configured_value: Any) -> Path:
    explicit = os.getenv("TRADINGAGENTS_PRISM_TELEGRAM_ARCHIVE_DIR")
    if explicit and explicit.strip():
        return Path(explicit)
    configured_text = str(configured_value or "./.runtime/prism-telegram-archive").strip()
    shared_archive = os.getenv("TRADINGAGENTS_ARCHIVE_DIR")
    default_texts = {
        "./.runtime/prism-telegram-archive",
        ".runtime/prism-telegram-archive",
        ".\\.runtime\\prism-telegram-archive",
    }
    if shared_archive and shared_archive.strip() and configured_text in default_texts:
        return Path(shared_archive) / "prism-telegram-archive"
    return Path(configured_text)


def _env_path(name: str, default: Any, base_dir: Path) -> Path | None:
    value = os.getenv(name)
    raw = value if value is not None else default
    if raw in (None, ""):
        return None
    path = Path(os.path.expandvars(os.path.expanduser(str(raw))))
    if not path.is_absolute():
        path = (base_dir / path).resolve()
    return path


def _env_text(name: str, default: Any) -> str | None:
    value = os.getenv(name)
    if value is None:
        value = default
    text = str(value or "").strip()
    return text or None


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default
