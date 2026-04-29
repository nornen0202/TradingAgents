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
    # KST anchors cover morning, lunch, and afternoon refresh windows.
    "KR": ("10:05", "11:05", "12:35", "14:35"),
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
    deep_model: str = "gpt-5.5"
    quick_model: str = "gpt-5.5"
    output_model: str = "gpt-5.5"
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
    execution_refresh_checkpoints_kst: tuple[str, ...] = tuple()
    execution_max_data_age_seconds: int = 180
    execution_publish_badges: bool = True
    execution_selective_rerun_enabled: bool = True
    execution_llm_summary_model: str | None = "gpt-5.5"
    execution_publish_debug: bool = False


@dataclass(frozen=True)
class SummaryImageSettings:
    enabled: bool = True
    mode: str = "deterministic_svg"
    publish_to_site: bool = True
    redact_account_values: bool = False
    image_model: str = "gpt-image-2"
    image_size: str = "1024x1536"
    image_quality: str = "medium"
    request_timeout: float = 180.0


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
class PrismDashboardSettings:
    enabled: bool = False
    mode: str = "advisory"
    local_dashboard_json_path: Path | None = None
    local_sqlite_db_path: Path | None = None
    dashboard_json_url: str | None = None
    dashboard_base_url: str = "https://analysis.stocksimulation.kr"
    timeout_seconds: float = 5.0
    max_payload_bytes: int = 5_000_000
    use_live_http: bool = False
    use_html_scraping: bool = False
    confidence_cap: float = 0.25
    market: str | None = None
    use_for_candidate_generation: bool = False
    use_for_performance_benchmark: bool = False
    use_for_ui_comparison: bool = True

    @property
    def dashboard_url(self) -> str | None:
        return self.dashboard_json_url

    @property
    def local_json_path(self) -> Path | None:
        return self.local_dashboard_json_path

    @property
    def sqlite_path(self) -> Path | None:
        return self.local_sqlite_db_path


@dataclass(frozen=True)
class ExternalDataSettings:
    prism: PrismDashboardSettings = field(default_factory=PrismDashboardSettings)

    @property
    def prism_dashboard(self) -> PrismDashboardSettings:
        return self.prism


@dataclass(frozen=True)
class ScannerSettings:
    enabled: bool = False
    market: str = "KR"
    max_candidates: int = 10
    max_new_tickers_per_run: int = 5
    include_prism_candidates: bool = True
    local_ohlcv_path: Path | None = None
    min_traded_value_krw: int = 10_000_000_000
    min_market_cap_krw: int = 500_000_000_000
    max_daily_change_pct: float = 20.0
    min_volume_ratio_to_market_avg: float = 0.2
    exclude_halted_or_low_liquidity: bool = True


@dataclass(frozen=True)
class PerformanceSettings:
    enabled: bool = False
    store_path: Path | None = None
    update_outcomes_on_run: bool = False
    price_provider: str = "none"
    price_history_path: Path | None = None
    benchmark_ticker: str | None = None
    outcome_horizons: tuple[int, ...] = (1, 3, 5, 10, 20, 60)
    price_lookback_days: int = 120


@dataclass(frozen=True)
class AlertSettings:
    enabled: bool = False
    markdown_output_path: Path | None = None
    telegram_enabled: bool = False


