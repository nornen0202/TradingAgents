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
        "quality": {
            "decision_ready": True,
            "conditional_strategy_ready": True,
            "fresh_row_ratio": 1.0,
            "conditional_row_ratio": 1.0,
            "minimum_fresh_row_ratio": 0.8,
        },
        "strategy_table": [
            {
                "ticker": "NVDA",
                "strategy_ko": "보유 유지",
                "data_status_ko": "현재 세션 데이터 사용 가능",
                "last_price": 200,
                "market_data_asof": "2026-07-10T12:00:00-04:00",
                "session_vwap": 198,
                "relative_volume": 1.2,
                "quality": {"execution_ready": True, "conditional_strategy_ready": True},
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
        "quality": {
            "decision_ready": True,
            "conditional_strategy_ready": True,
            "fresh_row_ratio": 1.0,
            "conditional_row_ratio": 1.0,
            "minimum_fresh_row_ratio": 0.8,
        },
        "strategy_table": [
            {
                "ticker": "NVDA",
                "strategy_ko": "지금 분할매수 검토",
                "data_status_ko": "현재 세션 데이터 사용 가능",
                "last_price": 200,
                "market_data_asof": "2026-07-10T12:00:00-04:00",
                "session_vwap": None,
                "relative_volume": 1.2,
                "quality": {"execution_ready": True, "conditional_strategy_ready": True},
            }
        ],
    }
    (tmp_path / "decision_bundle_v2.json").write_text(json.dumps(bundle), encoding="utf-8")

    result = verify.verify_run_dir(tmp_path, require_ready=True)

    assert any("missing session_vwap" in error for error in result["errors"])


def test_public_stable_site_contract_does_not_require_private_markdown(tmp_path: Path):
    target = tmp_path / "latest" / "kr"
    target.mkdir(parents=True)
    (target / "status.json").write_text(
        json.dumps(
            {
                "latest_run_id": "ready-kr",
                "decision_ready": True,
                "conditional_strategy_ready": True,
            }
        ),
        encoding="utf-8",
    )
    (target / "source.json").write_text(
        json.dumps(
            {
                "decision_ready_run_id": "ready-kr",
                "artifacts": {
                    "public_decision_bundle_json": "decision_bundle.json",
                    "public_decision_bundle_status_json": "decision_bundle_status.json",
                },
            }
        ),
        encoding="utf-8",
    )
    (target / "decision_bundle.json").write_text(json.dumps({"version": 2}), encoding="utf-8")
    (target / "decision_bundle_status.json").write_text(
        json.dumps({"decision_ready": True}),
        encoding="utf-8",
    )

    result = verify.verify_site(tmp_path, market="kr")

    assert result["errors"] == []
    assert not (target / "strategy_table_ko.md").exists()


def test_public_stable_site_requires_declared_json_artifacts(tmp_path: Path):
    target = tmp_path / "latest" / "us"
    target.mkdir(parents=True)
    (target / "status.json").write_text(
        json.dumps({"latest_run_id": "ready-us", "decision_ready": True}),
        encoding="utf-8",
    )
    (target / "source.json").write_text(
        json.dumps(
            {
                "decision_ready_run_id": "ready-us",
                "artifacts": {"public_decision_bundle_json": "decision_bundle.json"},
            }
        ),
        encoding="utf-8",
    )
    (target / "decision_bundle.json").write_text(json.dumps({"version": 2}), encoding="utf-8")

    result = verify.verify_site(tmp_path, market="us")

    assert any("public_decision_bundle_status_json" in error for error in result["errors"])
