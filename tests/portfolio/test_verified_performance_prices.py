import json
import sqlite3

import pytest

from tradingagents.performance.action_outcomes import (
    initialize_action_tracker,
    record_run_recommendations,
    summarize_action_performance,
    update_action_outcomes,
)
from tradingagents.performance.evidence_audit import audit_snapshot


KNOWN = "2026-09-30T20:00:00+00:00"
MEASURED = "2026-10-08T23:00:00+00:00"


def _reference(currency="USD", **changes):
    return {"price": 100, "currency": currency, "basis": "unadjusted",
            "source": "synthetic-quote", "observed_at": KNOWN, **changes}


def _prices(currency="USD", **changes):
    return {"AAPL": [
        {"date": f"2026-10-0{day}", "close": 100 + day, "currency": currency,
         "basis": "unadjusted", "source": "synthetic-daily", "split_ratio": 1, "dividend": 0, **changes}
        for day in range(1, 7)
    ]}


def _recommendation(tmp_path, reference):
    db = tmp_path / "performance.sqlite"
    run = tmp_path / "run"
    portfolio = run / "portfolio-private"
    portfolio.mkdir(parents=True)
    (run / "run.json").write_text(json.dumps({"run_id": "fixture", "finished_at": KNOWN}))
    (portfolio / "portfolio_report.json").write_text(json.dumps({"actions": [{
        "canonical_ticker": "AAPL", "action_now": "ADD_NOW", "position_metrics": {"market_price_krw": 150000},
        "data_health": {"price_reference": reference},
    }]}))
    assert record_run_recommendations(run, db, recorded_at=KNOWN) == 1
    return db


def test_explicit_matching_reference_appends_revision_and_preserves_legacy(tmp_path):
    db = _recommendation(tmp_path, _reference())
    assert update_action_outcomes(db, MEASURED, price_history=_prices(), recorded_at=MEASURED) == 1
    with sqlite3.connect(db) as conn:
        prior = conn.execute("SELECT * FROM action_outcomes").fetchone()
        assert conn.execute("SELECT return_5d FROM action_outcomes").fetchone()[0] < -0.99
    assert summarize_action_performance(db, analysis_as_of=MEASURED, require_verified_price=True).outcomes == 0

    kwargs = dict(price_history=_prices(), recorded_at=MEASURED, require_verified_price=True)
    assert update_action_outcomes(db, MEASURED, **kwargs) == 1
    assert update_action_outcomes(db, MEASURED, **kwargs) == 0
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT * FROM action_outcomes ORDER BY rowid").fetchall()[0] == prior
        assert conn.execute("SELECT COUNT(*) FROM action_outcomes").fetchone() == (2,)
        assert conn.execute("SELECT COUNT(*) FROM lifecycle_events WHERE kind='OUTCOME'").fetchone() == (2,)
    summary = summarize_action_performance(db, analysis_as_of=MEASURED, require_verified_price=True)
    assert summary.outcomes == 1
    assert summary.by_action["ADD_NOW"]["avg_return_5d"] == pytest.approx(0.06)


@pytest.mark.parametrize(("reference", "prices"), [
    (None, _prices()),
    (_reference("KRW"), _prices()),
    (_reference(), _prices(currency="")),
    (_reference(), _prices(split_ratio=2)),
    (_reference(), _prices(dividend=1)),
    (_reference(observed_at="2026-10-01T00:00:00+00:00"), _prices()),
])
def test_missing_wrong_currency_or_unadjusted_corporate_action_is_unscored(tmp_path, reference, prices):
    db = _recommendation(tmp_path, reference)
    assert update_action_outcomes(db, MEASURED, price_history=prices, recorded_at=MEASURED,
                                  require_verified_price=True) == 0
    summary = summarize_action_performance(db, analysis_as_of=MEASURED, require_verified_price=True)
    assert summary.recommendations == 1 and summary.outcomes == 0
    assert summary.data_quality["recommendations_without_verified_outcome"] == 1


def test_legacy_schema_gains_nullable_price_evidence(tmp_path):
    db = tmp_path / "old.sqlite"
    initialize_action_tracker(db)
    with sqlite3.connect(db) as conn:
        assert "price_reference_json" in {row[1] for row in conn.execute("PRAGMA table_info(action_recommendations)")}


def test_read_only_audit_distinguishes_screening_and_proof(tmp_path):
    db = _recommendation(tmp_path, None)
    assert update_action_outcomes(db, MEASURED, price_history=_prices(), recorded_at=MEASURED) == 1
    before = db.read_bytes()
    result = audit_snapshot(db)
    assert result["markets"]["US"]["extreme_legacy_return_candidates"] == 1
    assert result["candidate_count_proves_currency_mismatch"] is False
    assert "AAPL" not in json.dumps(result) and db.read_bytes() == before
