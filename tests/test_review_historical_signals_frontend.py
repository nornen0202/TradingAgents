"""Offline display-only historical marker projection and privacy checks."""
from pathlib import Path
import shutil
import subprocess

import pytest


@pytest.mark.skipif(shutil.which("node") is None, reason="Node is an optional frontend test runtime")
def test_historical_signal_display_contract():
    fixture = Path(__file__).parent / "frontend/review_historical_signals.test.cjs"
    result = subprocess.run([shutil.which("node"), "--test", str(fixture)], capture_output=True,
                            text=True, encoding="utf-8", timeout=30, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
