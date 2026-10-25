"""Small offline checks of the actual price-line display functions."""
from pathlib import Path
import shutil
import subprocess

import pytest


@pytest.mark.skipif(shutil.which("node") is None, reason="Node is an optional frontend test runtime")
def test_chart_price_level_display_contract():
    fixture = Path(__file__).parent / "frontend/review_chart_levels.test.cjs"
    result = subprocess.run([shutil.which("node"), "--test", str(fixture)], capture_output=True,
                            text=True, encoding="utf-8", timeout=30, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
