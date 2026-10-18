"""Read-only, point-in-time experiment cards for the existing immutable registry.

Cards show unknown model/data metadata and absent observations explicitly. They
do not register, freeze, simulate or execute a strategy. Reading a missing path
never creates a SQLite database. HTML export is self-contained and escaped.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
import sqlite3
from typing import Any, Callable, Iterator

from .experiments import ExperimentRegistry, _stamp, validate_spec


CARD_VERSION = "experiment-card-v1"
_STATUSES = {
    "not_frozen": "규칙 고정 전",
    "awaiting_forward_start": "미래 관측 시작 대기",
    "awaiting_observations": "완료된 미래 모의 관측 없음",
    "collecting": "미래 모의 관측 수집 중",
    "window_ended": "등록된 관측 기간 종료",
}


def _cutoff(analysis_as_of: str | datetime, clock: Callable[[], datetime] | None) -> datetime:
    cutoff = _stamp(analysis_as_of)
    now = _stamp(clock() if clock else datetime.now(timezone.utc))
    if cutoff > now:
        raise ValueError("Card cutoff cannot be in the future")
    return cutoff


@contextmanager
def _registry_reader(path: str | Path, clock: Callable[[], datetime] | None) -> Iterator[ExperimentRegistry]:
    """Reuse the existing report implementation without its schema-writing init."""
    path = Path(path).resolve(strict=True)
    if not path.is_file():
        raise ValueError("Experiment registry must be a file")
    registry = object.__new__(ExperimentRegistry)
    registry.db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=5)
    registry.db.row_factory = sqlite3.Row
    registry.clock = clock or (lambda: datetime.now(timezone.utc))
    try:
        registry.db.execute("PRAGMA query_only=ON")
        yield registry
    finally:
        registry.close()


def _visible_decisions(registry: ExperimentRegistry, experiment_id: str, spec_hash: str,
                       cutoff: datetime) -> list[dict[str, Any]]:
    rows = registry.db.execute(
        "SELECT * FROM experiment_decisions WHERE experiment_id=? ORDER BY open_at", (experiment_id,),
    ).fetchall()
    decisions: list[dict[str, Any]] = []
    for row in rows:
        # Future payloads are never deserialized, hashed, scored or displayed.
        if _stamp(row["recorded_at"]) > cutoff:
            continue
        payload = registry._verified_payload(row, spec_hash)
        recorded_at, data_as_of = _stamp(row["recorded_at"]), _stamp(payload.get("data_as_of"))
        if data_as_of > recorded_at or data_as_of > cutoff:
            raise ValueError("Experiment decision contains future or unknown data timing")
        if not isinstance(payload.get("dataset_version"), str) or not payload["dataset_version"].strip():
            raise ValueError("Experiment decision has no dataset version")
        decisions.append(payload)
    return decisions


def _card(registry: ExperimentRegistry, experiment_id: str, cutoff: datetime) -> dict[str, Any]:
    report = registry.report(experiment_id, analysis_as_of=cutoff)
    spec = validate_spec(report["spec"])
    if spec["id"] != experiment_id:
        raise ValueError("Experiment identity does not match the frozen spec")
    decisions = _visible_decisions(registry, experiment_id, report["spec_hash"], cutoff)
    if not report["frozen_at"]:
        status = "not_frozen"
    elif cutoff < _stamp(spec["forward_start"]):
        status = "awaiting_forward_start"
    elif cutoff >= _stamp(spec["forward_end"]):
        status = "window_ended"
    else:
        status = "collecting" if report["sessions"] else "awaiting_observations"
    model_keys = ("model", "model_name", "provider", "model_version", "prompt_hash")
    declared_model = {key: spec["ai_rules"][key] for key in model_keys if spec["ai_rules"].get(key) not in (None, "")}
    data_times = sorted({_stamp(item["data_as_of"]).isoformat() for item in decisions})
    data_versions = sorted({item["dataset_version"] for item in decisions})
    arms = report["arms"] if report["sessions"] else None
    limits = [
        "미래 모의 관측 결과이며 실계좌 체결·수익률이 아닙니다. 관측 기간만으로 수익성을 입증하지 않습니다.",
        "규칙 설명과 실제 제출된 비중의 일치 여부는 별도 검토가 필요합니다.",
        "표시한 데이터 버전은 기록된 식별자입니다. 원천 데이터의 당시 공시 가능 시각까지 보증하지 않습니다.",
        "모델 이름·버전이 미기록이면 알 수 없음으로 표시합니다. 비용과 모델 식별자는 별개입니다.",
    ] + report["limitations"]
    return {
        "card_version": CARD_VERSION, "id": experiment_id, "as_of": report["as_of"],
        "status": status, "status_label": _STATUSES[status],
        "hypothesis": spec["hypothesis"], "spec_hash": report["spec_hash"],
        "registered_at": report["registered_at"], "frozen_at": report["frozen_at"],
        "rules": {"baseline": spec["baseline_rules"], "ai": spec["ai_rules"]},
        "data": {
            "universe": spec["universe"], "benchmark": spec["benchmark"],
            "training_end": spec["training_end"], "forward_start": spec["forward_start"],
            "forward_end": spec["forward_end"], "dataset_versions": data_versions,
            "input_data_as_of": data_times,
            "status": "recorded" if decisions else "not_recorded",
        },
        "model": {"status": "declared" if declared_model else "not_recorded", "declared": declared_model},
        "costs": {
            "initial_capital": spec["capital"], "currency": spec["currency"],
            "fee_bps_per_side": spec["costs"]["fee_bps"],
            "slippage_bps_per_side": spec["costs"]["slippage_bps"],
            "model_cost": report["model_cost"], "validation_seconds": report["validation_seconds"],
        },
        "results": {
            "basis": "forward_paper", "sessions": report["sessions"],
            "pending_sessions": report["pending_sessions"], "arms": arms,
            "status": "observed" if arms is not None else "no_observations",
            "message": "동일 자본·대상·비용 조건의 미래 모의 관측입니다." if arms is not None else
                       "완료된 미래 모의 관측이 없어 수익률·낙폭을 표시하지 않습니다.",
        },
        "limitations": limits,
    }


def read_experiment_card(registry_path: str | Path, experiment_id: str, *,
                         analysis_as_of: str | datetime,
                         clock: Callable[[], datetime] | None = None) -> dict[str, Any]:
    """Read one registered experiment using only observations known by cutoff."""
    if not isinstance(experiment_id, str) or not experiment_id.strip() or len(experiment_id) > 300:
        raise ValueError("A nonempty experiment id of at most 300 characters is required")
    cutoff = _cutoff(analysis_as_of, clock)
    with _registry_reader(registry_path, clock) as registry:
        return _card(registry, experiment_id, cutoff)


def list_experiment_cards(registry_path: str | Path, *, analysis_as_of: str | datetime,
                          clock: Callable[[], datetime] | None = None) -> dict[str, Any]:
    """List visible cards; future experiments do not affect the historical list.

    A missing registry is an honest empty state and does not create a file. An
    invalid/unknown registration timestamp is excluded, never inferred from the
    filesystem or experiment's proposed start date. A visible corrupt card fails
    closed instead of silently producing a partial performance leaderboard.
    """
    cutoff = _cutoff(analysis_as_of, clock)
    result: dict[str, Any] = {"as_of": cutoff.isoformat(), "cards": [], "status": "empty", "issues": []}
    if not Path(registry_path).exists():
        result["issues"] = ["등록된 실험이 없습니다. 실험 등록·규칙 고정 후 미래 모의 관측을 기록해 주세요."]
        return result
    with _registry_reader(registry_path, clock) as registry:
        rows = registry.db.execute("SELECT id,registered_at FROM experiments ORDER BY id").fetchall()
        for row in rows:
            try:
                registered_at = _stamp(row["registered_at"])
            except (ValueError, TypeError):
                continue
            if registered_at <= cutoff:
                result["cards"].append(_card(registry, row["id"], cutoff))
    result["status"] = "ok" if result["cards"] else "empty"
    return result


def render_experiment_card(card: dict[str, Any]) -> str:
    """Render one self-contained Korean card; all registry content is escaped."""
    def value(item: Any) -> str:
        if item is None:
            return "알 수 없음"
        if isinstance(item, (dict, list)):
            return escape(json.dumps(item, ensure_ascii=False, indent=2, allow_nan=False))
        return escape(str(item))

    def rows(items: list[tuple[str, Any]]) -> str:
        return "".join(f"<tr><th>{escape(label)}</th><td><pre>{value(item)}</pre></td></tr>" for label, item in items)

    cost, data, results = card["costs"], card["data"], card["results"]
    model = card["model"]["declared"] or None
    summary = rows([
        ("실험 ID", card["id"]), ("상태", card["status_label"]), ("검토 기준 시각", card["as_of"]),
        ("가설", card["hypothesis"]), ("규칙 해시", card["spec_hash"]),
        ("등록 시각", card["registered_at"]), ("규칙 고정 시각", card["frozen_at"]),
        ("기존 규칙", card["rules"]["baseline"]), ("AI 보강 규칙", card["rules"]["ai"]),
        ("대상 종목", data["universe"]), ("비교 지수", data["benchmark"]),
        ("연구 종료 시각", data["training_end"]),
        ("미래 관측 기간", [data["forward_start"], data["forward_end"]]),
        ("입력 데이터 버전", data["dataset_versions"] or None),
        ("입력 기준 시각", data["input_data_as_of"] or None), ("기록된 모델", model),
        ("초기 가상자본", f"{cost['initial_capital']:,.2f} {cost['currency']}"),
        ("편도 수수료 / 슬리피지", f"{cost['fee_bps_per_side']} / {cost['slippage_bps_per_side']} bps"),
        ("누적 모델 비용", f"{cost['model_cost']:,.4f} {cost['currency']}"),
        ("검증 시간", f"{cost['validation_seconds']}초"),
        ("완료 / 대기 관측", f"{results['sessions']} / {results['pending_sessions']}"),
    ])
    metrics = ""
    if results["arms"] is not None:
        metric_rows = []
        for arm, label in (("baseline", "기존 규칙"), ("ai", "AI 보강"), ("benchmark", "비교 지수")):
            item = results["arms"][arm]
            metric_rows.append("<tr>" + "".join(f"<td>{value(cell)}</td>" for cell in (
                label, f"{item['net_return_pct']:.4f}%", f"{item['max_drawdown_pct']:.4f}%",
                item["trade_count"], f"{item['turnover_over_initial']:.4f}",
                f"{item['execution_cost']:.4f}",
                f"{item['net_after_model_cost_pct']:.4f}%" if "net_after_model_cost_pct" in item else "해당 없음",
            )) + "</tr>")
        metrics = "<div class='scroll'><table><thead><tr><th>비교군</th><th>비용 차감 수익률</th><th>최대낙폭</th><th>매매 건수</th><th>회전율</th><th>체결 비용</th><th>모델비용 추가 차감</th></tr></thead><tbody>" + "".join(metric_rows) + "</tbody></table></div>"
    limitations = "".join(f"<li>{value(item)}</li>" for item in card["limitations"])
    return "<!doctype html><html lang='ko'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>" + \
        "<title>실험 카드 · " + value(card["id"]) + "</title><style>" + \
        "body{font-family:system-ui,sans-serif;max-width:1080px;margin:24px auto;padding:0 16px;line-height:1.6;color:#18283b}" + \
        "table{border-collapse:collapse;width:100%;margin:16px 0}th,td{border:1px solid #ccd6e2;padding:10px;text-align:left;vertical-align:top}" + \
        "th{background:#eef3f9;min-width:100px}pre{white-space:pre-wrap;overflow-wrap:anywhere;margin:0;font:inherit}.scroll{overflow:auto}" + \
        ".status{background:#edf6ff;padding:12px;border-radius:8px}li{margin:8px 0}</style>" + \
        "<main><h1>전략 실험 카드</h1><p class='status'>" + value(card["status_label"]) + \
        " · 실계좌 주문 없음</p><table><tbody>" + summary + "</tbody></table><h2>미래 모의 검증</h2><p>" + \
        value(results["message"]) + "</p>" + metrics + "<h2>해석의 한계</h2><ul>" + limitations + "</ul></main></html>"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read/export point-in-time strategy experiment cards")
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--id", help="Omit to list all experiments visible at the cutoff")
    parser.add_argument("--format", choices=("json", "html"), default="json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.format == "html" and not args.id:
            raise ValueError("HTML export requires --id")
        data = read_experiment_card(args.registry, args.id, analysis_as_of=args.as_of) if args.id else \
            list_experiment_cards(args.registry, analysis_as_of=args.as_of)
        output = render_experiment_card(data) if args.format == "html" else \
            json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output)
        return 0
    except (ValueError, OSError, sqlite3.Error, KeyError, TypeError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
