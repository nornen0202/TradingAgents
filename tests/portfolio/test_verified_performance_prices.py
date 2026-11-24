import hashlib
import json
import sqlite3
from datetime import date, timedelta

import pytest

from tradingagents.performance.action_outcomes import (
    initialize_action_tracker,
    record_run_recommendations,
    summarize_action_performance,
    update_action_outcomes,
)
from tradingagents.performance.evidence_audit import audit_snapshot
from tradingagents.performance.price_history import load_price_history_for_recommendations
from tradingagents.performance.price_revisions import append_price_revision, main as revision_cli


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


def _recommendation(tmp_path, reference, *, legacy=True):
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
    if legacy:
        # Emulate a pre-contract writer for historic revision tests.
        with sqlite3.connect(db) as conn:
            conn.execute("UPDATE action_recommendations SET recommended_price=150000, "
                         "native_reference_state=NULL, price_reference_json=?", (json.dumps(reference),))
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


def test_reviewed_historical_reference_is_asof_bound_idempotent_and_reversible(tmp_path):
    db = _recommendation(tmp_path, None)
    assert update_action_outcomes(db, MEASURED, price_history=_prices(), recorded_at=MEASURED) == 1
    fixture = {"recommendation_id": 1, "run_id": "fixture", "ticker": "AAPL", "decided_at": KNOWN,
               "parent_id": None, "reference": _reference(), "source_digest": "a" * 64}
    preview = append_price_revision(db, fixture, clock=lambda: MEASURED)
    assert preview["state"] == "PREVIEW"
    price_day = "2026-10-09"
    past = "2026-10-07T19:00:00+00:00"
    kwargs = {"price_history": _prices(), "require_verified_price": True}
    assert not load_price_history_for_recommendations(db, asof_date=price_day, require_verified_price=True).due_recommendation_ids
    assert append_price_revision(db, fixture, clock=lambda: MEASURED, apply=True)["revision_id"] == preview["revision_id"]
    assert append_price_revision(db, fixture, clock=lambda: MEASURED, apply=True)["state"] == "ALREADY_RECORDED"
    assert load_price_history_for_recommendations(db, asof_date=price_day, require_verified_price=True).due_recommendation_ids == (1,)
    assert update_action_outcomes(db, past, **kwargs) == 0
    assert update_action_outcomes(db, MEASURED, recorded_at=MEASURED, **kwargs) == 1
    later = "2026-10-10T20:00:00+00:00"
    invalidation = fixture | {"reference": None, "source_digest": "b" * 64}
    with pytest.raises(ValueError, match="parent is stale"):
        append_price_revision(db, invalidation, clock=lambda: later, apply=True)
    invalidation["parent_id"] = preview["revision_id"]
    append_price_revision(db, invalidation, clock=lambda: later, apply=True)
    assert update_action_outcomes(db, later, recorded_at=later, **kwargs) == 0
    assert summarize_action_performance(db, analysis_as_of=later, require_verified_price=True).outcomes == 0
    before = summarize_action_performance(db, analysis_as_of=MEASURED, require_verified_price=True)
    assert before.by_action["ADD_NOW"]["avg_return_5d"] == pytest.approx(.06)
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM action_outcomes").fetchone() == (2,)
        assert conn.execute("SELECT COUNT(*) FROM action_price_revisions").fetchone() == (2,)
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            conn.execute("DELETE FROM action_price_revisions")


def test_revision_cli_writes_only_a_verified_copy_and_rejects_unmatched_evidence(tmp_path):
    db = _recommendation(tmp_path, None)
    proof, attestation, clone = (tmp_path / name for name in ("proof", "attestation.json", "revised.sqlite"))
    proof.write_bytes(b"synthetic receipt")
    fixture = {"recommendation_id": 1, "run_id": "fixture", "ticker": "AAPL", "decided_at": KNOWN,
               "parent_id": None, "reference": _reference(), "source_digest": "a" * 64}
    attestation.write_text(json.dumps(fixture))
    paths = [str(db), str(attestation), str(proof), "--revised-copy", str(clone)]
    with pytest.raises(ValueError, match="source digest"):
        revision_cli(paths)
    assert not clone.exists()
    fixture["source_digest"] = hashlib.sha256(proof.read_bytes()).hexdigest()
    attestation.write_text(json.dumps(fixture))
    original = db.read_bytes()
    assert revision_cli(paths) == 0
    assert db.read_bytes() == original
    with sqlite3.connect(clone) as conn:
        assert conn.execute("PRAGMA quick_check").fetchone() == ("ok",)
        assert conn.execute("SELECT COUNT(*) FROM action_price_revisions").fetchone() == (1,)
    with pytest.raises(FileExistsError):
        revision_cli(paths)


