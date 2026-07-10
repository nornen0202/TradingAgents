from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


MODULE_PATH = Path(".github/scripts/verify_decision_bundle.py")
SPEC = importlib.util.spec_from_file_location("verify_decision_bundle", MODULE_PATH)
verify = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = verify
SPEC.loader.exec_module(verify)


def test_valid_live_bundle_passes_and_ratio_is_recomputed(tmp_path: Path):
    bundle = {
        "version": 2,
        "run_id": "live-run",
        "quality": {"decision_ready": True, "fresh_row_ratio": 1.0, "minimum_fresh_row_ratio": 0.8},
        "strategy_table": [
            {
                "ticker": "NVDA",
                "strategy_ko": "보유 유지",
                "data_status_ko": "현재 세션 데이터 사용 가능",
                "last_price": 200,
                "market_data_asof": "2026-07-10T12:00:00-04:00",
                "session_vwap": 198,
                "relative_volume": 1.2,
                "quality": {"execution_ready": True},
            }
        ],
    }
    (tmp_path / "decision_bundle_v2.json").write_text(json.dumps(bundle), encoding="utf-8")

    result = verify.verify_run_dir(tmp_path, require_ready=True)

    assert result["errors"] == []
    assert result["decision_ready"] is True


def test_ready_bundle_fails_when_live_row_is_missing_vwap(tmp_path: Path):
    bundle = {
        "version": 2,
        "run_id": "broken-live-run",
        "quality": {"decision_ready": True, "fresh_row_ratio": 1.0, "minimum_fresh_row_ratio": 0.8},
        "strategy_table": [
            {
                "ticker": "NVDA",
                "strategy_ko": "지금 분할매수 검토",
                "data_status_ko": "현재 세션 데이터 사용 가능",
                "last_price": 200,
                "market_data_asof": "2026-07-10T12:00:00-04:00",
                "session_vwap": None,
                "relative_volume": 1.2,
                "quality": {"execution_ready": True},
            }
        ],
    }
    (tmp_path / "decision_bundle_v2.json").write_text(json.dumps(bundle), encoding="utf-8")

    result = verify.verify_run_dir(tmp_path, require_ready=True)

    assert any("missing session_vwap" in error for error in result["errors"])
