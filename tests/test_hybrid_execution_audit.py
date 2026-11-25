from datetime import date, datetime, timedelta, timezone
import json

import pytest

from tools.compare_hybrid_execution import compare_fills, period_stats
from tools.hybrid_audit_inputs import parse_chart
from tools.run_hybrid_quant_backtest import simulate_after_tax_walk_forward


def chart(timestamps):
    n = len(timestamps)
    return json.dumps({"chart": {"error": None, "result": [{
        "meta": {"symbol": "ETF", "exchangeTimezoneName": "America/New_York"},
        "timestamp": timestamps,
        "indicators": {"quote": [{"open": [80] * n, "close": [100] * n, "volume": [123] * n}],
                       "adjclose": [{"adjclose": [50] * n}]},
    }]}})


def test_reconstruction_bounds_local_dates_and_keeps_open_on_close_basis():
    # 00:00 UTC is still the preceding exchange-local date.
    start = datetime(2026, 1, 6, tzinfo=timezone.utc).timestamp()
    rows, gaps = parse_chart(chart([None, "bad", start, start + 86400]), "ETF", "US",
                             "2026-01-05", "2026-01-05")
    assert rows == [{"date": "2026-01-05", "open": 40, "close": 50, "volume": 123, "executable_volume": 123}]
    assert gaps == {"invalid_date": 2, "outside_dates": 1}
    with pytest.raises(ValueError, match="No dated"):
        parse_chart(chart([]), "ETF", "US", "2026-01-05", "2026-01-05")


def test_next_observed_open_uses_prior_target_and_never_fills_a_missing_quote(monkeypatch):
    def proposal(policy, bars, *, analysis_as_of, **kwargs):
        return {"after_veto": {"weights": {"ETF": 0.99}}}

    monkeypatch.setattr("tools.run_hybrid_quant_backtest.evaluate_hybrid_portfolio_proposal", proposal)
    days = [(date(2025, 4, 1) + timedelta(days=i)).isoformat() for i in range(95)]
    bars = [{"date": d, "open": 10, "close": 10, "volume": 10} for d in days]
    bars[71].update(open=None, close=1000)
    bars[72].update(open=1, executable_volume=0)
    bars[73].update(open=20)
    traces = {}
    for timing in ("same_close", "next_open"):
        traces[timing] = {}
        simulate_after_tax_walk_forward({"ETF": bars}, market="US", core_tickers=["ETF"], satellite_tickers=[],
                                        benchmark_ticker="ETF", fill_timing=timing, audit_traces=traces[timing])
    close, opening = (traces[key]["buy_and_hold"] for key in ("same_close", "next_open"))
    assert close["signals"] == opening["signals"] == {days[70]: {"ETF": .99}}
    assert opening["fills"] == [(days[70], days[73], "ETF", "buy", 20)]
    assert opening["missing_quotes"] == [(days[71], "ETF"), (days[72], "ETF")]
    assert opening["nav"][:3] == [10000] * 3
    assert opening["nav"][3] == pytest.approx(100 + 9900 * .999 / 20 * 10)
    assert compare_fills(close, opening)["median_open_minus_close_bps"] == 10000
    stats = period_stats(opening, days[73], days[73])
    assert stats["net_time_weighted_return"] == pytest.approx(opening["nav"][3] / 10000 - 1)
    assert stats["fills"] == stats["marks"] == stats["returns"] == 1
    assert stats["sharpe_rf_zero"] is None
