from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from datetime import datetime, time
from pathlib import Path
from typing import Iterable
from zoneinfo import ZoneInfo

from cli.utils import normalize_ticker_symbol

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    import tomli as tomllib


ALL_ANALYSTS = ("market", "social", "news", "fundamentals")
VALID_TRADE_DATE_MODES = {"latest_available", "today", "previous_business_day", "explicit"}
VALID_TICKER_UNIVERSE_MODES = {"config_only", "config_plus_account", "account_only"}
VALID_RUN_MODES = {"full", "overlay_only", "selective_rerun_only"}
DEFAULT_EXECUTION_CHECKPOINTS_BY_MARKET: dict[str, tuple[str, ...]] = {
    # KST anchors intentionally map to (pre-open, intraday, post-close) semantics.
    "KR": ("09:20", "12:00", "15:40"),
}


@dataclass(frozen=True)
class RunSettings:
    tickers: list[str]
    market: str = "AUTO"
    ticker_universe_mode: str = "config_only"
    analysts: list[str] = field(default_factory=lambda: list(ALL_ANALYSTS))
    output_language: str = "Korean"
    trade_date_mode: str = "latest_available"
    explicit_trade_date: str | None = None
    timezone: str = "Asia/Seoul"
    max_debate_rounds: int = 2
    max_risk_discuss_rounds: int = 2
    latest_market_data_lookback_days: int = 14
    continue_on_ticker_error: bool = True
    report_polisher_enabled: bool = True
    ticker_name_overrides: dict[str, str] = field(default_factory=dict)
    run_mode: str = "full"


@dataclass(frozen=True)
class LLMSettings:
    provider: str = "codex"
    deep_model: str = "gpt-5.4"
    quick_model: str = "gpt-5.4-mini"
    output_model: str = "gpt-5.4-mini"
    codex_reasoning_effort: str = "medium"
    codex_summary: str = "none"
    codex_personality: str = "none"
    codex_request_timeout: float = 180.0
    codex_max_retries: int = 2
    codex_cleanup_threads: bool = True
    codex_workspace_dir: str | None = str(Path.home() / ".codex" / "tradingagents-workspace")
    codex_binary: str | None = None


@dataclass(frozen=True)
class TranslationSettings:
    backend: str = "nllb_ct2"
    model: str = "nllb-200-distilled-600m"
    model_path: str | None = None
    tokenizer_path: str | None = None
    device: str = "auto"
    compute_type: str = "auto"
    max_chunk_chars: int = 1800
    allow_llm_fallback: bool = True
    allow_large_model: bool = False


@dataclass(frozen=True)
class StorageSettings:
    archive_dir: Path
    site_dir: Path


@dataclass(frozen=True)
class SiteSettings:
    title: str = "TradingAgents Daily Reports"
    subtitle: str = "Automated multi-agent market analysis powered by Codex"
    max_runs_on_homepage: int = 30


@dataclass(frozen=True)
class ExecutionSettings:
    execution_refresh_enabled: bool = False
    execution_refresh_checkpoints_kst: tuple[str, ...] = DEFAULT_EXECUTION_CHECKPOINTS_BY_MARKET["KR"]
    execution_max_data_age_seconds: int = 180
    execution_publish_badges: bool = True
    execution_selective_rerun_enabled: bool = True
    execution_llm_summary_model: str | None = "gpt-5.4-mini"
    execution_publish_debug: bool = False


@dataclass(frozen=True)
class PortfolioSettings:
    enabled: bool = False
    profile_path: Path | None = None
    profile_name: str = "kr_kis_default"
    continue_on_error: bool = True
    semantic_judge_enabled: bool = False
    action_judge_enabled: bool = False
    action_judge_top_n: int = 5
    report_polisher_enabled: bool = True


@dataclass(frozen=True)
class ScheduledAnalysisConfig:
    run: RunSettings
    llm: LLMSettings
    translation: TranslationSettings
    storage: StorageSettings
    site: SiteSettings
    portfolio: PortfolioSettings
    execution: ExecutionSettings
    config_path: Path


