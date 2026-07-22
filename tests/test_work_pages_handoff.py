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
                            "lineage": {
                                "status": "CURRENT_ANALYSIS_LINEAGE",
                                "current_action_cards_enriched": True,
                            },
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    public_report = tmp_path / "site" / "work" / "v1" / "kr" / "report"
    (public_report / "events").mkdir(parents=True)
    (public_report / "latest.json").write_text(content, encoding="utf-8")
    (public_report / "events" / f"{report_sha}.json").write_text(content, encoding="utf-8")

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
    assert site_receipt["publication_mode"] == "CURRENT_ACTION_CARDS"
    assert site_receipt["current_action_cards_enriched"] is True


def test_verify_site_accepts_exact_analysis_only_reference(tmp_path: Path, monkeypatch):
    verifier = _module()
    monkeypatch.setattr(verifier, "validate_work_report", lambda _report: None)
    report_sha = "a" * 64
    event_id = "us:" + "b" * 32
    strategy = tmp_path / "site" / "mobile" / "strategy.json"
    strategy.parent.mkdir(parents=True)
    strategy.write_text(
        json.dumps(
            {
                "markets": {
                    "us": {
                        "reference_report": {
                            "event_id": event_id,
                            "report_id": f"us:{report_sha[:32]}",
                            "analysis_only": True,
                            "structured_report": {"strategies": [{"ticker": "MU"}]},
                            "lineage": {
                                "status": "PAST_REFERENCE",
                                "reason": "workflow_contract_mismatch",
                                "current_action_cards_enriched": False,
                            }
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    report = {
        "schema": "tradingagents.work-report/v1",
        "surface": "us",
        "event_id": event_id,
        "report_sha256": report_sha,
    }
    content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    public_report = tmp_path / "site" / "work" / "v1" / "us" / "report"
    (public_report / "events").mkdir(parents=True)
    (public_report / "latest.json").write_text(content, encoding="utf-8")
    (public_report / "events" / f"{report_sha}.json").write_text(content, encoding="utf-8")

    receipt = verifier.verify_built_site(
        tmp_path / "site",
        surface="us",
        event_id=event_id,
        report_sha256=report_sha,
    )

    assert receipt["publication_mode"] == "ANALYSIS_REFERENCE"
    assert receipt["lineage_status"] == "PAST_REFERENCE"
    assert receipt["current_action_cards_enriched"] is False


def test_verify_site_rejects_reference_that_retains_execution_gate(tmp_path: Path):
    verifier = _module()
    strategy = tmp_path / "site" / "mobile" / "strategy.json"
    strategy.parent.mkdir(parents=True)
    strategy.write_text(
        json.dumps(
            {
                "markets": {
                    "us": {
                        "reference_report": {
                            "event_id": "us:" + "b" * 32,
                            "report_id": "us:" + "a" * 32,
                            "analysis_only": True,
                            "structured_report": {
                                "strategies": [{"ticker": "MU", "execution": {"action": "BUY"}}]
                            },
                            "lineage": {
                                "status": "PAST_REFERENCE",
                                "current_action_cards_enriched": False,
                            },
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="retained a stale per-ticker execution gate"):
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