@dataclass(frozen=True)
class ScheduledAnalysisConfig:
    run: RunSettings
    llm: LLMSettings
    translation: TranslationSettings
    storage: StorageSettings
    site: SiteSettings
    portfolio: PortfolioSettings
    execution: ExecutionSettings
    summary_image: SummaryImageSettings
    external_data: ExternalDataSettings
    scanner: ScannerSettings
    performance: PerformanceSettings
    alerts: AlertSettings
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
    summary_image_raw = raw.get("summary_image") or {}
    external_raw = raw.get("external") or {}
    external_data_raw = raw.get("external_data") or {}
    scanner_raw = raw.get("scanner") or {}
    performance_raw = raw.get("performance") or {}
    alerts_raw = raw.get("alerts") or {}

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

    codex_model_override = _optional_string(os.getenv("TRADINGAGENTS_CODEX_MODEL"))
    quick_model_override = _optional_string(os.getenv("TRADINGAGENTS_CODEX_QUICK_MODEL")) or codex_model_override
    deep_model_override = _optional_string(os.getenv("TRADINGAGENTS_CODEX_DEEP_MODEL")) or codex_model_override
    output_model_override = _optional_string(os.getenv("TRADINGAGENTS_CODEX_OUTPUT_MODEL")) or codex_model_override
    execution_model_override = _optional_string(os.getenv("TRADINGAGENTS_EXECUTION_LLM_SUMMARY_MODEL")) or codex_model_override
    codex_workspace_override = _optional_string(os.getenv("TRADINGAGENTS_CODEX_WORKSPACE_DIR"))

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
            deep_model=deep_model_override or str(llm_raw.get("deep_model", "gpt-5.5")).strip() or "gpt-5.5",
            quick_model=quick_model_override or str(llm_raw.get("quick_model", "gpt-5.5")).strip() or "gpt-5.5",
            output_model=output_model_override or str(llm_raw.get("output_model", "gpt-5.5")).strip() or "gpt-5.5",
            codex_reasoning_effort=str(llm_raw.get("codex_reasoning_effort", "medium")).strip() or "medium",
            codex_summary=str(llm_raw.get("codex_summary", "none")).strip() or "none",
            codex_personality=str(llm_raw.get("codex_personality", "none")).strip() or "none",
            codex_request_timeout=float(llm_raw.get("codex_request_timeout", 180.0)),
            codex_max_retries=int(llm_raw.get("codex_max_retries", 2)),
            codex_cleanup_threads=bool(llm_raw.get("codex_cleanup_threads", True)),
            codex_workspace_dir=codex_workspace_override
            or _optional_string(llm_raw.get("codex_workspace_dir"))
            or str(Path.home() / ".codex" / "tradingagents-workspace"),
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
            execution_refresh_checkpoints_kst=_normalize_execution_checkpoints(
                execution_raw.get("checkpoints_kst"),
                default_checkpoints=default_checkpoints,
            ),
            execution_max_data_age_seconds=max(30, int(execution_raw.get("max_data_age_seconds", 180))),
            execution_publish_badges=bool(execution_raw.get("publish_badges", True)),
            execution_selective_rerun_enabled=bool(execution_raw.get("selective_rerun_enabled", True)),
            execution_llm_summary_model=execution_model_override or _optional_string(execution_raw.get("llm_summary_model")) or "gpt-5.5",
            execution_publish_debug=bool(execution_raw.get("publish_debug", False)),
        ),
        summary_image=SummaryImageSettings(
            enabled=bool(summary_image_raw.get("enabled", True)),
            mode=_normalize_summary_image_mode(summary_image_raw.get("mode", "deterministic_svg")),
            publish_to_site=bool(summary_image_raw.get("publish_to_site", True)),
            redact_account_values=bool(summary_image_raw.get("redact_account_values", False)),
            image_model=str(summary_image_raw.get("image_model", "gpt-image-2")).strip() or "gpt-image-2",
            image_size=str(summary_image_raw.get("image_size", "1024x1536")).strip() or "1024x1536",
            image_quality=str(summary_image_raw.get("image_quality", "medium")).strip() or "medium",
            request_timeout=float(summary_image_raw.get("request_timeout", 180.0)),
        ),
        external_data=_load_external_data_settings(
            external_raw=external_raw,
            external_data_raw=external_data_raw,
            base_dir=base_dir,
            default_market=market_code,
        ),
        scanner=_load_scanner_settings(scanner_raw, base_dir=base_dir, default_market=market_code),
        performance=_load_performance_settings(performance_raw, base_dir=base_dir),
        alerts=_load_alert_settings(alerts_raw, base_dir=base_dir),
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
    if len(normalized) == 6 and normalized.isdigit():
        return f"KR:{normalized}"
    if normalized.endswith(".KS") or normalized.endswith(".KQ"):
        base = normalized[:-3]
        if len(base) == 6 and base.isdigit():
            return f"KR:{base}"
    return normalized


