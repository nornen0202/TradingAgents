from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from tradingagents.dataflows.api_keys import get_api_key

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    import tomli as tomllib

from .account_models import AccountConstraints, PortfolioProfile
from .instrument_identity import resolve_identity


def load_portfolio_profile(path: str | Path, profile_name: str) -> PortfolioProfile:
    profile_path = Path(path).expanduser().resolve()
    with profile_path.open("rb") as handle:
        raw = tomllib.load(handle)

    profiles = raw.get("profiles") or {}
    if profile_name not in profiles:
        raise ValueError(f"Profile '{profile_name}' was not found in {profile_path}.")

    payload = profiles[profile_name] or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Profile '{profile_name}' must be a table.")

    watch_tickers = tuple(_normalize_watch_ticker(item) for item in (payload.get("watch_tickers") or []))
    watch_tickers = tuple(item for item in watch_tickers if item)
    broker = str(payload.get("broker", "kis")).strip().lower() or "kis"
    market_scope = _normalize_market_scope(
        payload.get("market_scope") or payload.get("market"),
        broker=broker,
        watch_tickers=watch_tickers,
    )

    constraints = AccountConstraints(
        min_cash_buffer_krw=_to_int(payload.get("min_cash_buffer_krw"), default=0),
        min_trade_krw=max(0, _to_int(payload.get("min_trade_krw"), default=100_000)),
        max_single_name_weight=_to_float(payload.get("max_single_name_weight"), default=0.35),
        max_sector_weight=_to_float(payload.get("max_sector_weight"), default=0.50),
        max_daily_turnover_ratio=_to_float(payload.get("max_daily_turnover_ratio"), default=0.30),
        max_order_count_per_day=max(1, _to_int(payload.get("max_order_count_per_day"), default=5)),
        respect_existing_weights_softly=bool(payload.get("respect_existing_weights_softly", True)),
    )

    return PortfolioProfile(
        name=profile_name,
        enabled=bool(payload.get("enabled", False)),
        broker=broker,
        broker_environment=str(payload.get("broker_environment", "real")).strip().lower() or "real",
        read_only=bool(payload.get("read_only", True)),
        account_no=_first_non_empty(
            _normalize_text(payload.get("account_no")),
            get_api_key("KIS_ACCOUNT_NO"),
            _normalize_text(os.getenv("KIS_ACCOUNT_NO")),
            _normalize_text(os.getenv("KIS_Developers_ACCOUNT_NO")),
        ),
        product_code=_first_non_empty(
            _normalize_text(payload.get("product_code")),
            get_api_key("KIS_PRODUCT_CODE"),
            _normalize_text(os.getenv("KIS_PRODUCT_CODE")),
            _normalize_text(os.getenv("KIS_Developers_PRODUCT_CODE")),
            "01",
        ),
        manual_snapshot_path=_resolve_optional_path(payload.get("manual_snapshot_path"), profile_path.parent),
        csv_positions_path=_resolve_optional_path(payload.get("csv_positions_path"), profile_path.parent),
        private_output_dirname=_normalize_text(payload.get("private_output_dirname")) or "portfolio-private",
        watch_tickers=watch_tickers,
        trigger_budget_krw=max(0, _to_int(payload.get("trigger_budget_krw"), default=500_000)),
        constraints=constraints,
        continue_on_error=bool(payload.get("continue_on_error", True)),
        market_scope=market_scope,
        allow_intraday_pilot=bool(payload.get("allow_intraday_pilot", False)),
        intraday_pilot_max_krw=max(0, _to_int(payload.get("intraday_pilot_max_krw"), default=600_000)),
        intraday_pilot_min_time_kst=_normalize_text(payload.get("intraday_pilot_min_time_kst")) or "10:30",
        intraday_pilot_require_vwap=bool(payload.get("intraday_pilot_require_vwap", True)),
        intraday_pilot_require_adjusted_rvol=bool(payload.get("intraday_pilot_require_adjusted_rvol", True)),
        intraday_pilot_forbid_failed_breakout=bool(payload.get("intraday_pilot_forbid_failed_breakout", True)),
    )


def _normalize_watch_ticker(value: object) -> str | None:
    text = _normalize_text(value)
    if not text:
        return None
    try:
        return resolve_identity(text).canonical_ticker
    except Exception:
        return text.strip().upper()


def _resolve_optional_path(value: object, base_dir: Path) -> Path | None:
    text = _normalize_text(value)
    if not text:
        return None
    expanded = os.path.expandvars(os.path.expanduser(text))
    path = Path(expanded)
    if not path.is_absolute():
        path = (base_dir / path).resolve()
    return path


def _normalize_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _first_non_empty(*values: str | None) -> str | None:
    for value in values:
        if value:
            return value
    return None


def _normalize_market_scope(value: object, *, broker: str, watch_tickers: tuple[str, ...]) -> str:
    text = _normalize_text(value)
    if text:
        normalized = text.strip().lower()
        aliases = {
            "domestic": "kr",
            "korea": "kr",
            "krx": "kr",
            "overseas": "us",
            "usa": "us",
            "united_states": "us",
            "united-states": "us",
        }
        normalized = aliases.get(normalized, normalized)
        if normalized in {"kr", "us", "all"}:
            return normalized
    if broker in {"watchlist", "paper", "none"} and _looks_like_us_watchlist(watch_tickers):
        return "us"
    if _looks_like_us_watchlist(watch_tickers):
        return "us"
    return "kr"


def _looks_like_us_watchlist(watch_tickers: tuple[str, ...]) -> bool:
    if not watch_tickers:
        return False
    has_us = False
    for ticker in watch_tickers:
        symbol = str(ticker or "").strip().upper()
        if symbol.endswith((".KS", ".KQ")) or (len(symbol) == 6 and symbol.isdigit()):
            return False
        if symbol:
            has_us = True
    return has_us


def _to_int(value: Any, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, *, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
