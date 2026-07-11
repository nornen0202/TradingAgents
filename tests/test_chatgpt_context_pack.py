from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


MODULE_PATH = Path(".github/scripts/build_chatgpt_context_pack.py")
SPEC = importlib.util.spec_from_file_location("build_chatgpt_context_pack", MODULE_PATH)
pack = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = pack
SPEC.loader.exec_module(pack)


def _write_run(
    tmp_path: Path,
    *,
    run_id: str,
    run_mode: str,
    decision_ready: bool,
    conditional_strategy_ready: bool = False,
) -> Path:
    run_dir = tmp_path / run_id
    run_dir.mkdir()
    manifest = {
        "run_id": run_id,
        "started_at": "2026-07-10T12:00:00+09:00",
        "settings": {"market": "US", "run_mode": run_mode},
        "decision_bundle": {
            "artifacts": {"decision_bundle_v2_json": "decision_bundle_v2.json"},
        },
    }
    (run_dir / "run.json").write_text(json.dumps(manifest), encoding="utf-8")
    (run_dir / "decision_bundle_v2.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "quality": {
                    "decision_ready": decision_ready,
                    "conditional_strategy_ready": conditional_strategy_ready,
                },
                "strategy_table": [{"ticker": "NVDA", "strategy_ko": "보유 유지"}],
            }
        ),
        encoding="utf-8",
    )
    return run_dir


def test_ready_bundle_selects_execution_mode_and_stable_transmission_key(tmp_path: Path):
    run_dir = _write_run(tmp_path, run_id="overlay-ready", run_mode="overlay_only", decision_ready=True)
    prompt = tmp_path / "prompt.md"
    prompt.write_text("모든 답변은 한국어로 작성한다.", encoding="utf-8")

    first_payload, first_meta = pack.build_context_pack(run_dir=run_dir, prompt_path=prompt)
    second_payload, second_meta = pack.build_context_pack(run_dir=run_dir, prompt_path=prompt)

    assert first_meta["mode"] == "execution"
    assert first_meta["transmission_key"] == second_meta["transmission_key"]
    assert first_payload == second_payload
    assert "REPORT_MODE: EXECUTION" in first_payload
    assert "BEGIN_TRADINGAGENTS_CONTEXT" in first_payload
    assert first_payload.count("모든 답변은 한국어로 작성한다.") == 1


def test_non_ready_overlay_selects_compact_outage_mode(tmp_path: Path):
    run_dir = _write_run(tmp_path, run_id="overlay-stale", run_mode="overlay_only", decision_ready=False)
    prompt = tmp_path / "prompt.md"
    prompt.write_text("한국어 장애 보고서", encoding="utf-8")

    payload, metadata = pack.build_context_pack(run_dir=run_dir, prompt_path=prompt)

    assert metadata["mode"] == "outage"
    assert metadata["decision_ready"] is False
    assert "REPORT_MODE: OUTAGE" in payload


def test_current_but_limited_overlay_selects_conditional_mode(tmp_path: Path):
    run_dir = _write_run(
        tmp_path,
        run_id="overlay-conditional",
        run_mode="overlay_only",
        decision_ready=False,
        conditional_strategy_ready=True,
    )
    prompt = tmp_path / "prompt.md"
    prompt.write_text("한국어 조건부 전략", encoding="utf-8")

    payload, metadata = pack.build_context_pack(run_dir=run_dir, prompt_path=prompt)

    assert metadata["mode"] == "conditional"
    assert metadata["conditional_strategy_ready"] is True
    assert "REPORT_MODE: CONDITIONAL" in payload


def test_non_ready_full_run_selects_research_mode_and_execution_override_is_rejected(tmp_path: Path):
    run_dir = _write_run(tmp_path, run_id="daily-us", run_mode="full", decision_ready=False)
    prompt = tmp_path / "prompt.md"
    prompt.write_text("한국어 연구 보고서", encoding="utf-8")

    _payload, metadata = pack.build_context_pack(run_dir=run_dir, prompt_path=prompt)
    assert metadata["mode"] == "research"

    try:
        pack.build_context_pack(run_dir=run_dir, prompt_path=prompt, requested_mode="execution")
    except ValueError as exc:
        assert "decision_ready=true" in str(exc)
    else:
        raise AssertionError("execution mode must reject a non-ready bundle")


def test_public_bundle_file_can_build_payload_without_archive(tmp_path: Path):
    bundle_path = tmp_path / "decision_bundle.json"
    bundle_path.write_text(
        json.dumps(
            {
                "run_id": "overlay-public-us",
                "market": "US",
                "quality": {"decision_ready": True},
                "strategy_table": [{"ticker": "NVDA", "strategy_ko": "보유 유지"}],
            }
        ),
        encoding="utf-8",
    )
    prompt = tmp_path / "prompt.md"
    prompt.write_text("한국어 실행 전략", encoding="utf-8")

    payload, metadata = pack.build_context_pack_from_bundle(bundle_path=bundle_path, prompt_path=prompt)

    assert metadata["mode"] == "execution"
    assert metadata["decision_bundle_present"] is True
    assert "overlay-public-us" in payload


def test_context_pack_keeps_all_holdings_and_only_five_new_candidates():
    rows = [
        {"ticker": "HELD1", "is_held": True, "strategy_ko": "보유 유지", "raw_codes": {"x": 1}},
        {"ticker": "HELD2", "is_held": True, "strategy_ko": "보유 유지", "raw_codes": {"x": 2}},
        *[
            {
                "ticker": f"NEW{index}",
                "is_held": False,
                "strategy_ko": "조건 충족 전 대기",
                "raw_codes": {"x": index},
            }
            for index in range(1, 8)
        ],
    ]

    compact = pack._compact_decision_bundle({"strategy_table": rows, "benchmark_context": {}})

    assert [row["ticker"] for row in compact["strategy_table"]] == [
        "HELD1",
        "HELD2",
        "NEW1",
        "NEW2",
        "NEW3",
        "NEW4",
        "NEW5",
    ]
    assert all("raw_codes" not in row for row in compact["strategy_table"])
    assert compact["transmission_scope"] == {
        "source_ticker_count": 9,
        "transmitted_ticker_count": 7,
        "held_ticker_count": 2,
        "new_candidate_limit": 5,
        "omitted_nonheld_ticker_count": 2,
        "raw_codes_omitted": True,
    }
