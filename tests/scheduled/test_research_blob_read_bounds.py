import io
from types import SimpleNamespace

import pytest

from tradingagents.scheduled.research_artifact_refs import _read, _MAX_BYTES


@pytest.mark.parametrize("size", [32, 4096])
def test_small_evidence_never_allocates_the_global_limit(size):
    sizes = []
    class Stream(io.BytesIO):
        def read(self, count):
            sizes.append(count)
            return super().read(count)
    stat = SimpleNamespace(st_size=size, st_mtime_ns=1, st_ino=1)
    path = SimpleNamespace(stat=lambda: stat, open=lambda _: Stream(b"x" * size))
    assert _read(path) == b"x" * size
    assert sizes == [size + 1]


@pytest.mark.parametrize("size", [0, _MAX_BYTES + 1])
def test_invalid_size_rejected_before_open(size):
    path = SimpleNamespace(stat=lambda: SimpleNamespace(st_size=size))
    with pytest.raises(ValueError, match="bound"):
        _read(path)


@pytest.mark.parametrize("delta", [-1, 1])
def test_concurrent_shrink_or_growth_still_rejected(delta):
    stat = SimpleNamespace(st_size=32, st_mtime_ns=1, st_ino=1)
    path = SimpleNamespace(stat=lambda: stat, open=lambda _: io.BytesIO(b"x" * (32 + delta)))
    with pytest.raises(ValueError, match="changed"):
        _read(path)
