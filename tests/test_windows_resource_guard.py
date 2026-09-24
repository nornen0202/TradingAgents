import importlib.util
import sys
from pathlib import Path

import pytest


@pytest.fixture
def guard(monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "windows_resource_guard", Path('.github/scripts/windows_resource_guard.py')
    )
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('resource', ['commit_free', 'physical_free', 'c_drive_free'])
def test_each_resource_can_block_job(guard, resource):
    values = dict(commit_free=10, physical_free=10, c_drive_free=10,
                  commit_total=10, commit_limit=20, process_count=5)
    thresholds = dict(min_commit_free=10, min_physical_free=10, min_c_drive_free=10)
    assert guard.has_headroom(guard.ResourceSnapshot(**values), **thresholds)
    values[resource] = 9
    assert not guard.has_headroom(guard.ResourceSnapshot(**values), **thresholds)


def test_low_resources_exit_without_waiting_forever(guard, monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['guard', '--wait-seconds', '0'])
    monkeypatch.setattr(guard, 'read_snapshot', lambda: guard.ResourceSnapshot(0, 1, 1, 0, 0, 1))
    assert guard.main() == 1
    assert '::error::Insufficient Windows' in capsys.readouterr().out


def test_recovered_resources_allow_job(guard, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['guard'])
    snapshots = iter([guard.ResourceSnapshot(0, 1, 1, 0, 0, 1),
                      guard.ResourceSnapshot(20 * guard.GIB, 0, 20 * guard.GIB,
                                             4 * guard.GIB, 20 * guard.GIB, 1)])
    monkeypatch.setattr(guard, 'read_snapshot', lambda: next(snapshots))
    monkeypatch.setattr(guard.time, 'sleep', lambda _: None)
    assert guard.main() == 0


def test_default_disk_reserve_allows_actual_runner_headroom(guard, monkeypatch):
    """The Windows runners' normal 6-8 GiB C: free must not time out."""
    monkeypatch.setattr(sys, 'argv', ['guard', '--wait-seconds', '0'])
    monkeypatch.setattr(
        guard,
        'read_snapshot',
        lambda: guard.ResourceSnapshot(
            40 * guard.GIB, 16 * guard.GIB, 56 * guard.GIB,
            4 * guard.GIB, 6 * guard.GIB, 350,
        ),
    )
    assert guard.main() == 0


def test_default_disk_reserve_blocks_unsafe_headroom(guard, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['guard', '--wait-seconds', '0'])
    monkeypatch.setattr(
        guard,
        'read_snapshot',
        lambda: guard.ResourceSnapshot(
            40 * guard.GIB, 16 * guard.GIB, 56 * guard.GIB,
            4 * guard.GIB, 3 * guard.GIB, 350,
        ),
    )
    assert guard.main() == 1
