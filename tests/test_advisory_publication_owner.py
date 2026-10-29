from pathlib import Path

import pytest
import yaml


@pytest.mark.parametrize("workflow,job,collection", [
    ("daily-prism-telegram-reports.yml", "build_prism_telegram_pages", "Run PRISM Telegram report collection"),
    ("daily-youtube-reports.yml", "build_youtube_pages", "Run YouTube verification reports"),
])
def test_local_collector_keeps_collection_but_leaves_full_site_to_local_publisher(workflow, job, collection):
    value = yaml.safe_load((Path(__file__).resolve().parents[1] / ".github/workflows" / workflow).read_text(encoding="utf-8"))
    steps = value["jobs"][job]["steps"]
    guarded = []
    for step in steps:
        name = step.get("name", "")
        if name.startswith("Rebuild ") or name in {
            "Stamp rollback-resistant Pages snapshot", "Add Git Bash to PATH for Pages packaging",
            "Verify Pages packaging tools", "Configure GitHub Pages", "Upload GitHub Pages artifact",
        }:
            assert "vars.TRADINGAGENTS_AUTOMATION_BACKEND != 'local'" in step["if"]
            assert "steps.runtime_gate.outputs.should_run == 'true'" in step["if"]
            guarded.append(name)
        if name == collection:
            assert "AUTOMATION_BACKEND" not in step["if"]
    assert len(guarded) >= 5
