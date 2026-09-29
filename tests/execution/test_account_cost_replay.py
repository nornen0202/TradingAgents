import numpy as np
import pandas as pd
import pytest
import json
from pathlib import Path

from tradingagents.execution.account_cost_replay import (
    CostScenario,
    annual_tax,
    round_trip_loss,
    simulate_account,
)


def data(dates=None, closes=None):
    dates = pd.to_datetime(dates or ["2026-01-01", "2026-01-02", "2026-01-05"])
    values = closes or [100.0] * len(dates)
    return pd.DataFrame(
        {
            "Open": values,
            "Close": values,
            "Adj Close": values,
            "Dividends": 0.0,
            "Stock Splits": 0.0,
        },
        index=dates,
    )


def run(frame=None, scenario=None, **kwargs):
    frame = frame if frame is not None else data()
    opts = dict(
        start=str(frame.index[1].date()),
        end=str(frame.index[-1].date()),
        initial_krw=1000,
        scenario=scenario or CostScenario(0),
        fx_krw_per_unit=pd.Series(
            1.0, index=pd.date_range(frame.index[0], frame.index[-1])
        ),
        price_basis="unadjusted_no_splits",
    )
    opts.update(kwargs)
    return simulate_account(frame, "broad_hold", **opts)


def test_fees_do_not_tax_buys_and_us_levy_is_not_a_percent_error():
    us = CostScenario(0.0025, 0.0000206)
    assert us.fees(10000, "BUY") == (25, 0)
    assert us.fees(10000, "SELL") == pytest.approx((25, 0.206))
    assert CostScenario(0.00147, 0.002).fees(1_000_000, "SELL") == (1470, 2000)


def test_discount_is_applied_to_spread_not_the_principal():
    c = CostScenario(0, fx_base_spread=0.01, fx_discount=0.6)
    assert c.fx_spread == pytest.approx(0.004)
    assert round_trip_loss(c, convert_currency=True) == pytest.approx(1 - 0.996 / 1.004)
    assert round_trip_loss(c, convert_currency=False) == 0
    assert CostScenario(0, fx_base_spread=0.01, fx_discount=1).fx_spread == 0


@pytest.mark.parametrize("bad", [-1, float("nan"), float("inf"), 1])
def test_bad_commission_rejected(bad):
    with pytest.raises(ValueError):
        CostScenario(bad)


def test_integer_affordability_and_terminal_costs():
    m, curve, trades = run(scenario=CostScenario(0.1, 0.05))
    assert trades[0]["quantity"] == 9
    assert trades[-1]["side"] == "SELL"
    assert m["final_krw"] == pytest.approx(775)
    assert all(r["cash_local"] >= 0 and isinstance(r["shares"], int) for r in curve)


def test_one_share_too_expensive_leaves_cash():
    m, _, trades = run(initial_krw=99)
    assert trades == []
    assert m["final_krw"] == 99


def test_current_cost_kr_etf_has_no_stock_sales_tax():
    stock, _, _ = run(scenario=CostScenario(0.00147, 0.002))
    etf, _, _ = run(scenario=CostScenario(0.00147))
    assert etf["final_krw"] - stock["final_krw"] == pytest.approx(1.8)


def test_realized_gain_fifo_includes_fees_and_annual_allowance():
    frame = data(closes=[100, 100, 200])
    m, _, _ = run(
        frame, CostScenario(0.01, capital_gains_rate=0.22, annual_allowance_krw=100)
    )
    # 9 shares: proceeds 1782, basis 909, gain 873, taxable 773.
    assert m["realized_by_year_krw"][2026] == pytest.approx(873)
    assert m["tax_reserve_krw"] == pytest.approx(773 * 0.22)
    assert m["final_krw"] == pytest.approx(1000 - 909 + 1782 - 773 * 0.22)


def test_yearly_tax_does_not_net_losses_across_years():
    c = CostScenario(0, capital_gains_rate=0.22, annual_allowance_krw=2_500_000)
    assert annual_tax({2025: 5_000_000, 2026: -4_000_000}, c) == 550_000
    assert annual_tax({2025: 2_500_000, 2026: 2_500_000}, c) == 0


def test_fx_gain_affects_krw_tax_and_fx_conversion_happens_only_at_ends():
    fx = pd.Series(
        [1.0, 1.0, 1.0, 1.0, 2.0], index=pd.date_range("2026-01-01", "2026-01-05")
    )
    c = CostScenario(0, fx_base_spread=0.01, fx_discount=0.6, capital_gains_rate=0.22)
    m, _, trades = run(scenario=c, fx_krw_per_unit=fx)
    assert trades[0]["quantity"] == 9
    assert m["tax_reserve_krw"] == pytest.approx(900 * 0.22)
    assert m["entry_fx_cost_krw"] == pytest.approx(1000 - 1000 / 1.004)
    assert m["exit_fx_cost_krw"] > 0


def test_dividend_ex_date_uses_overnight_shares_and_is_not_spendable():
    frame = data()
    frame.loc[frame.index[1], "Dividends"] = 10  # Entry day: no entitlement.
    frame.loc[frame.index[2], "Dividends"] = 2
    m, curve, _ = run(frame, CostScenario(0, dividend_withholding=0.15))
    assert m["dividends_net_local"] == 17
    assert curve[-1]["cash_local"] == 1000
    assert m["final_krw"] == 1017


