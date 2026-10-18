from datetime import datetime
import hashlib
import json
import sqlite3

import pytest

from tradingagents.execution.experiment_cards import (
    list_experiment_cards, main, read_experiment_card, render_experiment_card,
)
from tradingagents.execution.experiments import ExperimentRegistry


def stamp(value):
    return datetime.fromisoformat(value)


@pytest.fixture
def setup_registry(tmp_path):
    path = tmp_path / "registry.sqlite"
    clock = [stamp("2026-01-15T00:00:00+00:00")]
    registry = ExperimentRegistry(path, clock=lambda: clock[0])
    spec = {"id": "trial", "hypothesis": "Less turnover after AI veto <script>alert(1)</script>",
            "universe": ["AAPL"], "capital": 1000, "currency": "USD",
            "costs": {"fee_bps": 10, "slippage_bps": 10}, "benchmark": "SPY",
            "baseline_rules": {"strategy": "fixed", "weight": 0.5},
            "ai_rules": {"strategy": "fixed-with-veto"},
            "training_end": "2026-01-01T00:00:00+00:00", "forward_start": "2026-02-01T00:00:00+00:00",
            "forward_end": "2026-04-01T00:00:00+00:00"}
    registry.register(spec)
    yield path, registry, clock, spec
    registry.close()


def read(path, clock, as_of=None):
    return read_experiment_card(path, "trial", analysis_as_of=as_of or clock[0], clock=lambda: clock[0])


def decide(registry, clock):
    registry.freeze("trial")
    clock[0] = stamp("2026-02-02T14:29:00+00:00")
    registry.record_decision("trial", {
        "session_id": "one", "open_at": "2026-02-02T14:30:00+00:00", "data_as_of": "2026-02-01T20:00:00+00:00",
        "dataset_version": "prices-v1", "baseline_weights": {"AAPL": 0.5}, "ai_weights": {"AAPL": 0.5},
        "model_cost": 0.1, "validation_seconds": 3,
    })


def observe(registry, clock):
    clock[0] = stamp("2026-02-02T21:01:00+00:00")
    registry.record_session("trial", {
        "session_id": "one", "close_at": "2026-02-02T21:00:00+00:00", "available_at": "2026-02-02T21:00:00+00:00",
        "opens": {"AAPL": 100}, "closes": {"AAPL": 110}, "benchmark_open": 200, "benchmark_close": 210,
    })


def test_empty_registry_is_honest_does_not_create_database(tmp_path):
    path = tmp_path / "not-created.sqlite"
    board = list_experiment_cards(path, analysis_as_of="2026-01-15T00:00:00+00:00")
    assert board["status"] == "empty"
    assert board["cards"] == []
    assert not path.exists()
    with pytest.raises(FileNotFoundError):
        read_experiment_card(path, "trial", analysis_as_of="2026-01-15T00:00:00+00:00")


def test_no_observations_means_unknown_performance_and_model(setup_registry):
    path, registry, clock, spec = setup_registry
    card = read(path, clock)
    assert card["id"] == "trial"
    assert card["status"] == "not_frozen"
    assert card["rules"]["baseline"] == spec["baseline_rules"]
    assert card["model"] == {"status": "not_recorded", "declared": {}}
    assert card["data"]["dataset_versions"] == []
    assert card["results"]["arms"] is None
    assert card["results"]["status"] == "no_observations"
    assert "0.0000%" not in render_experiment_card(card)
    registry.freeze("trial")
    assert read(path, clock)["status"] == "awaiting_forward_start"


def test_observed_card_matches_existing_engine_and_is_read_only(setup_registry):
    path, registry, clock, spec = setup_registry
    decide(registry, clock)
    assert read(path, clock)["status"] == "awaiting_observations"
    observe(registry, clock)
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    card = read(path, clock)
    report = registry.report("trial", analysis_as_of=clock[0])
    assert card["results"]["arms"] == report["arms"]
    assert card["results"]["sessions"] == 1
    assert card["data"]["dataset_versions"] == ["prices-v1"]
    assert card["costs"]["model_cost"] == 0.1
    assert card["costs"]["validation_seconds"] == 3
    assert card["status"] == "collecting"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before
    html = render_experiment_card(card)
    assert "<script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "모델비용 추가 차감" in html
    assert "실계좌 주문 없음" in html


