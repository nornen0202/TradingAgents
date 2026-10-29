from datetime import datetime, timedelta, timezone
import json

import pytest

from tradingagents.charting.identity import research_company_matches
from tradingagents.charting.operations import archive_catalog
from tradingagents.charting.snapshot import get_replay_snapshot


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.mark.parametrize(
    "company,expected",
    [("SPG", True), ("058610.KQ", False), ("MSFT", False), (None, True)],
)
def test_known_company_identity_is_bound_to_requested_market(
    tmp_path, company, expected
):
    cutoff = datetime(2026, 10, 29, 16, tzinfo=timezone.utc)
    write(
        tmp_path / "analysis.json",
        {"finished_at": (cutoff - timedelta(minutes=1)).isoformat()},
    )
    write(tmp_path / "final_state.json", {"company_of_interest": company})
    assert (
        research_company_matches(tmp_path, "SPG", cutoff=cutoff, market="US")
        is expected
    )


@pytest.mark.parametrize(
    "clock", [None, "invalid", "2026-10-29T15:59:00", "2099-01-01T00:00:00+00:00"]
)
def test_unavailable_research_identity_cannot_change_a_prior_view(tmp_path, clock):
    cutoff = datetime(2026, 10, 29, 16, tzinfo=timezone.utc)
    write(tmp_path / "analysis.json", {"finished_at": clock})
    write(tmp_path / "final_state.json", {"company_of_interest": "058610.KQ"})
    assert research_company_matches(tmp_path, "SPG", cutoff=cutoff, market="US")


def test_catalog_falls_back_from_wrong_company_and_direct_snapshot_rejects_it(tmp_path):
    cutoff = datetime(2026, 10, 29, 16, tzinfo=timezone.utc)
    paths = []
    for i, company in [(2, "SPG"), (1, "058610.KQ")]:
        identity = f"20261029T1{i}0000_full"
        root = tmp_path / "runs/2026" / identity
        start = cutoff - timedelta(hours=i + 1)
        finish = cutoff - timedelta(hours=i)
        manifest = {
            "run_id": identity,
            "status": "success",
            "started_at": start.isoformat(),
            "finished_at": finish.isoformat(),
            "settings": {"market": "US", "run_mode": "full"},
            "tickers": [{"ticker": "SPG", "status": "success"}],
        }
        write(root / "run.json", manifest)
        write(root / "tickers/SPG/analysis.json", {"finished_at": finish.isoformat()})
        write(root / "tickers/SPG/final_state.json", {"company_of_interest": company})
        paths.append(root)
    catalog = archive_catalog(
        tmp_path, analysis_as_of=cutoff, only_ticker="SPG", include_coverage=False
    )
    assert catalog["SPG"]["public_context"]["run_id"] == paths[0].name
    with pytest.raises(ValueError, match="research company"):
        get_replay_snapshot(
            "SPG", cutoff, ticker_dir=paths[1] / "tickers/SPG", clock=lambda: cutoff
        )
