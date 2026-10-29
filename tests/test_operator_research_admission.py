"""Production admission requires terminal fresh research and preserved budgets."""

from copy import deepcopy
from datetime import timedelta
import hashlib
import json
from types import SimpleNamespace

import pytest

from tests.test_research_recovery import recovery, write  # noqa: F401 -- imported pytest fixture
from tradingagents import local_automation as local
from tradingagents.notifications.local import _local_market_producer
from tradingagents.scheduled import runner
from tradingagents.scheduled.operator_admission import (
    CERTIFICATE,
    certify_operator_research,
    verified_operator_research,
)


@pytest.fixture
def operator(recovery, tmp_path):  # noqa: F811 -- imported pytest fixture
    f = recovery
    m, root, now = f["source"], f["root"], f["now"]
    m.update(
        status="success", label="manual-us-identity-recovery", source_revision="a" * 40
    )
    m["tickers"] = m["tickers"][:1]
    m["summary"].update(total_tickers=1, successful_tickers=1, failed_tickers=0)
    m["active_universe"].update(active_count=1, selected_tickers=["AAPL"])
    m["active_universe"]["coverage"].update(complete=True, analysis_complete=True)
    m["settings"].update(
        provider="codex",
        **{
            f"{role}_model": "gpt-6.1-sol"
            for role in ("quick", "deep", "output", "writer", "judge")
        },
    )
    write(root / "run.json", m)
    write(
        root / "attempt.json",
        {
            "run_id": m["run_id"],
            "status": "SUCCESS",
            "market": "US",
            "run_mode": "full",
            "started_at": m["started_at"],
            "finished_at": (now - timedelta(minutes=59)).isoformat(),
        },
    )
    archive = f["config"].storage.archive_dir
    proofs = {}
    for i in (5, 4):
        start = now - timedelta(hours=i, minutes=10)
        source = start.strftime("%Y%m%dT%H%M%S") + "_local-scheduler-us-full"
        path = archive / "runs" / source[:4] / source / "attempt.json"
        write(
            path,
            {
                "run_id": source,
                "status": "FAILED",
                "market": "US",
                "run_mode": "full",
                "error_type": "KeyError",
                "started_at": start.isoformat(),
                "finished_at": (now - timedelta(hours=i)).isoformat(),
            },
        )
        proofs[source] = hashlib.sha256(path.read_bytes()).hexdigest()
    key, state = "b" * 64, tmp_path / "state"
    original = {
        "target": "daily-codex-us",
        "attempts": 2,
        "exit_code": 1,
        "started_at": (now - timedelta(hours=5, minutes=20)).isoformat(),
        "finished_at": (now - timedelta(hours=4)).isoformat(),
    }
    repair = {
        "schema": "tradingagents.manual-research-repair/v1",
        "mode": "fresh_research_after_preworker_identity_failure",
        "status": "COMPLETED",
        "attempts": 1,
        "exit_code": 0,
        "source_revision": "a" * 40,
        "original_target_key": key,
        "original_attempts": 2,
        "cumulative_limit": 4,
        "orders_sent": 0,
        "reused_ticker_count": 0,
        "source_attempt_sha256": proofs,
        "source_run_id": source,
        "started_at": (now - timedelta(hours=3)).isoformat(),
        "finished_at": (now - timedelta(minutes=58)).isoformat(),
    }
    write(state / "attempts" / f"{key}.json", original)
    write(state / "finalization-recovery" / f"{key}.json", repair)
    return dict(
        f=f,
        manifest=m,
        root=root,
        now=now,
        archive=archive,
        state=state,
        key=key,
        original=original,
        repair=repair,
    )


def certify(f):
    return certify_operator_research(
        archive_dir=f["archive"],
        state_dir=f["state"],
        run_id=f["manifest"]["run_id"],
        target_key=f["key"],
        now=f["now"],
    )


