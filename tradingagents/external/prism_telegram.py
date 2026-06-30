from __future__ import annotations

from datetime import datetime
from typing import Any

from .prism_models import PrismIngestionResult, PrismSourceKind
from .prism_telegram_bot import load_telegram_bot_api
from .prism_telegram_common import PrismTelegramRuntimeConfig, runtime_config_from_any
from .prism_telegram_preview import load_telegram_public_preview
from .prism_telegram_user import load_telegram_user_session


def load_telegram_prism_signals(
    config: PrismTelegramRuntimeConfig | Any,
    *,
    default_market: str | None = None,
) -> PrismIngestionResult:
    cfg = config if isinstance(config, PrismTelegramRuntimeConfig) else runtime_config_from_any(config)
    if not cfg.enabled:
        return PrismIngestionResult(enabled=False, ok=True)
    mode = str(cfg.mode or "public_preview").strip().lower()
    if mode in {"user_session", "mtproto", "telethon"}:
        result = load_telegram_user_session(cfg, default_market=default_market)
        if result.ok or not cfg.fallback_to_public_preview:
            return result
        preview = load_telegram_public_preview(cfg, default_market=default_market)
        return _combine_failed_user_with_preview(result, preview)
    if mode in {"bot_api", "bot"}:
        result = load_telegram_bot_api(cfg, default_market=default_market)
        if result.ok or not cfg.fallback_to_public_preview:
            return result
        preview = load_telegram_public_preview(cfg, default_market=default_market)
        return _combine_failed_user_with_preview(result, preview)
    return load_telegram_public_preview(cfg, default_market=default_market)


def _combine_failed_user_with_preview(
    user_result: PrismIngestionResult,
    preview_result: PrismIngestionResult,
) -> PrismIngestionResult:
    warnings = [*user_result.warnings, *preview_result.warnings]
    return PrismIngestionResult(
        enabled=True,
        ok=preview_result.ok,
        source_kind=preview_result.source_kind or PrismSourceKind.TELEGRAM_PUBLIC_PREVIEW,
        source=preview_result.source or user_result.source,
        ingested_at=preview_result.ingested_at or datetime.now().astimezone(),
        signals=list(preview_result.signals),
        portfolio_snapshot=preview_result.portfolio_snapshot,
        performance_summary=preview_result.performance_summary,
        journal_lessons=list(preview_result.journal_lessons),
        warnings=list(dict.fromkeys(warnings)),
        raw_payload_hash=preview_result.raw_payload_hash,
    )