def test_adjusted_prices_and_splits_cannot_be_used_as_integer_shares():
    with pytest.raises(ValueError, match="unadjusted"):
        run(price_basis="adjusted")
    frame = data()
    frame.loc[frame.index[1], "Stock Splits"] = 2
    with pytest.raises(ValueError, match="splits"):
        run(frame)


def test_missing_fx_cannot_be_backfilled_from_future():
    fx = pd.Series([1.0], index=pd.to_datetime(["2026-01-05"]))
    with pytest.raises(ValueError, match="future"):
        run(fx_krw_per_unit=fx)


def test_old_fx_is_rejected():
    fx = pd.Series([1.0], index=pd.to_datetime(["2025-12-01"]))
    with pytest.raises(ValueError, match="older"):
        run(fx_krw_per_unit=fx)


def test_future_prices_do_not_change_prior_ledger():
    dates = pd.bdate_range("2019-01-01", periods=850)
    values = 100 * np.exp(np.arange(850) * 0.001 + 0.1 * np.sin(np.arange(850) / 30))
    frame = pd.DataFrame(
        {
            "Open": values,
            "Close": values,
            "Adj Close": values,
            "Dividends": 0.0,
            "Stock Splits": 0.0,
        },
        index=dates,
    )
    fx = pd.Series(1.0, index=pd.date_range(dates[0], dates[-1]))
    opts = dict(
        start="2020-01-01",
        end="2023-12-31",
        initial_krw=10000,
        scenario=CostScenario(0.0025),
        fx_krw_per_unit=fx,
        price_basis="unadjusted_no_splits",
        liquidate_at_end=False,
    )
    for strategy in ("balanced_80_20", "monthly_trend", "trend_vol_cap"):
        _, full, trades = simulate_account(frame, strategy, **opts)
        _, partial, partial_trades = simulate_account(
            frame.iloc[:700], strategy, **opts
        )
        assert full[: len(partial)] == partial
        assert [t for t in trades if t["date"] <= partial[-1]["date"]] == partial_trades


def test_terminal_krw_return_reconciles_with_local_return_fx_and_tax():
    frame = data(closes=[100, 100, 120])
    fx = pd.Series(
        [1.0, 1.0, 1.0, 1.0, 1.2], index=pd.date_range("2026-01-01", "2026-01-05")
    )
    c = CostScenario(0.0025, 0.0000206, 0.01, 0.6, 0.0005, capital_gains_rate=0.22)
    m, _, _ = run(frame, c, fx_krw_per_unit=fx)
    expected = (1 + m["local_return_before_capital_gains_tax_pct"] / 100) * (
        1 + m["fx_change_pct"] / 100
    )
    expected *= (1 - c.fx_spread) / (1 + c.fx_spread)
    expected -= m["tax_reserve_krw"] / m["initial_krw"]
    assert m["final_krw"] / m["initial_krw"] == pytest.approx(expected)


def test_missing_price_with_dividend_is_rejected_instead_of_dropped():
    frame = data()
    frame.loc[frame.index[1], ["Open", "Close"]] = np.nan
    frame.loc[frame.index[1], "Dividends"] = 1
    with pytest.raises(ValueError, match="finite prices"):
        run(frame)


def test_runner_records_blocked_market_without_fabricating_results(
    tmp_path, monkeypatch
):
    from tools import replay_account_costs as runner

    monkeypatch.setattr(runner, "STRATEGIES", ("broad_hold",))
    cfg = json.loads(Path("config/account_cost_replay_20260929.json").read_text())
    cfg["periods"] = [{"id": "small", "start": "2026-01-02", "end": "2026-01-05"}]
    cfg["slippage_bps_per_side"] = [0]
    cfg["additional_execution_delays"] = [0]
    for m in cfg["markets"].values():
        m["annual_allowances_krw"] = [0]
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(cfg))
    account = {
        "markets": {
            m: {"market_view_nav_krw": 1000, "as_of": "2026-01-01"}
            for m in ("KR", "US")
        }
    }
    account_path = tmp_path / "account.json"
    account_path.write_text(json.dumps(account))
    data().to_csv(tmp_path / "SPY_raw.csv")
    missing = data()
    missing.loc[missing.index[1], ["Open", "Close"]] = np.nan
    missing.to_csv(tmp_path / "069500.KS_raw.csv")
    pd.DataFrame(
        {"Close": 1.0}, index=pd.date_range("2026-01-01", "2026-01-05")
    ).to_csv(tmp_path / "KRW_X_raw.csv")
    output = tmp_path / "out"
    runner.main(
        [
            "--price-dir",
            str(tmp_path),
            "--account-review",
            str(account_path),
            "--cost-config",
            str(config_path),
            "--output",
            str(output),
        ]
    )
    result = json.loads((output / "cost_replay.json").read_text())
    assert result["strategy_runs"] == 1
    assert len(result["blocked_runs"]) == 1
    assert result["results"][0]["market"] == "US"
    assert result["data_quality"]["KR"]["missing_price_dates"] == ["2026-01-02"]
    assert result["implementation_sha256"]["ledger"]
