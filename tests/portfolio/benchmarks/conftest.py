from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from tradingagents.portfolio.account_models import AccountConstraints, AccountSnapshot
from tradingagents.portfolio.performance.broker_models import BrokerPerformanceSummary
from tradingagents.portfolio.performance.etf_alternatives import build_etf_alternative_comparison


FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "etf_benchmark"


@pytest.fixture()
def etf_fixture_dir() -> Path:
    return FIXTURE_DIR


def default_snapshot() -> AccountSnapshot:
    return AccountSnapshot(
        snapshot_id="current",
        as_of="2026-05-13T15:30:00+09:00",
        broker="kis",
        account_id="kr_kis_default",
        currency="KRW",
        settled_cash_krw=0,
        available_cash_krw=0,
        buying_power_krw=0,
        total_equity_krw=15_813_494,
        snapshot_health="OK",
        positions=tuple(),
        constraints=AccountConstraints(),
    )


def default_broker_summary(fixture_dir: Path = FIXTURE_DIR) -> BrokerPerformanceSummary:
    payload = json.loads((fixture_dir / "account_actual_broker_summary.json").read_text(encoding="utf-8"))
    return BrokerPerformanceSummary(**payload)


def default_settings(
    fixture_dir: Path = FIXTURE_DIR,
    *,
    cashflow_path: Path | None = None,
    price_path: Path | None = None,
    portfolios: dict[str, dict[str, float]] | None = None,
    alpha_policy_inputs: dict | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        etf_alternative_enabled=True,
        cashflow_baseline_path=cashflow_path or fixture_dir / "cashflows_one_month.csv",
        etf_price_history_path=price_path or fixture_dir / "kr_etf_prices.json",
        etf_fx_history_path=None,
        price_provider="local_json",
        etf_alternative_symbols={},
        etf_alternative_currencies={},
        etf_alternative_labels={},
        etf_alternative_portfolios=portfolios or {},
        etf_alternative_blended_weights={},
        etf_alternative_include_start_asset=True,
        etf_alternative_transaction_cost_bps=0.0,
        etf_dca_min_initial_seed_krw=10_000,
        etf_dca_reinvest_dividends=True,
        etf_dca_period_start="",
        etf_dca_period_end="",
        alpha_policy_mode="report_only",
        alpha_policy_reduce_target_pct=15.0,
        alpha_policy_min_action_samples=5,
        alpha_policy_inputs=alpha_policy_inputs or {},
    )


def build_fixture_comparison(
    fixture_dir: Path = FIXTURE_DIR,
    *,
    settings: SimpleNamespace | None = None,
    broker_summary: BrokerPerformanceSummary | None = None,
):
    return build_etf_alternative_comparison(
        snapshot=default_snapshot(),
        settings=settings or default_settings(fixture_dir),
        summary={},
        periods=[],
        broker_performance=broker_summary or default_broker_summary(fixture_dir),
        reconciliation={"reconciliation_status": "FAILED"},
        warnings=[],
    )