def load_scheduled_config(path: str | Path) -> ScheduledAnalysisConfig:
    config_path = Path(path).resolve()
    with config_path.open("rb") as handle:
        raw = tomllib.load(handle)

    run_raw = raw.get("run") or {}
    llm_raw = raw.get("llm") or {}
    translation_raw = raw.get("translation") or {}
    storage_raw = raw.get("storage") or {}
    site_raw = raw.get("site") or {}
    portfolio_raw = raw.get("portfolio") or {}
    execution_raw = raw.get("execution") or {}

    tickers = _normalize_tickers(run_raw.get("tickers") or [])
    if not tickers:
        raise ValueError("Scheduled analysis config must declare at least one ticker in [run].tickers.")

    analysts = _normalize_analysts(run_raw.get("analysts") or list(ALL_ANALYSTS))

    trade_date_mode = str(run_raw.get("trade_date_mode", "latest_available")).strip().lower()
    explicit_trade_date = None
    if run_raw.get("trade_date"):
        trade_date_mode = "explicit"
        explicit_trade_date = _validate_trade_date(str(run_raw["trade_date"]))
    elif trade_date_mode == "explicit":
        explicit_trade_date = _validate_trade_date(str(run_raw.get("explicit_trade_date", "")).strip())

    if trade_date_mode not in VALID_TRADE_DATE_MODES:
        raise ValueError(
            f"Unsupported trade_date_mode '{trade_date_mode}'. "
            f"Expected one of: {', '.join(sorted(VALID_TRADE_DATE_MODES))}."
        )

    timezone_name = str(run_raw.get("timezone", "Asia/Seoul")).strip()
    ZoneInfo(timezone_name)
    declared_market = str(run_raw.get("market", "AUTO")).strip().upper() or "AUTO"
    market_code = _normalize_market_code(declared_market, timezone_name=timezone_name)
    default_checkpoints = _default_execution_checkpoints_kst(market_code)

    base_dir = config_path.parent
    archive_dir = _resolve_path(storage_raw.get("archive_dir", ".tradingagents-scheduled/archive"), base_dir)
    site_dir = _resolve_path(storage_raw.get("site_dir", "site"), base_dir)

    return ScheduledAnalysisConfig(
        run=RunSettings(
            tickers=tickers,
            market=market_code,
            ticker_universe_mode=_normalize_ticker_universe_mode(run_raw.get("ticker_universe_mode", "config_only")),
            analysts=analysts,
            output_language=str(run_raw.get("output_language", "Korean")).strip() or "Korean",
            trade_date_mode=trade_date_mode,
            explicit_trade_date=explicit_trade_date,
            timezone=timezone_name,
            max_debate_rounds=int(run_raw.get("max_debate_rounds", 2)),
            max_risk_discuss_rounds=int(run_raw.get("max_risk_discuss_rounds", 2)),
            latest_market_data_lookback_days=int(run_raw.get("latest_market_data_lookback_days", 14)),
            continue_on_ticker_error=bool(run_raw.get("continue_on_ticker_error", True)),
            report_polisher_enabled=bool(run_raw.get("report_polisher_enabled", True)),
            ticker_name_overrides=_normalize_ticker_name_overrides(raw.get("ticker_names") or {}),
            run_mode=_normalize_run_mode(run_raw.get("run_mode", "full")),
        ),
        llm=LLMSettings(
            provider=str(llm_raw.get("provider", "codex")).strip().lower() or "codex",
            deep_model=str(llm_raw.get("deep_model", "gpt-5.4")).strip() or "gpt-5.4",
            quick_model=str(llm_raw.get("quick_model", "gpt-5.4-mini")).strip() or "gpt-5.4-mini",
            output_model=str(llm_raw.get("output_model", "gpt-5.4-mini")).strip() or "gpt-5.4-mini",
            codex_reasoning_effort=str(llm_raw.get("codex_reasoning_effort", "medium")).strip() or "medium",
            codex_summary=str(llm_raw.get("codex_summary", "none")).strip() or "none",
            codex_personality=str(llm_raw.get("codex_personality", "none")).strip() or "none",
            codex_request_timeout=float(llm_raw.get("codex_request_timeout", 180.0)),
            codex_max_retries=int(llm_raw.get("codex_max_retries", 2)),
            codex_cleanup_threads=bool(llm_raw.get("codex_cleanup_threads", True)),
            codex_workspace_dir=_optional_string(llm_raw.get("codex_workspace_dir")) or str(Path.home() / ".codex" / "tradingagents-workspace"),
            codex_binary=_optional_string(llm_raw.get("codex_binary")),
        ),
        translation=TranslationSettings(
            backend=str(translation_raw.get("backend", "nllb_ct2")).strip().lower() or "nllb_ct2",
            model=str(translation_raw.get("model", "nllb-200-distilled-600m")).strip()
            or "nllb-200-distilled-600m",
            model_path=_optional_string(translation_raw.get("model_path")),
            tokenizer_path=_optional_string(translation_raw.get("tokenizer_path")),
            device=str(translation_raw.get("device", "auto")).strip() or "auto",
            compute_type=str(translation_raw.get("compute_type", "auto")).strip() or "auto",
            max_chunk_chars=max(400, int(translation_raw.get("max_chunk_chars", 1800))),
            allow_llm_fallback=bool(translation_raw.get("allow_llm_fallback", True)),
            allow_large_model=bool(translation_raw.get("allow_large_model", False)),
        ),
        storage=StorageSettings(
            archive_dir=archive_dir,
            site_dir=site_dir,
        ),
        site=SiteSettings(
            title=str(site_raw.get("title", "TradingAgents Daily Reports")).strip() or "TradingAgents Daily Reports",
            subtitle=str(
                site_raw.get(
                    "subtitle",
                    "Automated multi-agent market analysis powered by Codex",
                )
            ).strip()
            or "Automated multi-agent market analysis powered by Codex",
            max_runs_on_homepage=int(site_raw.get("max_runs_on_homepage", 30)),
        ),
        portfolio=PortfolioSettings(
            enabled=bool(portfolio_raw.get("enabled", False)),
            profile_path=(
                _resolve_path(portfolio_raw.get("profile_path", "portfolio_profiles.toml"), base_dir)
                if portfolio_raw.get("enabled", False) or portfolio_raw.get("profile_path")
                else None
            ),
            profile_name=str(portfolio_raw.get("profile_name", "kr_kis_default")).strip() or "kr_kis_default",
            continue_on_error=bool(portfolio_raw.get("continue_on_error", True)),
            semantic_judge_enabled=bool(portfolio_raw.get("semantic_judge_enabled", False)),
            action_judge_enabled=bool(portfolio_raw.get("action_judge_enabled", False)),
            action_judge_top_n=max(1, int(portfolio_raw.get("action_judge_top_n", 5))),
            report_polisher_enabled=bool(portfolio_raw.get("report_polisher_enabled", True)),
        ),
        execution=ExecutionSettings(
            execution_refresh_enabled=bool(execution_raw.get("enabled", False)),
            execution_refresh_checkpoints_kst=tuple(execution_raw.get("checkpoints_kst", default_checkpoints)),
            execution_max_data_age_seconds=max(30, int(execution_raw.get("max_data_age_seconds", 180))),
            execution_publish_badges=bool(execution_raw.get("publish_badges", True)),
            execution_selective_rerun_enabled=bool(execution_raw.get("selective_rerun_enabled", True)),
            execution_llm_summary_model=_optional_string(execution_raw.get("llm_summary_model")) or "gpt-5.4-mini",
            execution_publish_debug=bool(execution_raw.get("publish_debug", False)),
        ),
        config_path=config_path,
    )


