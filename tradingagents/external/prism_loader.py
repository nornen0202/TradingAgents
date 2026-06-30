from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from .prism_dashboard import (
    candidate_dashboard_urls,
    fetch_dashboard_html_url,
    fetch_dashboard_json_url,
    load_dashboard_json_file,
)
from .prism_models import PrismExternalSignal, PrismIngestionResult, PrismSourceKind
from .prism_sqlite import load_prism_sqlite
from .prism_telegram import load_telegram_prism_signals
from .prism_telegram_common import PrismTelegramRuntimeConfig, runtime_config_from_any


@dataclass(frozen=True)
class PrismLoaderConfig:
    enabled: bool = False
    mode: str = "advisory"
    local_dashboard_json_path: str | Path | None = None
    local_sqlite_db_path: str | Path | None = None
    dashboard_json_url: str | None = None
    dashboard_base_url: str | None = "https://analysis.stocksimulation.kr"
    timeout_seconds: float = 5.0
    max_payload_bytes: int = 5_000_000
    use_live_http: bool = False
    use_html_scraping: bool = False
    confidence_cap: float = 0.25
    market: str | None = None
    telegram: Any | None = None


def load_prism_signals(config: PrismLoaderConfig | Any | None = None) -> PrismIngestionResult:
    cfg = _config_from_any(config)
    if not cfg.enabled:
        return PrismIngestionResult(enabled=False, ok=True)

    primary = _load_primary_prism_signals(cfg)
    telegram = load_telegram_prism_signals(cfg.telegram, default_market=cfg.market) if cfg.telegram is not None else None
    return _merge_primary_and_telegram(primary, telegram)


def _load_primary_prism_signals(cfg: PrismLoaderConfig) -> PrismIngestionResult:
    if cfg.local_dashboard_json_path:
        return load_dashboard_json_file(cfg.local_dashboard_json_path, market=cfg.market)
    if cfg.local_sqlite_db_path:
        return load_prism_sqlite(cfg.local_sqlite_db_path, market=cfg.market)
    if cfg.use_live_http and cfg.dashboard_json_url:
        return fetch_dashboard_json_url(
            cfg.dashboard_json_url,
            timeout_seconds=cfg.timeout_seconds,
            max_payload_bytes=cfg.max_payload_bytes,
            market=cfg.market,
        )
    if cfg.use_live_http and cfg.dashboard_base_url:
        warnings: list[str] = []
        for url in candidate_dashboard_urls(cfg.dashboard_base_url, market=cfg.market):
            result = fetch_dashboard_json_url(
                url,
                timeout_seconds=cfg.timeout_seconds,
                max_payload_bytes=cfg.max_payload_bytes,
                market=cfg.market,
            )
            if result.ok and result.signals:
                return result
            warnings.extend(result.warnings)
        if cfg.use_html_scraping:
            result = fetch_dashboard_html_url(
                cfg.dashboard_base_url,
                timeout_seconds=cfg.timeout_seconds,
                max_payload_bytes=cfg.max_payload_bytes,
                market=cfg.market,
            )
            if result.ok and result.signals:
                return result
            warnings.extend(result.warnings)
        return PrismIngestionResult(
            enabled=True,
            ok=False,
            warnings=warnings or ["dashboard_live_candidates_unavailable"],
        )
    return PrismIngestionResult(
        enabled=True,
        ok=True,
        warnings=["prism_enabled_but_no_source_configured"],
    )