def test_certificate_admits_three_consumers_and_changes_publication_fingerprint_without_rewriting(
    operator,
):
    f = operator
    before = {p: p.read_bytes() for p in f["archive"].rglob("*") if p.is_file()}
    fingerprint = local.archive_fingerprint(f["archive"])
    assert not verified_operator_research(f["archive"], f["manifest"], now=f["now"])
    assert not _local_market_producer(f["manifest"], f["archive"], now=f["now"])
    receipt = certify(f)
    assert receipt["evidence"]["cumulative_attempts"] == 3
    assert verified_operator_research(f["archive"], f["manifest"], now=f["now"])
    assert _local_market_producer(f["manifest"], f["archive"], now=f["now"])
    assert runner._manifest_is_complete_overlay_baseline(
        f["manifest"],
        market="US",
        requested_tickers=None,
        required_holding_tickers=None,
        archive_dir=f["archive"],
        now=f["now"],
    )
    target = SimpleNamespace(
        workflow_file="daily-codex-analysis.yml",
        inputs={"profile": "us"},
        window_start_kst=f["now"] - timedelta(hours=3),
    )
    assert local.completed_target(
        local._scheduler_manifest_view(f["manifest"]),
        target,
        archive=f["archive"],
        now=f["now"],
    )
    assert local.archive_fingerprint(f["archive"]) != fingerprint
    assert all(p.read_bytes() == value for p, value in before.items())
    assert certify(f) == receipt
    assert (
        runner._resolve_latest_full_overlay_baseline_manifest(
            f["archive"],
            market="US",
            now=f["now"] + timedelta(days=5),
            write_discovery_index=False,
        )
        is None
    )


@pytest.mark.parametrize(
    "case",
    [
        "budget",
        "bool_budget",
        "wrong_target",
        "active_repair",
        "future_repair",
        "naive_repair",
        "missing_time",
        "source_hash",
        "source_missing",
        "source_workers",
        "source_manifest",
        "source_clock",
        "wrong_latest",
        "source_revision",
        "smoke",
        "wrong_market",
        "fallback",
        "model",
        "coverage",
        "selection",
        "reuse",
        "future_date",
        "missing_date",
        "empty_date",
        "malformed_date",
        "future_trade_date",
        "wrong_artifact",
        "future_row",
        "active_attempt",
        "noncanonical",
    ],
)
def test_invalid_operator_run_is_rejected_before_any_certificate(operator, case):
    f = operator
    m, r, o = f["manifest"], f["repair"], f["original"]
    source = f["archive"] / "runs" / r["source_run_id"][:4] / r["source_run_id"]
    if case == "budget":
        r["attempts"] = 3
    elif case == "bool_budget":
        r["attempts"] = True
    elif case == "wrong_target":
        o["target"] = "daily-codex-kr"
    elif case == "active_repair":
        r["status"] = "STARTED"
    elif case == "future_repair":
        r["finished_at"] = (f["now"] + timedelta(days=1)).isoformat()
    elif case == "naive_repair":
        r["started_at"] = "2026-10-29T00:00:00"
    elif case == "missing_time":
        r.pop("finished_at")
    elif case == "source_hash":
        r["source_attempt_sha256"][r["source_run_id"]] = "0" * 64
    elif case == "source_missing":
        (source / "attempt.json").unlink()
    elif case == "source_workers":
        write(source / "worker-summaries/AAPL.json", {"status": "success"})
    elif case == "source_manifest":
        write(source / "run.json", {})
    elif case == "source_clock":
        d = json.loads((source / "attempt.json").read_text())
        d["finished_at"] = (f["now"] + timedelta(days=1)).isoformat()
        write(source / "attempt.json", d)
        r["source_attempt_sha256"][r["source_run_id"]] = hashlib.sha256(
            (source / "attempt.json").read_bytes()
        ).hexdigest()
    elif case == "wrong_latest":
        r["source_run_id"] = next(iter(r["source_attempt_sha256"]))
    elif case == "source_revision":
        m["source_revision"] = "c" * 40
    elif case == "smoke":
        m["label"] = "manual-us-smoke"
    elif case == "wrong_market":
        m["settings"]["market"] = "KR"
    elif case == "fallback":
        m["settings"]["codex_fallback_on_app_server_error"] = True
    elif case == "model":
        m["settings"]["writer_model"] = "other"
    elif case == "coverage":
        m["active_universe"]["coverage"]["complete"] = False
    elif case == "selection":
        m["active_universe"]["selected_tickers"] = []
    elif case == "reuse":
        m["tickers"][0]["research_reuse"] = {}
    elif case in {
        "future_date",
        "missing_date",
        "empty_date",
        "malformed_date",
        "future_trade_date",
    }:
        key = "trade_date" if case == "future_trade_date" else "analysis_date"
        m["tickers"][0][key] = {
            "future_date": "2099-01-01",
            "missing_date": None,
            "empty_date": "",
            "malformed_date": "2026-99-99",
            "future_trade_date": "2099-01-01",
        }[case]
        path = f["root"] / m["tickers"][0]["artifacts"]["analysis_json"]
        analysis = json.loads(path.read_text())
        analysis[key] = m["tickers"][0][key]
        write(path, analysis)
    elif case == "wrong_artifact":
        (f["root"] / m["tickers"][0]["artifacts"]["analysis_json"]).write_text("{}")
    elif case == "future_row":
        m["tickers"][0]["finished_at"] = (f["now"] + timedelta(days=1)).isoformat()
    elif case == "active_attempt":
        write(f["root"] / "attempt.json", {"status": "RUNNING"})
    elif case == "noncanonical":
        f["manifest"] = deepcopy(m)
        f["manifest"]["label"] = "noncanonical"
    write(f["state"] / "attempts" / f"{f['key']}.json", o)
    write(f["state"] / "finalization-recovery" / f"{f['key']}.json", r)
    write(f["root"] / "run.json", m)
    if case == "noncanonical":
        assert not verified_operator_research(f["archive"], f["manifest"], now=f["now"])
        return
    with pytest.raises((ValueError, KeyError, OSError, TypeError)):
        certify(f)
    assert not (f["root"] / CERTIFICATE).exists()


