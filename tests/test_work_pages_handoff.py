from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT = Path(".github/scripts/verify_work_pages_handoff.py")


def _module():
    spec = importlib.util.spec_from_file_location("verify_work_pages_handoff", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_verify_exact_latest_report_and_current_site_lineage(tmp_path: Path, monkeypatch):
    verifier = _module()
    monkeypatch.setattr(verifier, "validate_work_report", lambda _report: None)
    report_sha = "a" * 64
    event_id = "kr:" + "b" * 32
    report = {
        "schema": "tradingagents.work-report/v1",
        "surface": "kr",
        "event_id": event_id,
        "report_sha256": report_sha,
    }
    report_root = tmp_path / "archive" / "work-reports" / "kr"
    events = report_root / "events"
    events.mkdir(parents=True)
    content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    (report_root / "latest.json").write_text(content, encoding="utf-8")
    (events / f"{report_sha}.json").write_text(content, encoding="utf-8")

    site_mobile = tmp_path / "site" / "mobile"
    site_mobile.mkdir(parents=True)
    (site_mobile / "strategy.json").write_text(
        json.dumps(
            {
                "markets": {
                    "kr": {
                        "integrated_report": {
                            "event_id": event_id,
                            "report_id": f"kr:{report_sha[:32]}",
                            "lineage": {"status": "CURRENT_ANALYSIS_LINEAGE"},
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    report_receipt = verifier.verify_latest_report(
        tmp_path / "archive",
        surface="kr",
        event_id=event_id,
        report_sha256=report_sha,
    )
    site_receipt = verifier.verify_built_site(
        tmp_path / "site",
        surface="kr",
        event_id=event_id,
        report_sha256=report_sha,
    )

    assert report_receipt["status"] == "REPORT_VERIFIED"
    assert site_receipt["status"] == "SITE_VERIFIED"
    assert site_receipt["lineage_status"] == "CURRENT_ANALYSIS_LINEAGE"


def test_verify_site_rejects_reference_only_work_report(tmp_path: Path):
    verifier = _module()
    strategy = tmp_path / "site" / "mobile" / "strategy.json"
    strategy.parent.mkdir(parents=True)
    strategy.write_text(
        json.dumps(
            {
                "markets": {
                    "us": {
                        "reference_report": {
                            "lineage": {
                                "status": "PAST_REFERENCE",
                                "reason": "workflow_contract_mismatch",
                            }
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="workflow_contract_mismatch"):
        verifier.verify_built_site(
            tmp_path / "site",
            surface="us",
            event_id="us:" + "b" * 32,
            report_sha256="a" * 64,
        )


def test_work_report_refresh_workflow_enforces_exact_pre_and_post_build_checks():
    workflow = Path(".github/workflows/work-report-pages-refresh.yml").read_text(encoding="utf-8")

    assert '"report"' in workflow
    assert '"site"' in workflow
    assert "verify_work_pages_handoff.py" in workflow
    assert "--require-strategy-payload" in workflow
    assert "Refuse stale Pages snapshot rollback" in workflow
    assert "cancel-in-progress: false" in workflow
