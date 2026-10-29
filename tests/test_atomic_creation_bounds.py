import errno
from unittest.mock import Mock

import pytest

from tradingagents import atomic_io


@pytest.mark.parametrize("error", [PermissionError(errno.EACCES, "denied"),
                                  OSError(errno.ENOSPC, "full disk")])
def test_creation_failure_is_immediate_and_preserves_destination(tmp_path, monkeypatch, error):
    target = tmp_path / "receipt.json"
    atomic_io.atomic_write_json(target, {"old": True})
    before = target.read_bytes()
    opener = Mock(side_effect=error)
    monkeypatch.setattr(atomic_io.os, "open", opener)
    with pytest.raises(type(error)) as caught:
        atomic_io.atomic_write_json(target, {"new": True})
    assert caught.value is error
    opener.assert_called_once()
    assert target.read_bytes() == before
    assert not list(tmp_path.glob(".*.tmp"))


def test_creation_collisions_are_bounded(tmp_path, monkeypatch):
    opener = Mock(side_effect=FileExistsError("collision"))
    monkeypatch.setattr(atomic_io.os, "open", opener)
    with pytest.raises(FileExistsError, match="unique"):
        atomic_io.atomic_write_json(tmp_path / "receipt.json", {})
    assert opener.call_count == 16


def test_creation_collision_retries_with_unique_exclusive_name(tmp_path, monkeypatch):
    original = atomic_io.os.open
    calls = []

    def collision_once(path, flags, mode):
        calls.append(path)
        assert flags & atomic_io.os.O_EXCL
        assert mode == 0o600
        if len(calls) == 1:
            raise FileExistsError("collision")
        return original(path, flags, mode)

    monkeypatch.setattr(atomic_io.os, "open", collision_once)
    atomic_io.atomic_write_json(tmp_path / "receipt.json", {})
    assert len(calls) == len(set(calls)) == 2
