from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import Mock

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


def test_mobile_layout_probe_checks_direction_and_separated_actions() -> None:
    source = Path(".github/scripts/mobile_layout_regression.py").read_text(encoding="utf-8")

    for label in (
        "분석 시점 전략 방향",
        "현재 실행 상태",
        "전략 발동 조건",
        "발동 조건 충족 시 행동",
        "위험 대응·무효화 조건",
        "위험 대응 조건 충족 시 행동",
    ):
        assert label in source
    assert "확인할 진입·축소 조건" not in source


class _Clock:
    def __init__(self):
        self.elapsed = 0.0

    def monotonic(self):
        return self.elapsed

    def sleep(self, seconds):
        self.elapsed += seconds


def test_devtools_endpoint_recovers_from_windows_lock_and_partial_write(tmp_path, monkeypatch):
    module = _module()
    clock = _Clock()
    reads = Mock(side_effect=[
        FileNotFoundError(), PermissionError(), "9222\n", "92x\n/devtools/browser/id",
        "9222\n/devtools/browser/", "9222\n/devtools/browser/ready-id\n",
    ])
    monkeypatch.setattr(module, "time", clock)
    monkeypatch.setattr(Path, "read_text", reads)

    assert module._devtools_endpoint(tmp_path, timeout_seconds=1) == (9222, "/devtools/browser/ready-id")
    assert reads.call_count == 6
    assert clock.elapsed == pytest.approx(0.5)


@pytest.mark.parametrize("response,reason", [
    (PermissionError(), "PermissionError"),
    (FileNotFoundError(), "FileNotFoundError"),
    ("9222\n", "incomplete marker"),
    ("99999\n/devtools/browser/id", "incomplete marker"),
])
def test_devtools_endpoint_persistent_startup_problem_expires(tmp_path, monkeypatch, response, reason):
    module = _module()
    clock = _Clock()
    reads = Mock(side_effect=response) if isinstance(response, Exception) else Mock(return_value=response)
    monkeypatch.setattr(module, "time", clock)
    monkeypatch.setattr(Path, "read_text", reads)

    with pytest.raises(RuntimeError, match=rf"within 0.25s.*{reason}"):
        module._devtools_endpoint(tmp_path, timeout_seconds=0.25)
    assert clock.elapsed == pytest.approx(0.25)
    assert reads.call_count == 3


def test_devtools_endpoint_does_not_hide_unrelated_io_failure(tmp_path, monkeypatch):
    module = _module()
    monkeypatch.setattr(Path, "read_text", Mock(side_effect=OSError("disk failure")))
    with pytest.raises(OSError, match="disk failure"):
        module._devtools_endpoint(tmp_path)
