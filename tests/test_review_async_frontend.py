"""Optional Node fixture executes the actual browser request/polling functions."""
from pathlib import Path
import shutil
import subprocess

import pytest


@pytest.mark.skipif(shutil.which("node") is None, reason="Node is an optional frontend test runtime")
def test_viewer_async_request_contract():
    fixture = Path(__file__).parent / "frontend/review_async_requests.test.cjs"
    result = subprocess.run([shutil.which("node"), "--test", str(fixture)], capture_output=True,
                            text=True, encoding="utf-8", timeout=30, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