def test_future_observations_decisions_and_experiments_do_not_change_old_card(setup_registry):
    path, registry, clock, spec = setup_registry
    decide(registry, clock)
    cutoff = clock[0]
    before_card = read(path, clock)
    before_list = list_experiment_cards(path, analysis_as_of=cutoff, clock=lambda: clock[0])
    observe(registry, clock)
    registry.register({**spec, "id": "future", "training_end": "2026-02-01T00:00:00+00:00",
                       "forward_start": "2026-03-01T00:00:00+00:00"})
    assert read(path, clock, cutoff) == before_card
    assert list_experiment_cards(path, analysis_as_of=cutoff, clock=lambda: clock[0]) == before_list
    with pytest.raises(ValueError, match="not registered"):
        read_experiment_card(path, "future", analysis_as_of=cutoff, clock=lambda: clock[0])


@pytest.mark.parametrize("bad", [None, "", "bad", "2026-01-15", "2026-01-15T00:00:00"])
def test_missing_malformed_or_naive_cutoff_rejected(setup_registry, bad):
    path, registry, clock, spec = setup_registry
    with pytest.raises(ValueError):
        list_experiment_cards(path, analysis_as_of=bad, clock=lambda: clock[0])
    with pytest.raises(ValueError):
        read_experiment_card(path, "trial", analysis_as_of=bad, clock=lambda: clock[0])


def test_future_cutoff_and_before_registration_are_rejected(setup_registry):
    path, registry, clock, spec = setup_registry
    with pytest.raises(ValueError, match="future"):
        read(path, clock, "2026-01-16T00:00:00+00:00")
    with pytest.raises(ValueError, match="not registered"):
        read(path, clock, "2026-01-14T00:00:00+00:00")


@pytest.mark.parametrize("bad", ["", "bad", "2026-01-15", "2026-01-15T00:00:00"])
def test_unknown_registration_dates_excluded_instead_of_inferred(setup_registry, bad):
    path, registry, clock, spec = setup_registry
    # Simulate an imported malformed/legacy DB, bypassing immutable writer only
    # in this fixture. Production cards never drop triggers or write records.
    registry.db.execute("DROP TRIGGER experiment_spec_immutable")
    with registry.db:
        registry.db.execute("UPDATE experiments SET registered_at=?", (bad,))
    assert list_experiment_cards(path, analysis_as_of=clock[0], clock=lambda: clock[0])["cards"] == []
    with pytest.raises(ValueError):
        read(path, clock)


def test_corrupted_payload_fails_closed(setup_registry):
    path, registry, clock, spec = setup_registry
    decide(registry, clock)
    registry.db.execute("DROP TRIGGER decision_no_update")
    with registry.db:
        registry.db.execute("UPDATE experiment_decisions SET payload='{}'")
    with pytest.raises(ValueError, match="integrity"):
        read(path, clock)


def test_cli_exports_saved_html_and_json_without_mutating_registry(setup_registry, tmp_path):
    path, registry, clock, spec = setup_registry
    output = tmp_path / "card.html"
    assert main(["--registry", str(path), "--as-of", clock[0].isoformat(), "--id", "trial",
                 "--format", "html", "--output", str(output)]) == 0
    assert "전략 실험 카드" in output.read_text("utf-8")
    output = tmp_path / "cards.json"
    assert main(["--registry", str(path), "--as-of", clock[0].isoformat(), "--output", str(output)]) == 0
    assert json.loads(output.read_text("utf-8"))["cards"][0]["id"] == "trial"
    assert registry.db.execute("SELECT COUNT(*) FROM experiments").fetchone()[0] == 1
