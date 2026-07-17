from pathlib import Path

import yaml


def test_ci_does_not_run_twice_for_pull_request_branches() -> None:
    workflow = yaml.safe_load(Path(".github/workflows/ci.yml").read_text(encoding="utf-8"))
    triggers = workflow[True]

    assert "pull_request" in triggers
    assert triggers["push"]["branches"] == ["main"]