@pytest.mark.parametrize(
    "case",
    [
        "artifact",
        "manifest",
        "attempt",
        "source",
        "future_certificate",
        "evidence",
        "missing_certificate",
    ],
)
def test_mutation_after_certification_revokes_admission(operator, case):
    f = operator
    certify(f)
    path = f["root"] / CERTIFICATE
    if case == "artifact":
        (
            f["root"] / f["manifest"]["tickers"][0]["artifacts"]["report_markdown"]
        ).write_text("changed")
    elif case == "manifest":
        f["manifest"]["summary"]["successful_tickers"] = 0
        write(f["root"] / "run.json", f["manifest"])
    elif case == "attempt":
        write(f["root"] / "attempt.json", {"status": "RUNNING"})
    elif case == "source":
        sid = f["repair"]["source_run_id"]
        write(f["archive"] / "runs" / sid[:4] / sid / "attempt.json", {})
    elif case == "missing_certificate":
        path.unlink()
    else:
        d = json.loads(path.read_text())
        if case == "future_certificate":
            d["certified_at"] = (f["now"] + timedelta(days=1)).isoformat()
        else:
            d["evidence"]["cumulative_attempts"] = 1
        write(path, d)
    assert not verified_operator_research(f["archive"], f["manifest"], now=f["now"])
    assert not _local_market_producer(f["manifest"], f["archive"], now=f["now"])


def test_certificate_does_not_archive_arbitrary_scheduler_metadata(operator):
    f = operator
    for directory, value in (
        ("attempts", f["original"]),
        ("finalization-recovery", f["repair"]),
    ):
        value["private_metadata"] = "must-stay-local"
        write(f["state"] / directory / f"{f['key']}.json", value)
    assert "must-stay-local" not in json.dumps(certify(f))