def _infer_market_code(timezone_name: str) -> str:
    normalized = str(timezone_name or "").strip().lower()
    if normalized in {"asia/seoul", "asia/tokyo"}:
        return "KR"
    if normalized.startswith("america/"):
        return "US"
    return "KR"


def _normalize_market_code(value: str, *, timezone_name: str) -> str:
    market = str(value or "").strip().upper()
    if market in {"US", "KR"}:
        return market
    return _infer_market_code(timezone_name)


def _default_execution_checkpoints_kst(market_code: str) -> tuple[str, ...]:
    normalized = str(market_code or "").strip().upper()
    if normalized == "US":
        # US checkpoints are derived from New York regular session anchors:
        # pre-open (09:20 ET), early-session checkpoint (10:00 ET), near-close (15:30 ET),
        # then converted to KST with DST awareness.
        return _convert_market_times_to_kst(
            market_timezone="America/New_York",
            anchor_times=(time(9, 20), time(10, 0), time(15, 30)),
        )
    return DEFAULT_EXECUTION_CHECKPOINTS_BY_MARKET["KR"]


def _convert_market_times_to_kst(
    *,
    market_timezone: str,
    anchor_times: tuple[time, ...],
) -> tuple[str, ...]:
    market_tz = ZoneInfo(market_timezone)
    kst_tz = ZoneInfo("Asia/Seoul")
    market_now = datetime.now(market_tz)
    result: list[str] = []
    for anchor in anchor_times:
        market_dt = datetime.combine(market_now.date(), anchor, tzinfo=market_tz)
        result.append(market_dt.astimezone(kst_tz).strftime("%H:%M"))
    return tuple(result)


