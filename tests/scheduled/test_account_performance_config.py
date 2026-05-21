from pathlib import Path

from tradingagents.scheduled.config import _load_portfolio_performance_settings


def test_min_coverage_ratio_zero_is_preserved(tmp_path: Path):
    settings = _load_portfolio_performance_settings({"min_coverage_ratio": 0.0}, base_dir=tmp_path)

    assert settings.min_coverage_ratio == 0.0


def test_min_coverage_ratio_missing_defaults_to_point_eight(tmp_path: Path):
    settings = _load_portfolio_performance_settings({}, base_dir=tmp_path)

    assert settings.min_coverage_ratio == 0.8


def test_min_coverage_ratio_is_clamped(tmp_path: Path):
    high = _load_portfolio_performance_settings({"min_coverage_ratio": 1.2}, base_dir=tmp_path)
    low = _load_portfolio_performance_settings({"min_coverage_ratio": -0.5}, base_dir=tmp_path)

    assert high.min_coverage_ratio == 1.0
    assert low.min_coverage_ratio == 0.0


def test_broker_performance_settings_are_loaded(tmp_path: Path):
    settings = _load_portfolio_performance_settings(
        {
            "broker_return_baseline_path": "broker.json",
            "broker_period_start": "2026-04-13",
            "broker_period_end": "2026-05-12",
            "prefer_broker_reported_performance": False,
            "show_snapshot_performance_when_unreconciled": True,
        },
        base_dir=tmp_path,
    )

    assert settings.broker_return_baseline_path == tmp_path / "broker.json"
    assert settings.broker_period_start == "2026-04-13"
    assert settings.broker_period_end == "2026-05-12"
    assert settings.prefer_broker_reported_performance is False
    assert settings.show_snapshot_performance_when_unreconciled is True


def test_etf_dca_benchmark_settings_are_loaded(tmp_path: Path):
    settings = _load_portfolio_performance_settings(
        {},
        etf_dca_raw={
            "enabled": True,
            "require_dated_cashflows": True,
            "cashflow_source": "manual_csv",
            "manual_cashflow_csv_path": "cashflows.csv",
            "price_history_path": "etf_prices.json",
            "fx_history_path": "fx.json",
            "period_start": "2026-04-13",
            "period_end": "2026-05-12",
            "price_basis": "close",
            "cashflow_trade_timing": "same_day_close",
            "withdrawal_policy": "pro_rata_current_weights",
            "min_initial_seed_krw": 10_000,
            "core_satellite_policy_enabled": True,
            "instruments": {
                "kospi200": {
                    "display_name": "KOSPI200 ETF",
                    "ticker": "069500.KS",
                    "currency": "KRW",
                },
                "sp500_krw": {
                    "display_name": "S&P500 KRW ETF",
                    "ticker": "360750.KS",
                    "currency": "KRW",
                },
            },
            "portfolios": {
                "blended_default": {
                    "weights": {"kospi200": 0.7, "sp500_krw": 0.3},
                }
            },
        },
        base_dir=tmp_path,
    )

    assert settings.etf_alternative_enabled is True
    assert settings.cashflow_baseline_path == tmp_path / "cashflows.csv"
    assert settings.etf_price_history_path == tmp_path / "etf_prices.json"
    assert settings.etf_fx_history_path == tmp_path / "fx.json"
    assert settings.etf_alternative_symbols["KOSPI200"] == "069500.KS"
    assert settings.etf_alternative_symbols["SP500_KRW"] == "360750.KS"
    assert settings.etf_alternative_blended_weights == {"KOSPI200": 0.7, "SP500_KRW": 0.3}
    assert settings.etf_dca_require_dated_cashflows is True
    assert settings.etf_dca_cashflow_source == "manual_csv"
    assert settings.etf_dca_period_start == "2026-04-13"
    assert settings.etf_dca_period_end == "2026-05-12"
    assert settings.etf_dca_price_basis == "close"
    assert settings.etf_dca_cashflow_trade_timing == "same_day_close"
    assert settings.etf_dca_withdrawal_policy == "pro_rata_current_weights"
    assert settings.etf_dca_min_initial_seed_krw == 10_000
    assert settings.etf_dca_core_satellite_policy_enabled is True


def test_default_account_cashflows_path_is_discovered(tmp_path: Path):
    default_path = tmp_path / "account_cashflows.csv"
    default_path.write_text("date,type,amount_krw\n2026-05-01,DEPOSIT,10000\n", encoding="utf-8")

    settings = _load_portfolio_performance_settings({}, base_dir=tmp_path)

    assert settings.cashflow_baseline_path == default_path


def test_manual_cashflow_path_overrides_default_discovery(tmp_path: Path):
    (tmp_path / "account_cashflows.csv").write_text("date,type,amount_krw\n2026-05-01,DEPOSIT,10000\n", encoding="utf-8")

    settings = _load_portfolio_performance_settings(
        {},
        etf_dca_raw={"manual_cashflow_csv_path": "manual.csv"},
        base_dir=tmp_path,
    )

    assert settings.cashflow_baseline_path == tmp_path / "manual.csv"
