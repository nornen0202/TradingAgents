from copy import deepcopy
import json

import pytest

from tradingagents.execution.research_comparison import ARMS, compare_replays, main


DAYS = ("2026-07-02", "2026-07-06", "2026-07-07")
AS_OF = "2026-07-08T20:00:00+00:00"


def fixture():
    policy = {"plan_sha256": "a" * 64, "frozen_at": "2026-06-01T00:00:00+00:00", "market": "US",
              "start": DAYS[0], "end": DAYS[-1], "initial_nav": 1000, "minimum_sessions": 3,
              "costs": {"low": "b" * 64, "high": "c" * 64}, "data_class": "synthetic",
              "external_cashflows": dict(zip(DAYS, (0, 100, 0))),
              "block_length": 2, "resamples": 200, "seed": 7}
    series = {}
    for scenario, digest in policy["costs"].items():
        series[scenario] = {}
        for arm in ARMS:
            nav = policy["initial_nav"]
            rows = []
            for n, day in enumerate(DAYS):
                cash = 100 if n == 1 else 0
                commission = 1 if scenario == "low" else 5
                nav = nav + cash + (8 if arm == "llm_veto" else 6) - commission
                rows.append({"status": "VERIFIED", "session": day, "available_at": day + "T21:00:00+00:00",
                             "cost_digest": digest, "closing_nav": nav, "external_cashflow": cash,
                             "commission": commission, "slippage": 1, "fx_cost": 0, "tax": 0,
                             "dividend_net": 0, "exposure": .35, "llm_cost": .01 if arm == "llm_veto" else 0,
                             "llm_calls": int(arm == "llm_veto"), "round_trips": 1,
                             "regime": "trend" if n < 2 else "range"})
            series[scenario][arm] = rows
    return policy, series


def test_same_cashflows_same_closes_cost_sensitivity_and_ablation():
    plan, scenarios = fixture()
    result = compare_replays(plan, scenarios, analysis_as_of=AS_OF)
    low, high = (result["results"][scenario] for scenario in ("low", "high"))
    assert result["data_class"] == "synthetic" and result["live_order_authority"] is False
    assert result["expected_sessions"] == 3  # July 3 was an exchange holiday.
    assert low["status"] == high["status"] == "COMPARABLE"
    assert low["eligible_sessions"] == 3
    assert low["arms"]["llm_veto"]["cost_totals"]["llm_calls"] == 3
    assert low["arms"]["llm_veto"]["regime_samples"] == {"trend": 2, "range": 1}
    assert low["arms"]["quant_only"]["net_time_weighted_return"] > high["arms"]["quant_only"]["net_time_weighted_return"]
    assert low["paired"]["llm_veto_vs_quant_only"]["paired_block_bootstrap_95pct"][0] > 0
    assert low["paired"]["quant_only_vs_dca"]["mean_paired_daily_excess"] == 0


@pytest.mark.parametrize("issue", ["cashflow", "future_receipt", "no_tax", "wrong_costs", "missing", "bad_clock"])
def test_invalid_observations_stay_in_the_expected_denominator(issue):
    plan, scenarios = fixture()
    arm = scenarios["low"]["dca"]
    if issue == "missing":
        arm.pop()
    else:
        key, value = {"cashflow": ("external_cashflow", 101), "future_receipt": ("available_at", "2026-07-09T00:00:00+00:00"),
                      "no_tax": ("tax", None), "wrong_costs": ("cost_digest", "d" * 64),
                      "bad_clock": ("available_at", "never")}[issue]
        arm[1][key] = value
    result = compare_replays(plan, scenarios, analysis_as_of=AS_OF)
    assert result["expected_sessions"] == 3
    incomplete = result["results"]["low"]
    assert incomplete["eligible_sessions"] == 2
    assert incomplete["status"] == "INSUFFICIENT_COMPARABLE_SESSIONS" and "paired" not in incomplete
    assert result["results"]["high"]["status"] == "COMPARABLE"


def test_comparison_cli_uses_scoped_replays_and_enforces_frozen_plan(tmp_path, capsys):
    plan, scenarios = fixture()
    broken = deepcopy(plan)
    broken["frozen_at"] = "2026-07-02T12:00:00+00:00"
    with pytest.raises(ValueError, match="frozen plan"):
        compare_replays(broken, scenarios, analysis_as_of=AS_OF)
    input_file = tmp_path / "input.json"
    input_file.write_text(json.dumps({"policy": plan, "series": scenarios}))
    assert main([str(input_file), "--as-of", AS_OF]) == 0
    assert json.loads(capsys.readouterr().out)["results"]["low"]["status"] == "COMPARABLE"


def test_cost_sensitivity_keeps_one_cashflow_schedule_and_non_degenerate_blocks():
    plan, scenarios = fixture()
    for arm in ARMS:
        scenarios["high"][arm][1]["external_cashflow"] = 150
    report = compare_replays(plan, scenarios, analysis_as_of=AS_OF)
    assert report["results"]["low"]["status"] == "COMPARABLE"
    assert report["results"]["high"]["cashflow_mismatch_sessions"] == [DAYS[1]]
    with pytest.raises(ValueError, match="sample policy"):
        compare_replays(plan | {"block_length": len(DAYS)}, scenarios, analysis_as_of=AS_OF)