def _config_from_any(value: PrismLoaderConfig | Any | None) -> PrismLoaderConfig:
    if isinstance(value, PrismLoaderConfig):
        return _apply_env_overrides(value)
    if value is None:
        return _apply_env_overrides(PrismLoaderConfig())
    prism = getattr(value, "prism", None) or getattr(value, "prism_dashboard", None) or value
    cfg = PrismLoaderConfig(
        enabled=bool(getattr(prism, "enabled", False)),
        mode=str(getattr(prism, "mode", "advisory") or "advisory"),
        local_dashboard_json_path=(
            getattr(prism, "local_dashboard_json_path", None)
            or getattr(prism, "local_json_path", None)
            or getattr(prism, "dashboard_json_path", None)
        ),
        local_sqlite_db_path=(
            getattr(prism, "local_sqlite_db_path", None)
            or getattr(prism, "sqlite_path", None)
            or getattr(prism, "sqlite_db_path", None)
        ),
        dashboard_json_url=getattr(prism, "dashboard_json_url", None) or getattr(prism, "dashboard_url", None),
        dashboard_base_url=getattr(prism, "dashboard_base_url", "https://analysis.stocksimulation.kr"),
        timeout_seconds=float(getattr(prism, "timeout_seconds", 5.0) or 5.0),
        max_payload_bytes=int(getattr(prism, "max_payload_bytes", 5_000_000) or 5_000_000),
        use_live_http=bool(getattr(prism, "use_live_http", False)),
        use_html_scraping=bool(getattr(prism, "use_html_scraping", False)),
        confidence_cap=float(getattr(prism, "confidence_cap", 0.25) or 0.25),
        market=getattr(prism, "market", None),
        telegram=getattr(prism, "telegram", None),
    )
    return _apply_env_overrides(cfg)


def _apply_env_overrides(config: PrismLoaderConfig) -> PrismLoaderConfig:
    enabled = _env_bool("PRISM_EXTERNAL_ENABLED", config.enabled)
    local_json = _env_text("PRISM_DASHBOARD_JSON_PATH", config.local_dashboard_json_path)
    sqlite_path = _env_text("PRISM_SQLITE_DB_PATH", config.local_sqlite_db_path)
    json_url = _env_text("PRISM_DASHBOARD_JSON_URL", config.dashboard_json_url)
    base_url = _env_text("PRISM_DASHBOARD_BASE_URL", config.dashboard_base_url)
    use_live = _env_bool("PRISM_USE_LIVE_HTTP", config.use_live_http)
    use_html = _env_bool("PRISM_USE_HTML_SCRAPING", config.use_html_scraping)
    timeout = _env_float("PRISM_TIMEOUT_SECONDS", config.timeout_seconds)
    max_bytes = _env_int("PRISM_MAX_PAYLOAD_BYTES", config.max_payload_bytes)
    telegram = _telegram_env_config(config.telegram)
    return PrismLoaderConfig(
        enabled=enabled,
        mode=config.mode,
        local_dashboard_json_path=local_json,
        local_sqlite_db_path=sqlite_path,
        dashboard_json_url=json_url,
        dashboard_base_url=base_url,
        timeout_seconds=timeout,
        max_payload_bytes=max_bytes,
        use_live_http=use_live,
        use_html_scraping=use_html,
        confidence_cap=config.confidence_cap,
        market=config.market,
        telegram=telegram,
    )


def _telegram_env_config(value: Any | None) -> PrismTelegramRuntimeConfig:
    cfg = runtime_config_from_any(value)
    return PrismTelegramRuntimeConfig(
        enabled=_env_bool("PRISM_TELEGRAM_ENABLED", cfg.enabled),
        mode=_env_text("PRISM_TELEGRAM_MODE", cfg.mode) or cfg.mode,
        channel=_env_text("PRISM_TELEGRAM_CHANNEL", cfg.channel) or cfg.channel,
        public_preview_url=_env_text("PRISM_TELEGRAM_PUBLIC_PREVIEW_URL", cfg.public_preview_url),
        lookback_minutes=_env_int("PRISM_TELEGRAM_LOOKBACK_MINUTES", cfg.lookback_minutes),
        max_messages=_env_int("PRISM_TELEGRAM_MAX_MESSAGES", cfg.max_messages),
        timeout_seconds=_env_float("PRISM_TELEGRAM_TIMEOUT_SECONDS", cfg.timeout_seconds),
        max_payload_bytes=_env_int("PRISM_TELEGRAM_MAX_PAYLOAD_BYTES", cfg.max_payload_bytes),
        download_pdfs=_env_bool("PRISM_TELEGRAM_DOWNLOAD_PDFS", cfg.download_pdfs),
        private_archive_dir=_env_text("PRISM_TELEGRAM_PRIVATE_ARCHIVE_DIR", cfg.private_archive_dir),
        state_path=_env_text("PRISM_TELEGRAM_STATE_PATH", cfg.state_path),
        session_path=_env_text("TELEGRAM_SESSION_PATH", cfg.session_path),
        session_string=_env_text("TELEGRAM_SESSION_STRING", cfg.session_string),
        api_id=_env_text("TELEGRAM_API_ID", cfg.api_id),
        api_hash=_env_text("TELEGRAM_API_HASH", cfg.api_hash),
        bot_token=_env_text("TELEGRAM_BOT_TOKEN", cfg.bot_token),
        max_pdf_bytes=_env_int("PRISM_TELEGRAM_MAX_PDF_BYTES", cfg.max_pdf_bytes),
        fallback_to_public_preview=_env_bool(
            "PRISM_TELEGRAM_FALLBACK_TO_PUBLIC_PREVIEW",
            cfg.fallback_to_public_preview,
        ),
    )