def _normalize_execution_checkpoints(
    raw_value: object,
    *,
    default_checkpoints: tuple[str, ...],
) -> tuple[str, ...]:
    if raw_value is None:
        return default_checkpoints
    values = tuple(str(item).strip() for item in (raw_value or []) if str(item).strip())
    return values or default_checkpoints


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


def _normalize_summary_image_mode(value: object) -> str:
    mode = str(value or "deterministic_svg").strip().lower()
    aliases = {
        "svg": "deterministic_svg",
        "deterministic": "deterministic_svg",
        "openai": "openai_image",
        "ai": "openai_image",
    }
    mode = aliases.get(mode, mode)
    valid_modes = {"deterministic_svg", "openai_image", "both"}
    if mode not in valid_modes:
        raise ValueError(
            f"Unsupported summary_image.mode '{mode}'. "
            f"Expected one of: {', '.join(sorted(valid_modes))}."
        )
    return mode


def _load_external_data_settings(
    *,
    external_raw: dict[str, object],
    external_data_raw: dict[str, object],
    base_dir: Path,
    default_market: str,
) -> ExternalDataSettings:
    prism_raw = {}
    if isinstance(external_raw, dict):
        prism_raw = external_raw.get("prism") or {}
    if not prism_raw and isinstance(external_data_raw, dict):
        prism_raw = external_data_raw.get("prism") or external_data_raw.get("prism_dashboard") or {}
    if not isinstance(prism_raw, dict):
        prism_raw = {}
    enabled = _env_bool("PRISM_EXTERNAL_ENABLED", bool(prism_raw.get("enabled", False)))
    local_json = _env_optional_path("PRISM_DASHBOARD_JSON_PATH", _first_config_value(prism_raw, "local_dashboard_json_path", "local_json_path"), base_dir)
    sqlite_path = _env_optional_path("PRISM_SQLITE_DB_PATH", _first_config_value(prism_raw, "local_sqlite_db_path", "sqlite_path"), base_dir)
    dashboard_json_url = _env_string("PRISM_DASHBOARD_JSON_URL", _optional_string(_first_config_value(prism_raw, "dashboard_json_url", "dashboard_url")))
    dashboard_base_url = _env_string(
        "PRISM_DASHBOARD_BASE_URL",
        _optional_string(prism_raw.get("dashboard_base_url")) or "https://analysis.stocksimulation.kr",
    )
    return ExternalDataSettings(
        prism=PrismDashboardSettings(
            enabled=enabled,
            mode=str(prism_raw.get("mode", "advisory")).strip().lower() or "advisory",
            local_dashboard_json_path=local_json,
            local_sqlite_db_path=sqlite_path,
            dashboard_json_url=dashboard_json_url,
            dashboard_base_url=dashboard_base_url or "https://analysis.stocksimulation.kr",
            timeout_seconds=_env_float("PRISM_TIMEOUT_SECONDS", float(prism_raw.get("timeout_seconds", 5.0) or 5.0)),
            max_payload_bytes=_env_int("PRISM_MAX_PAYLOAD_BYTES", int(prism_raw.get("max_payload_bytes", 5_000_000) or 5_000_000)),
            use_live_http=_env_bool("PRISM_USE_LIVE_HTTP", bool(prism_raw.get("use_live_http", False))),
            use_html_scraping=_env_bool("PRISM_USE_HTML_SCRAPING", bool(prism_raw.get("use_html_scraping", False))),
            confidence_cap=float(prism_raw.get("confidence_cap", 0.25) or 0.25),
            market=_optional_string(prism_raw.get("market")) or default_market,
            use_for_candidate_generation=bool(prism_raw.get("use_for_candidate_generation", False)),
            use_for_performance_benchmark=bool(prism_raw.get("use_for_performance_benchmark", False)),
            use_for_ui_comparison=bool(prism_raw.get("use_for_ui_comparison", True)),
        )
    )


