from datetime import datetime, timedelta, timezone

import pytest

from tradingagents.execution.quant_policy import propose_weights, purged_folds


NOW = datetime(2026, 11, 1, 20, tzinfo=timezone.utc)
POLICY = {"version": "fixture-v1", "frozen_at": "2026-09-01T00:00:00Z", "currency": "USD",
          "core": ["CORE1", "CORE2"], "satellite": ["SAT1", "SAT2"], "budget_core": .5,
          "budget_satellite": .3, "cash_floor": .2, "asset_cap": .5, "trend_window": 3,
          "momentum_window": 3, "volatility_window": 3, "annual_volatility_target": .15,
          "maximum_stale_days": 3, "minimum_turnover": 10000, "satellite_limit": 1,
          "factor_weights": {"quality": .5, "revision": .5}, "cost_version": "costs-v1"}


def _evidence(at, **content):
    return {"effective_at": at.isoformat(), "known_at": at.isoformat(), "source": "synthetic", **content}


def _asset(prices, score=.4, currency="USD"):
    return {
        "security": _evidence(NOW - timedelta(days=70), currency=currency, eligible=True),
        "liquidity": _evidence(NOW - timedelta(days=1), turnover=12000),
        "closes": [_evidence(NOW - timedelta(days=len(prices) - i), price=price, currency=currency,
                              basis="total_return") for i, price in enumerate(prices)],
        "factors": {key: _evidence(NOW - timedelta(days=1), value=score) for key in ("quality", "revision")},
    }


def test_core_and_satellite_cash_and_dated_veto_are_separate():
    evidence = {"CORE1": _asset([100, 101, 102, 103, 104]), "CORE2": _asset([100, 99, 98, 97, 96]),
                "SAT1": _asset([100, 101, 102, 103, 104]), "SAT2": _asset([100, 101, 102, 103, 104], .1)}
    result = propose_weights(POLICY, evidence, analysis_as_of=NOW,
                             vetoes={"CORE1": _evidence(NOW + timedelta(seconds=1), decision="VETO", reason="future"),
                                     "SAT1": _evidence(NOW, decision="DEFER", reason="dated filing")},
                             settled_cash=_evidence(NOW, amount=100, currency="USD"),
                             unsettled_cash=_evidence(NOW, amount=30, currency="USD"))
    assert result["quant_only"]["weights"] == {"CORE1": .5, "SAT1": .3}
    assert result["after_veto"]["weights"] == {"CORE1": .5}
    assert result["cash_evidence"] == {"settled": 100, "unsettled": 30}
    assert result["universe_count"] == 4 and not result["execution_authority"]


def test_future_filing_currency_mismatch_and_empty_providers_are_excluded():
    mixed = _asset([100, 101, 102, 103, 104], currency="KRW")
    unavailable = _asset([100, 101, 102, 103, 104])
    unavailable["factors"]["revision"]["known_at"] = (NOW + timedelta(days=1)).isoformat()
    result = propose_weights(POLICY, {"CORE1": mixed, "SAT1": unavailable}, analysis_as_of=NOW)
    assert result["quant_only"]["cash_weight"] == 1
    assert set(result["rejected_evidence"]) == {"CORE1", "CORE2", "SAT1", "SAT2"}
    with pytest.raises(ValueError, match="budget"):
        propose_weights({**POLICY, "cash_floor": .3}, {}, analysis_as_of=NOW)


def test_purging_removes_overlap_and_keeps_final_holdout_outside_models():
    def stamp(day):
        return f"2026-10-{day:02d}T00:00:00Z"

    def sample(key, event, outcome, known):
        return dict(id=key, decision_at=stamp(event), outcome_end=stamp(outcome), outcome_known_at=stamp(known))

    rows = [sample("clean", 2, 4, 5), sample("purged", 3, 10, 11),
            sample("evaluation", 12, 13, 14), sample("late-evaluation", 12, 22, 23), sample("holdout", 20, 21, 22)]
    result = purged_folds(rows, [{"train_before": stamp(9), "test_start": stamp(12), "test_end": stamp(15)}],
                          frozen_at=stamp(1), holdout_start=stamp(20), analysis_as_of=stamp(30))
    assert result["folds"][0]["training"] == ["clean"]
    assert result["folds"][0]["purged"] == ["purged"]
    assert result["folds"][0]["evaluation"] == ["evaluation"]
    assert result["folds"][0]["purged_evaluation"] == ["late-evaluation"]
    assert result["holdout"] == ["holdout"]


@pytest.mark.parametrize("field", ["effective_at", "known_at"])
@pytest.mark.parametrize("clock", [None, "not-a-date", "2026-11-01T18:00:00", "2026-11-02T00:00:00Z"])
def test_quant_rank_excludes_unverified_factor_clocks(field, clock):
    asset = _asset([100, 101, 102, 103, 104])
    revision = asset["factors"]["revision"]
    if clock is None:
        revision.pop(field)
    else:
        revision[field] = clock
    result = propose_weights(POLICY, {"SAT1": asset}, analysis_as_of=NOW)
    assert "SAT1" in result["rejected_evidence"] and not result["quant_only"]["weights"]


@pytest.mark.parametrize("field", ["decision_at", "outcome_end", "outcome_known_at"])
@pytest.mark.parametrize("clock", [None, "not-a-date", "2026-10-12T00:00:00", "2026-10-31T00:00:00Z"])
def test_purging_refuses_unverified_outcome_clock(field, clock):
    row = {"id": "fixture", "decision_at": "2026-10-12T00:00:00Z", "outcome_end": "2026-10-13T00:00:00Z",
           "outcome_known_at": "2026-10-14T00:00:00Z"}
    if clock is None:
        row.pop(field)
    else:
        row[field] = clock
    with pytest.raises(ValueError):
        purged_folds([row], [{"train_before": "2026-10-09T00:00:00Z", "test_start": "2026-10-12T00:00:00Z",
                             "test_end": "2026-10-15T00:00:00Z"}], frozen_at="2026-10-01T00:00:00Z",
                     holdout_start="2026-10-20T00:00:00Z", analysis_as_of="2026-10-30T00:00:00Z")
