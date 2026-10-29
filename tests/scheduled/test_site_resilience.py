import json

import pytest

from tradingagents.scheduled import site
from tradingagents.scheduled.config import SiteSettings


def test_corrupt_archive_does_not_hide_valid_reports(tmp_path):
    runs = tmp_path / "runs"
    for run_id, content in [
        ("valid", json.dumps({"run_id": "valid", "started_at": "2026-09-22", "status": "success", "settings": {}})),
        ("partial-write", "{"),
        ("invalid-shape", "[]"),
        ("mismatched-id", json.dumps({"run_id": "../escape", "started_at": "2026-09-22", "status": "success", "settings": {}})),
    ]:
        path = runs / run_id / "run.json"
        path.parent.mkdir(parents=True)
        path.write_text(content, encoding="utf-8")
    with pytest.warns(RuntimeWarning):
        manifests = site._load_run_manifests(tmp_path)
    assert [item["run_id"] for item in manifests] == ["valid"]


def test_homepage_does_not_parse_private_portfolio_files(tmp_path, monkeypatch):
    run_dir = tmp_path / "run"
    private = run_dir / "portfolio-private"
    private.mkdir(parents=True)
    (private / "status.json").write_text("{", encoding="utf-8")
    manifest = {"run_id": "run", "started_at": "2026-09-22", "status": "success",
                "settings": {}, "_run_dir": str(run_dir), "tickers": []}
    def forbidden(*args, **kwargs):
        raise AssertionError("Homepage must not load private account payloads")
    monkeypatch.setattr(site, "_load_portfolio_summary", forbidden)
    page = site._render_index_page([manifest], SiteSettings())
    assert "strategy.html" in page
    assert 'aria-label="주요 메뉴"' in page


def test_discovery_preserves_both_run_layouts_and_excludes_nested_artifacts(tmp_path):
    for relative, run_id in (("legacy", "legacy"), ("2026/current", "current"),
                             ("2026/current/tickers/embedded", "embedded")):
        path = tmp_path / "runs" / relative / "run.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"run_id": run_id, "started_at": "2026-10-27",
                                    "status": "success", "settings": {}}), encoding="utf-8")
    manifests = site._load_run_manifests(tmp_path)
    assert {item["run_id"] for item in manifests} == {"legacy", "current"}


def test_corrupt_portfolio_status_degrades_to_empty_summary(tmp_path):
    private = tmp_path / "portfolio-private"
    private.mkdir()
    (private / "status.json").write_text("{", encoding="utf-8")
    with pytest.warns(RuntimeWarning, match="portfolio status"):
        assert site._load_portfolio_summary(tmp_path) == {}


@pytest.mark.parametrize("text_decision", [False, True])
def test_repeated_research_is_shared_without_changing_rendered_values(tmp_path, text_decision):
    original = []
    for index in range(3):
        run_id = f"run-{index}"
        payload = {"run_id": run_id, "started_at": f"2026-10-28T10:0{index}:00+09:00",
                   "status": "success", "settings": {"market": "US"},
                   "active_universe": {"expected_watchlist_tickers": ["AAPL"]},
                   "tickers": [{"ticker": "AAPL", "status": "success",
                                "decision": {"reason": "same research " * 1000,
                                             "rating": "HOLD" if index < 2 else "WAIT"},
                                "artifacts": {}}]}
        if text_decision:
            payload["tickers"][0]["decision"] = json.dumps(payload["tickers"][0]["decision"])
        path = tmp_path / "runs" / "2026" / run_id / "run.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        original.append((path, path.read_bytes()))
    manifests = site._load_run_manifests(tmp_path)
    assert manifests[1]["tickers"][0]["decision"] is manifests[2]["tickers"][0]["decision"]
    assert manifests[0]["tickers"][0]["decision"] is not manifests[1]["tickers"][0]["decision"]
    before = json.dumps(manifests)
    for manifest in manifests:
        public = site._public_ticker_summaries(manifest)
        if text_decision:
            public[0]["decision"] = "modified public copy"
        else:
            public[0]["decision"]["reason"] = "modified public copy"
    assert json.dumps(manifests) == before
    assert all(path.read_bytes() == data for path, data in original)

def test_daily_history_survives_overlay_limit_and_rejects_invalid_clocks(tmp_path, monkeypatch):
    from datetime import datetime, timezone
    base={'run_id':'daily','started_at':'2026-10-23T09:00:00+09:00','finished_at':'2026-10-23T10:00:00+09:00',
          'status':'partial_failure','settings':{'market':'us','run_mode':'full'},
          'summary':{'total_tickers':30,'successful_tickers':29,'failed_tickers':1}}
    rows=[base, {**base,'run_id':'overlay','settings':{'run_mode':'overlay_only'}},
          {**base,'run_id':'future','finished_at':'2099-01-01T00:00:00Z'},
          {**base,'run_id':'unknown','finished_at':None},
          {**base,'run_id':'reversed','finished_at':'2026-10-22T00:00:00Z'}]
    writes=[]
    def render(site_dir, manifest, settings, manifests):
        writes.append(manifest['run_id'])
        target=site_dir/'runs'/manifest['run_id']/'index.html'
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text('verified render')
    monkeypatch.setattr(site,'_write_run_pages',render)
    result=site.publish_daily_report_history(tmp_path/'archive',tmp_path/'site',SiteSettings(),manifests=rows,
                                             now=datetime(2026,10,29,tzinfo=timezone.utc))
    assert writes==['daily'] and len(result)==1
    assert result[0]['failed']==1 and result[0]['status']=='partial_failure'
    site.publish_daily_report_history(tmp_path/'archive',tmp_path/'site',SiteSettings(),manifests=rows,
                                       now=datetime(2026,10,29,tzinfo=timezone.utc))
    assert writes==['daily']