def _load_scanner_settings(raw: dict[str, object], *, base_dir: Path, default_market: str) -> ScannerSettings:
    raw = raw if isinstance(raw, dict) else {}
    return ScannerSettings(
        enabled=bool(raw.get("enabled", False)),
        market=str(raw.get("market", default_market)).strip().upper() or default_market,
        max_candidates=max(1, int(raw.get("max_candidates", 10) or 10)),
        max_new_tickers_per_run=max(0, int(raw.get("max_new_tickers_per_run", 5) or 5)),
        include_prism_candidates=bool(raw.get("include_prism_candidates", True)),
        local_ohlcv_path=_resolve_optional_path(raw.get("local_ohlcv_path"), base_dir),
        min_traded_value_krw=int(raw.get("min_traded_value_krw", 10_000_000_000) or 10_000_000_000),
        min_market_cap_krw=int(raw.get("min_market_cap_krw", 500_000_000_000) or 500_000_000_000),
        max_daily_change_pct=float(raw.get("max_daily_change_pct", 20.0) or 20.0),
        min_volume_ratio_to_market_avg=float(raw.get("min_volume_ratio_to_market_avg", 0.2) or 0.2),
        exclude_halted_or_low_liquidity=bool(raw.get("exclude_halted_or_low_liquidity", True)),
    )


def _load_performance_settings(raw: dict[str, object], *, base_dir: Path) -> PerformanceSettings:
    raw = raw if isinstance(raw, dict) else {}
    return PerformanceSettings(
        enabled=bool(raw.get("enabled", False)),
        store_path=_resolve_optional_path(raw.get("store_path"), base_dir),
        update_outcomes_on_run=bool(raw.get("update_outcomes_on_run", False)),
        price_provider=(
            _env_string("TRADINGAGENTS_PERFORMANCE_PRICE_PROVIDER", _optional_string(raw.get("price_provider")))
            or "none"
        ).strip().lower(),
        price_history_path=_env_optional_path(
            "TRADINGAGENTS_PERFORMANCE_PRICE_HISTORY_PATH",
            raw.get("price_history_path"),
            base_dir,
        ),
        benchmark_ticker=_env_string(
            "TRADINGAGENTS_PERFORMANCE_BENCHMARK_TICKER",
            _optional_string(raw.get("benchmark_ticker")),
        ),
        outcome_horizons=_normalize_int_sequence(raw.get("outcome_horizons"), default=(1, 3, 5, 10, 20, 60)),
        price_lookback_days=max(1, int(raw.get("price_lookback_days", 120) or 120)),
    )


def _load_alert_settings(raw: dict[str, object], *, base_dir: Path) -> AlertSettings:
    raw = raw if isinstance(raw, dict) else {}
    return AlertSettings(
        enabled=bool(raw.get("enabled", False)),
        markdown_output_path=_resolve_optional_path(raw.get("markdown_output_path"), base_dir),
        telegram_enabled=bool(raw.get("telegram_enabled", False)),
    )


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


def _first_config_value(raw: dict[str, object], *keys: str) -> object | None:
    for key in keys:
        if key in raw and raw[key] not in (None, ""):
            return raw[key]
    return None


def _env_string(name: str, default: str | None) -> str | None:
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


def _env_optional_path(name: str, default: object, base_dir: Path) -> Path | None:
    value = os.getenv(name)
    if value is not None:
        default = value
    return _resolve_optional_path(default, base_dir)


def _resolve_optional_path(value: object, base_dir: Path) -> Path | None:
    text = _optional_string(value)
    if text is None:
        return None
    return _resolve_path(text, base_dir)


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_int_sequence(value: object, *, default: tuple[int, ...]) -> tuple[int, ...]:
    if value is None:
        return default
    if isinstance(value, str):
        raw_values = [item.strip() for item in value.split(",")]
    else:
        try:
            raw_values = [str(item).strip() for item in value]  # type: ignore[operator]
        except TypeError:
            raw_values = [str(value).strip()]
    result: list[int] = []
    for item in raw_values:
        if not item:
            continue
        try:
            horizon = int(item)
        except ValueError:
            continue
        if horizon > 0 and horizon not in result:
            result.append(horizon)
    return tuple(result) or default


def _validate_trade_date(value: str) -> str:
    text = value.strip()
    if len(text) != 10 or text[4] != "-" or text[7] != "-":
        raise ValueError(f"Invalid trade date '{value}'. Expected YYYY-MM-DD.")
    return text