def _merge_primary_and_telegram(
    primary: PrismIngestionResult,
    telegram: PrismIngestionResult | None,
) -> PrismIngestionResult:
    if telegram is None or not telegram.enabled:
        return primary
    if not primary.enabled:
        return telegram

    warnings = [*primary.warnings, *telegram.warnings]
    signals = list(primary.signals)
    primary_keys = {_signal_key(signal): index for index, signal in enumerate(signals)}
    added = 0
    enriched = 0
    for signal in telegram.signals:
        key = _signal_key(signal)
        index = primary_keys.get(key)
        if index is None:
            primary_keys[key] = len(signals)
            signals.append(signal)
            added += 1
            continue
        signals[index] = _with_telegram_evidence(signals[index], signal)
        enriched += 1
    if added or enriched:
        warnings.append(f"telegram_prism_signals_merged:added={added};enriched={enriched}")

    source_kind = primary.source_kind
    source = primary.source
    if (not primary.signals and telegram.signals) or not source_kind:
        source_kind = telegram.source_kind
        source = telegram.source
    elif telegram.signals:
        source_kind = PrismSourceKind.MIXED

    return PrismIngestionResult(
        enabled=True,
        ok=bool(primary.ok or telegram.ok),
        source_kind=source_kind,
        source=source,
        ingested_at=primary.ingested_at,
        signals=signals,
        portfolio_snapshot=primary.portfolio_snapshot or telegram.portfolio_snapshot,
        performance_summary=primary.performance_summary or telegram.performance_summary,
        journal_lessons=[*primary.journal_lessons, *telegram.journal_lessons],
        warnings=list(dict.fromkeys(warnings)),
        raw_payload_hash=primary.raw_payload_hash or telegram.raw_payload_hash,
    )


def _with_telegram_evidence(primary: PrismExternalSignal, telegram: PrismExternalSignal) -> PrismExternalSignal:
    raw = dict(primary.raw or {})
    evidence = list(raw.get("telegram_evidence") or [])
    evidence.append(telegram.to_dict())
    raw["telegram_evidence"] = evidence
    tags = tuple(dict.fromkeys([*primary.tags, "telegram_evidence"]))
    rationale = primary.rationale
    if telegram.rationale and telegram.rationale not in str(rationale or ""):
        rationale = f"{rationale}\n\nTelegram evidence: {telegram.rationale}" if rationale else telegram.rationale
    return replace(primary, raw=raw, tags=tags, rationale=rationale)


def _signal_key(signal: PrismExternalSignal) -> tuple[str, str, str | None]:
    return (
        str(signal.canonical_ticker or "").strip().upper(),
        signal.signal_action.value,
        signal.trigger_type,
    )


def _env_text(name: str, default: Any) -> Any:
    value = os.getenv(name)
    if value is None:
        return default
    text = value.strip()
    return text or None


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default