def with_overrides(
    config: ScheduledAnalysisConfig,
    *,
    archive_dir: str | Path | None = None,
    site_dir: str | Path | None = None,
    tickers: Iterable[str] | None = None,
    ticker_universe_mode: str | None = None,
    trade_date: str | None = None,
    run_mode: str | None = None,
) -> ScheduledAnalysisConfig:
    run = config.run
    storage = config.storage

    if tickers is not None:
        run = replace(run, tickers=_normalize_tickers(tickers))
    if ticker_universe_mode:
        run = replace(run, ticker_universe_mode=_normalize_ticker_universe_mode(ticker_universe_mode))
    if trade_date:
        run = replace(run, trade_date_mode="explicit", explicit_trade_date=_validate_trade_date(trade_date))
    if run_mode:
        run = replace(run, run_mode=_normalize_run_mode(run_mode))
    if archive_dir:
        storage = replace(storage, archive_dir=Path(archive_dir).expanduser().resolve())
    if site_dir:
        storage = replace(storage, site_dir=Path(site_dir).expanduser().resolve())

    return replace(config, run=run, storage=storage)


def _normalize_tickers(values: Iterable[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    seen_identity: set[str] = set()
    for value in values:
        ticker = normalize_ticker_symbol(str(value))
        if not ticker or ticker in seen:
            continue
        identity_key = _ticker_identity_key(ticker)
        if identity_key in seen_identity:
            continue
        seen.add(ticker)
        seen_identity.add(identity_key)
        normalized.append(ticker)
    return normalized


def _ticker_identity_key(ticker: str) -> str:
    normalized = str(ticker or "").strip().upper()
    if normalized.endswith(".KS") or normalized.endswith(".KQ"):
        base = normalized[:-3]
        if len(base) == 6 and base.isdigit():
            return f"KR:{base}"
    return normalized


def _normalize_ticker_universe_mode(value: object) -> str:
    mode = str(value or "config_only").strip().lower()
    if mode not in VALID_TICKER_UNIVERSE_MODES:
        raise ValueError(
            f"Unsupported ticker_universe_mode '{mode}'. "
            f"Expected one of: {', '.join(sorted(VALID_TICKER_UNIVERSE_MODES))}."
        )
    return mode


def _normalize_run_mode(value: object) -> str:
    mode = str(value or "full").strip().lower()
    if mode not in VALID_RUN_MODES:
        raise ValueError(
            f"Unsupported run_mode '{mode}'. "
            f"Expected one of: {', '.join(sorted(VALID_RUN_MODES))}."
        )
    return mode


def _normalize_analysts(values: Iterable[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        analyst = str(value).strip().lower()
        if analyst not in ALL_ANALYSTS:
            raise ValueError(
                f"Unsupported analyst '{analyst}'. Expected only: {', '.join(ALL_ANALYSTS)}."
            )
        if analyst in seen:
            continue
        seen.add(analyst)
        normalized.append(analyst)
    return normalized or list(ALL_ANALYSTS)


def _normalize_ticker_name_overrides(values: dict[str, object]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in (values or {}).items():
        ticker = normalize_ticker_symbol(str(key))
        name = str(value).strip()
        if ticker and name:
            normalized[ticker] = name
    return normalized


def _resolve_path(value: str | os.PathLike[str], base_dir: Path) -> Path:
    expanded = os.path.expanduser(os.path.expandvars(str(value)))
    path = Path(expanded)
    if not path.is_absolute():
        path = (base_dir / path).resolve()
    return path


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _validate_trade_date(value: str) -> str:
    text = value.strip()
    if len(text) != 10 or text[4] != "-" or text[7] != "-":
        raise ValueError(f"Invalid trade date '{value}'. Expected YYYY-MM-DD.")
    return text
