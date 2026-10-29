"""Wrong-company success is quarantined and repaired within the original budget."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import timedelta
from types import SimpleNamespace
import hashlib
import json

import pytest

from tests.test_operator_research_admission import operator  # noqa: F401 -- imported fixture
from tests.test_research_recovery import write, recovery  # noqa: F401 -- dependency fixture
from tradingagents.agents.utils.instrument_resolver import (
    resolve_instrument,
    InstrumentResolutionError,
)
from tradingagents.dataflows.config import get_config, run_config, run_config_context
from tradingagents.dataflows.interface import _prioritize_market_specific_vendors
from tradingagents.graph.propagation import Propagator
from tradingagents.scheduled.operator_admission import (
    CERTIFICATE,
    INTEGRITY_CERTIFICATE,
    INTEGRITY_SCHEMA,
    certify_operator_research,
    certify_integrity_recovery,
    verified_operator_research,
    verified_operator_lineage_source,
)
from tradingagents.scheduled.research_recovery import (
    load_recovery_source,
    copy_recovered_research,
    verified_completed_recovery,
)
from tradingagents.scheduled.site import _operator_publication_eligible
from tradingagents.notifications.local import _local_market_producer
from tradingagents import local_automation as local
from tradingagents.scheduled import runner


@pytest.mark.parametrize("company", [None, "058610.KQ", "MSFT"])
def test_worker_rejects_missing_or_wrong_company_before_report_and_success(
    tmp_path, monkeypatch, company
):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        f'[run]\ntickers=["SPG"]\nmarket="US"\n[storage]\narchive_dir="{(tmp_path / "archive").as_posix()}"\n',
        encoding="utf-8",
    )
    config = runner.load_scheduled_config(config_path)
    graph = SimpleNamespace(
        propagate=lambda *a, **k: ({"company_of_interest": company}, "HOLD"),
        close=lambda: None,
    )
    monkeypatch.setattr(runner, "TradingAgentsGraph", lambda *a, **k: graph)
    monkeypatch.setattr(
        runner,
        "polish_ticker_report",
        lambda *a, **k: pytest.fail("wrong company reached publication"),
    )
    result = runner._run_single_ticker(
        config=config,
        ticker="SPG",
        run_dir=tmp_path / "run",
        engine_results_dir=tmp_path / "engine",
        trade_date_override="2026-10-29",
    )
    assert result["status"] == "failed"
    assert "company differs" in result["error"]


def test_explicit_and_concurrent_market_scopes_disambiguate_spg_without_leaking():
    original = get_config()
    assert resolve_instrument("SPG", market="US").primary_symbol == "SPG"
    assert resolve_instrument("SPG", market="US").display_name == "Simon Property Group"
    assert resolve_instrument("SPG", market="KR").primary_symbol == "058610.KQ"
    assert resolve_instrument("058610.KQ").primary_symbol == "058610.KQ"

    def check(market):
        with run_config({"instrument_market": market}):
            profile = resolve_instrument("SPG")
            state = Propagator().create_initial_state("SPG", "2026-10-29")
            vendors = _prioritize_market_specific_vendors(
                "get_disclosures", ["sec_edgar", "opendart"], ("SPG",), {}
            )
            assert state["company_of_interest"] == profile.primary_symbol
            return profile.primary_symbol, vendors

    with ThreadPoolExecutor(max_workers=2) as pool:
        us, kr = list(pool.map(check, ["US", "KR"]))
    assert us == ("SPG", ["sec_edgar"])
    assert kr == ("058610.KQ", ["opendart"])
    assert get_config() == original
    context = run_config_context({"instrument_market": "US"})
    assert context.run(resolve_instrument, "SPG").country == "US"
    assert get_config() == original


@pytest.mark.parametrize(
    "symbol,market",
    [("058610.KQ", "US"), ("에스피지", "US"), ("AAPL", "KR"), ("SPG", "EU")],
)
def test_explicit_foreign_or_invalid_market_fails_closed(symbol, market):
    with pytest.raises(InstrumentResolutionError):
        resolve_instrument(symbol, market=market)


@pytest.fixture
def corrected(operator):  # noqa: F811 -- imported fixture
    f = operator
    parent = f["manifest"]
    archive = f["archive"]
    now = f["now"]
    wrong = deepcopy(parent["tickers"][0])
    wrong["ticker"] = "XOM"
    wrong["artifacts"] = {
        key: relative.replace("AAPL", "XOM")
        for key, relative in wrong["artifacts"].items()
    }
    for key, relative in wrong["artifacts"].items():
        source = f["root"] / parent["tickers"][0]["artifacts"][key]
        target = f["root"] / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if key == "report_markdown":
            target.write_text("Wrong company research", encoding="utf-8")
        else:
            value = json.loads(source.read_text())
            if key == "analysis_json":
                value["ticker"] = "XOM"
            elif key == "final_state_json":
                value["company_of_interest"] = "058610.KQ"
            elif key == "execution_contract_json":
                value["ticker"] = "XOM"
            write(target, value)
    parent["tickers"].append(wrong)
    parent["summary"].update(total_tickers=2, successful_tickers=2)
    parent["active_universe"].update(
        active_count=2,
        selected_tickers=["AAPL", "XOM"],
        expected_watchlist_tickers=["AAPL", "XOM"],
    )
    write(f["root"] / "run.json", parent)
    certificate = certify_operator_research(
        archive_dir=archive,
        state_dir=f["state"],
        run_id=parent["run_id"],
        target_key=f["key"],
        now=now,
    )
    assert certificate["baseline_eligible"] is False
    plan = load_recovery_source(
        archive_dir=archive,
        source_run_id=parent["run_id"],
        settings=parent["settings"],
        now=now,
        holding_tickers=[],
        account_status="disabled",
    )
    assert plan["retry_tickers"] == ["XOM"] and [
        r["ticker"] for r in plan["successful_rows"]
    ] == ["AAPL"]
    identity = (now + timedelta(seconds=2)).strftime(
        "%Y%m%dT%H%M%S"
    ) + "_manual-us-integrity-recovery"
    directory = archive / "runs" / identity[:4] / identity
    reused, receipt = copy_recovered_research(plan, run_dir=directory)
    assert [r["ticker"] for r in reused] == ["AAPL"]
    child = deepcopy(parent)
    child.update(
        run_id=identity,
        label="manual-us-integrity-recovery",
        source_revision="c" * 40,
        started_at=(now + timedelta(seconds=2)).isoformat(),
        finished_at=(now + timedelta(seconds=3)).isoformat(),
        research_recovery=receipt,
        active_universe=plan["active_universe"],
        tickers=[*reused, deepcopy(wrong)],
    )
    row = child["tickers"][-1]
    row.update(started_at=child["started_at"], finished_at=child["finished_at"])
    for key, relative in row["artifacts"].items():
        original = f["root"] / relative
        target = directory / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if key == "report_markdown":
            target.write_text("Correct US company research", encoding="utf-8")
        else:
            data = json.loads(original.read_text())
            if key == "analysis_json":
                for k in ("started_at", "finished_at", "analysis_date", "trade_date"):
                    data[k] = row[k]
            elif key == "final_state_json":
                data["company_of_interest"] = "XOM"
            write(target, data)
    write(directory / "run.json", child)
    write(
        directory / "attempt.json",
        {
            "run_id": identity,
            "status": "SUCCESS",
            "market": "US",
            "run_mode": "full",
            "started_at": child["started_at"],
            "finished_at": (now + timedelta(seconds=4)).isoformat(),
        },
    )
    budget = {
        "schema": INTEGRITY_SCHEMA,
        "status": "COMPLETED",
        "attempts": 1,
        "exit_code": 0,
        "orders_sent": 0,
        "run_id": identity,
        "source_run_id": parent["run_id"],
        "source_revision": child["source_revision"],
        "source_certificate_sha256": hashlib.sha256(
            (f["root"] / CERTIFICATE).read_bytes()
        ).hexdigest(),
        "original_target_key": f["key"],
        "original_attempts": 2,
        "original_manual_attempts": 1,
        "cumulative_limit": 4,
        "started_at": (now + timedelta(seconds=1)).isoformat(),
        "finished_at": (now + timedelta(seconds=5)).isoformat(),
    }
    write(f["state"] / "research-integrity-recovery" / f"{f['key']}.json", budget)
    f.update(
        parent=parent,
        child=child,
        child_root=directory,
        budget=budget,
        checked=now + timedelta(seconds=6),
    )
    return f


def test_successful_wrong_company_is_never_published_or_admitted_and_only_corrected_child_qualifies(
    corrected,
):
    f = corrected
    archive = f["archive"]
    now = f["checked"]
    assert verified_operator_lineage_source(archive, f["parent"], now=now)
    assert not verified_operator_research(archive, f["parent"], now=now)
    assert not _operator_publication_eligible(archive, f["parent"])
    assert not verified_completed_recovery(archive, f["child"], now=now)
    before = {p: p.read_bytes() for p in f["root"].rglob("*") if p.is_file()}
    fingerprint = local.archive_fingerprint(archive)
    receipt = certify_integrity_recovery(
        archive_dir=archive,
        state_dir=f["state"],
        run_id=f["child"]["run_id"],
        target_key=f["key"],
        now=now,
    )
    assert receipt["evidence"]["cumulative_attempts"] == 4
    assert local.archive_fingerprint(archive) != fingerprint
    assert verified_completed_recovery(archive, f["child"], now=now)
    assert _local_market_producer(f["child"], archive, now=now)
    assert all(p.read_bytes() == data for p, data in before.items())


@pytest.mark.parametrize(
    "case",
    [
        "budget",
        "bool_budget",
        "active",
        "future",
        "naive",
        "missing",
        "source_hash",
        "source_revision",
        "wrong_target",
        "wrong_run",
        "unrepaired",
    ],
)
def test_invalid_identity_correction_cannot_be_certified(corrected, case):
    f = corrected
    r = f["budget"]
    if case == "budget":
        r["attempts"] = 2
    elif case == "bool_budget":
        r["attempts"] = True
    elif case == "active":
        r["status"] = "STARTED"
    elif case == "future":
        r["finished_at"] = (f["checked"] + timedelta(days=1)).isoformat()
    elif case == "naive":
        r["started_at"] = "2026-10-29T00:00:00"
    elif case == "missing":
        r.pop("finished_at")
    elif case == "source_hash":
        r["source_certificate_sha256"] = "0" * 64
    elif case == "source_revision":
        r["source_revision"] = "d" * 40
    elif case == "wrong_target":
        r["original_target_key"] = "e" * 64
    elif case == "wrong_run":
        r["run_id"] = "other"
    elif case == "unrepaired":
        p = f["child_root"] / f["child"]["tickers"][0]["artifacts"]["final_state_json"]
        state = json.loads(p.read_text())
        state["company_of_interest"] = "058610.KQ"
        write(p, state)
    write(f["state"] / "research-integrity-recovery" / f"{f['key']}.json", r)
    with pytest.raises((ValueError, KeyError, OSError, TypeError)):
        certify_integrity_recovery(
            archive_dir=f["archive"],
            state_dir=f["state"],
            run_id=f["child"]["run_id"],
            target_key=f["key"],
            now=f["checked"],
        )
    assert not (f["child_root"] / INTEGRITY_CERTIFICATE).exists()
