from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _module():
    path = Path(".github/scripts/mobile_layout_regression.py")
    spec = importlib.util.spec_from_file_location("mobile_layout_regression", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mobile_layout_probe_retries_with_a_clean_profile(tmp_path: Path, monkeypatch) -> None:
    module = _module()
    profiles: list[Path] = []

    def fake_probe(_page_url: str, profile: Path):
        profiles.append(profile)
        if len(profiles) == 1:
            raise RuntimeError("Chrome DevToolsActivePort was not created")
        return [{"requestedWidth": 390}]

    monkeypatch.setattr(module, "_run_probe_once", fake_probe)
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)

    result = module._run_probe("http://127.0.0.1/", tmp_path / "chrome-profile")

    assert result == [{"requestedWidth": 390}]
    assert [profile.name for profile in profiles] == [
        "chrome-profile-attempt-1",
        "chrome-profile-attempt-2",
    ]


def test_mobile_layout_probe_preserves_both_startup_failures(tmp_path: Path, monkeypatch) -> None:
    module = _module()
    monkeypatch.setattr(
        module,
        "_run_probe_once",
        lambda _page_url, profile: (_ for _ in ()).throw(RuntimeError(f"failed {profile.name}")),
    )
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)

    with pytest.raises(RuntimeError, match="attempt 1: failed chrome-profile-attempt-1.*attempt 2"):
        module._run_probe("http://127.0.0.1/", tmp_path / "chrome-profile")
