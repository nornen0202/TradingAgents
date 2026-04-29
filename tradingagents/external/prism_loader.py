from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .prism_dashboard import (
    candidate_dashboard_urls,
    fetch_dashboard_html_url,
    fetch_dashboard_json_url,
    load_dashboard_json_file,
)
from .prism_models import PrismIngestionResult
from .prism_sqlite import load_prism_sqlite


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


def load_prism_signals(config: PrismLoaderConfig | Any | None = None) -> PrismIngestionResult:
    cfg = _config_from_any(config)
    if not cfg.enabled:
        return PrismIngestionResult(enabled=False, ok=True)

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
        for url in candidate_dashboard_urls(cfg.dashboard_base_url):
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