def test_summary_selects_one_visible_outcome_and_does_not_backdate_ingestion(tmp_path):
    db = _recommendation(tmp_path, _reference())
    later = "2026-10-10T20:00:00+00:00"
    last = "2026-10-11T20:00:00+00:00"
    assert update_action_outcomes(db, MEASURED, price_history=_prices(), recorded_at=MEASURED) == 1
    offset_ingestion = "2026-10-08T20:00:00-07:00"
    assert update_action_outcomes(db, MEASURED, price_history=_prices(), recorded_at=offset_ingestion, require_verified_price=True) == 1
    assert summarize_action_performance(db, analysis_as_of=MEASURED, require_verified_price=True).outcomes == 0
    assert summarize_action_performance(db, analysis_as_of=later, require_verified_price=True).outcomes == 1
    assert update_action_outcomes(db, last, price_history=_prices(), recorded_at=last, require_verified_price=True) == 1
    summary = summarize_action_performance(db, analysis_as_of=last)
    assert summary.recommendations == summary.outcomes == 1
    assert summary.by_action["ADD_NOW"]["avg_return_5d"] == pytest.approx(.06)
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM action_outcomes").fetchone() == (3,)


def test_direct_refresh_remeasures_completed_outcome_after_price_revision(tmp_path):
    db = _recommendation(tmp_path, _reference())
    original = _prices()["AAPL"][0]
    series = {"AAPL": [original | {"date": (date(2026, 10, 1) + timedelta(days=i)).isoformat(), "close": 101 + i}
                       for i in range(62)]}
    complete = "2026-12-02T20:00:00+00:00"
    revision_at = "2026-12-03T20:00:00+00:00"
    kwargs = dict(price_history=series, require_verified_price=True)
    assert update_action_outcomes(db, complete, recorded_at=complete, **kwargs) == 1
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT return_60d FROM action_outcomes").fetchone()[0] is not None
    fixture = {"recommendation_id": 1, "run_id": "fixture", "ticker": "AAPL", "decided_at": KNOWN,
               "parent_id": None, "reference": _reference() | {"price": 105}, "source_digest": "a" * 64}
    append_price_revision(db, fixture, clock=lambda: revision_at, apply=True)
    assert update_action_outcomes(db, revision_at, recorded_at=revision_at, **kwargs) == 1
    assert update_action_outcomes(db, revision_at, recorded_at=revision_at, **kwargs) == 0
    assert summarize_action_performance(db, analysis_as_of=revision_at, require_verified_price=True).outcomes == 1


def test_old_corporate_action_outside_the_reference_window_does_not_block_fresh_outcome(tmp_path):
    db = _recommendation(tmp_path, _reference())
    pricing = _prices()
    historical_split = pricing["AAPL"][0] | {"date": "2026-09-01", "split_ratio": 2}
    pricing["AAPL"].insert(0, historical_split)
    assert update_action_outcomes(db, MEASURED, price_history=pricing, recorded_at=MEASURED,
                                  require_verified_price=True) == 1
    summary = summarize_action_performance(db, analysis_as_of=MEASURED, require_verified_price=True)
    assert summary.by_action["ADD_NOW"]["avg_return_5d"] == pytest.approx(.06)

@pytest.mark.parametrize("reference,price,status", [
    (_reference(), 100, "verified_native_reference"),
    (_reference("KRW"), None, "currency_mismatch"),
    (None, None, "missing_reference"),
    (_reference() | {"observed_at": MEASURED}, None, "future_reference"),
])
def test_standard_writer_never_uses_krw_display_as_native(tmp_path, reference, price, status):
    from concurrent.futures import ThreadPoolExecutor

    db = _recommendation(tmp_path, reference, legacy=False)
    with ThreadPoolExecutor(max_workers=2) as pool:
        retries = list(pool.map(lambda _: record_run_recommendations(tmp_path / "run", db, recorded_at=KNOWN), range(2)))
    assert retries == [0, 0]
    with sqlite3.connect(db) as conn:
        row, = conn.execute("SELECT recommended_price, native_reference_state, display_unit_price_krw, "
                            "price_reference_json FROM action_recommendations").fetchall()
    assert row[:3] == (price, status, 150000)
    assert (row[3] is None) == (price is None)
