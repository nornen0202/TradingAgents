from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

# This file is also a directly executable repository helper.  Python otherwise
# places only .github/scripts on sys.path, so a clean checkout cannot import the
# adjacent tradingagents package unless the project happens to be installed.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tradingagents.work.packet import compact_decision_bundle


VALID_MODES = {"auto", "conditional", "execution", "mixed", "research", "outage"}


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _find_run_dir(archive_dir: Path, run_id: str | None) -> Path:
    if run_id:
        matches = list((archive_dir / "runs").glob(f"*/{run_id}"))
        if matches:
            return matches[0]
        raise FileNotFoundError(f"Run not found: {run_id}")
    latest = _load_json(archive_dir / "latest-run.json")
    latest_run_id = str(latest.get("run_id") or "")
    started_at = str(latest.get("started_at") or "")
    if not latest_run_id or len(started_at) < 4:
        raise FileNotFoundError("latest-run.json does not identify a run.")
    return archive_dir / "runs" / started_at[:4] / latest_run_id


def _resolve_artifact(run_dir: Path, value: Any) -> Path | None:
    if not value:
        return None
    path = Path(str(value))
    return path if path.is_absolute() else run_dir / path


def _decision_bundle(run_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    artifacts = ((manifest.get("decision_bundle") or {}).get("artifacts") or {})
    path = _resolve_artifact(run_dir, artifacts.get("decision_bundle_v2_json"))
    if path is None:
        path = run_dir / "decision_bundle_v2.json"
    return _load_json(path)


def _prism_current(run_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    artifacts = ((manifest.get("portfolio") or {}).get("artifacts") or {})
    path = _resolve_artifact(run_dir, artifacts.get("external_prism_current_signals_json"))
    return _load_json(path) if path is not None else {}


def _compact_decision_bundle(bundle: dict[str, Any], *, max_new_candidates: int = 5) -> dict[str, Any]:
    return compact_decision_bundle(bundle, max_new_candidates=max_new_candidates)


def choose_report_mode(*, requested_mode: str, manifest: dict[str, Any], bundle: dict[str, Any]) -> str:
    requested = str(requested_mode or "auto").strip().lower()
    if requested not in VALID_MODES:
        raise ValueError(f"Unsupported mode: {requested_mode}")
    decision_ready = bool((bundle.get("quality") or {}).get("decision_ready"))
    rows = [row for row in (bundle.get("strategy_table") or []) if isinstance(row, dict)]
    ready_rows = sum(bool((row.get("quality") or {}).get("execution_ready")) for row in rows)
    conditional_rows = sum(bool((row.get("quality") or {}).get("conditional_strategy_ready")) for row in rows)
    if requested == "execution" and not decision_ready:
        raise ValueError("Execution mode requires decision_bundle.quality.decision_ready=true.")
    if requested == "conditional" and not conditional_rows:
        raise ValueError("Conditional mode requires at least one conditional-ready row.")
    if requested != "auto":
        return requested
    if decision_ready:
        return "execution"
    if ready_rows:
        return "mixed"
    if bool((bundle.get("quality") or {}).get("conditional_strategy_ready")):
        return "conditional"
    if conditional_rows:
        return "mixed"
    run_mode = str(((manifest.get("settings") or {}).get("run_mode") or "")).lower()
    run_id = str(manifest.get("run_id") or "").lower()
    if run_mode in {"overlay_only", "selective_rerun_only"} or "overlay" in run_id:
        return "outage"
    return "research"


def build_context_pack(
    *,
    run_dir: Path,
    prompt_path: Path,
    requested_mode: str = "auto",
    extra_paths: list[Path] | None = None,
    max_payload_chars: int = 80_000,
) -> tuple[str, dict[str, Any]]:
    manifest = _load_json(run_dir / "run.json")
    if not manifest:
        raise FileNotFoundError(f"run.json is missing under {run_dir}")
    prompt = prompt_path.read_text(encoding="utf-8").strip()
    bundle = _compact_decision_bundle(_decision_bundle(run_dir, manifest))
    prism = _prism_current(run_dir, manifest)
    mode = choose_report_mode(requested_mode=requested_mode, manifest=manifest, bundle=bundle)
    source_payload: dict[str, Any] = {
        "run_id": manifest.get("run_id"),
        "started_at": manifest.get("started_at"),
        "market": ((manifest.get("settings") or {}).get("market")),
        "run_mode": ((manifest.get("settings") or {}).get("run_mode")),
        "decision_bundle": bundle,
        "prism_current_signals": prism,
    }
    extras: list[dict[str, Any]] = []
    for path in extra_paths or []:
        if not path.is_file():
            continue
        extras.append(
            {
                "name": path.name,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "content": path.read_text(encoding="utf-8"),
            }
        )
    if extras:
        source_payload["additional_context"] = extras
    return _render_context_payload(
        prompt=prompt,
        source_payload=source_payload,
        mode=mode,
        run_id=str(manifest.get("run_id") or run_dir.name),
        max_payload_chars=max_payload_chars,
    )


def build_context_pack_from_bundle(
    *,
    bundle_path: Path,
    prompt_path: Path,
    requested_mode: str = "auto",
    extra_paths: list[Path] | None = None,
    max_payload_chars: int = 80_000,
) -> tuple[str, dict[str, Any]]:
    bundle = _compact_decision_bundle(_load_json(bundle_path))
    if not bundle:
        raise FileNotFoundError(f"Decision bundle is missing or invalid: {bundle_path}")
    run_id = str(bundle.get("run_id") or bundle_path.stem)
    synthetic_manifest = {
        "run_id": run_id,
        "settings": {"run_mode": "overlay_only" if "overlay" in run_id.lower() else "full"},
    }
    mode = choose_report_mode(requested_mode=requested_mode, manifest=synthetic_manifest, bundle=bundle)
    source_payload: dict[str, Any] = {
        "run_id": run_id,
        "market": bundle.get("market"),
        "decision_bundle": bundle,
    }
    extras: list[dict[str, Any]] = []
    for path in extra_paths or []:
        if path.is_file():
            extras.append(
                {
                    "name": path.name,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "content": path.read_text(encoding="utf-8"),
                }
            )
    if extras:
        source_payload["additional_context"] = extras
    return _render_context_payload(
        prompt=prompt_path.read_text(encoding="utf-8").strip(),
        source_payload=source_payload,
        mode=mode,
        run_id=run_id,
        max_payload_chars=max_payload_chars,
    )


def _render_context_payload(
    *,
    prompt: str,
    source_payload: dict[str, Any],
    mode: str,
    run_id: str,
    max_payload_chars: int,
) -> tuple[str, dict[str, Any]]:
    source_json = json.dumps(source_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    source_sha256 = hashlib.sha256(source_json.encode("utf-8")).hexdigest()
    prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    payload_body = "\n\n".join(
        [
            prompt,
            "BEGIN_TRADINGAGENTS_CONTEXT\n"
            + json.dumps(source_payload, ensure_ascii=False, indent=2)
            + "\nEND_TRADINGAGENTS_CONTEXT",
        ]
    )
    key_material = f"chatgpt-context-v2:{run_id}:{mode}:{source_sha256}:{prompt_sha256}"
    transmission_key = hashlib.sha256(key_material.encode("utf-8")).hexdigest()
    header = "\n".join(
        [
            f"REPORT_MODE: {mode.upper()}",
            f"SOURCE_RUN_ID: {run_id}",
            f"SOURCE_SHA256: {source_sha256}",
            f"PROMPT_SHA256: {prompt_sha256}",
            f"TRANSMISSION_KEY: {transmission_key}",
            "이 payload와 동일한 TRANSMISSION_KEY가 이미 전송됐다면 내용을 다시 붙여넣지 말고 no-op으로 종료하세요.",
        ]
    )
    payload = f"{header}\n\n{payload_body}\n"
    if len(payload) > max(1, int(max_payload_chars)):
        raise ValueError(f"ChatGPT payload is too large: {len(payload)} chars > {max_payload_chars} chars")
    bundle = source_payload.get("decision_bundle") if isinstance(source_payload.get("decision_bundle"), dict) else {}
    metadata = {
        "run_id": run_id,
        "mode": mode,
        "source_sha256": source_sha256,
        "prompt_sha256": prompt_sha256,
        "transmission_key": transmission_key,
        "payload_chars": len(payload),
        "decision_ready": bool((bundle.get("quality") or {}).get("decision_ready")),
        "conditional_strategy_ready": bool(
            (bundle.get("quality") or {}).get("conditional_strategy_ready")
        ),
        "decision_bundle_present": bool(bundle),
        "prism_current_signal_count": len((source_payload.get("prism_current_signals") or {}).get("signals") or []),
    }
    return payload, metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deterministic, deduplicated ChatGPT context payload.")
    parser.add_argument("--archive-dir", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--prompt", required=True, type=Path)
    parser.add_argument("--mode", default="auto", choices=sorted(VALID_MODES))
    parser.add_argument("--extra", action="append", default=[], type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--metadata-output", type=Path)
    parser.add_argument("--max-payload-chars", type=int, default=80_000)
    parser.add_argument("--bundle-file", type=Path)
    args = parser.parse_args()

    if args.bundle_file:
        payload, metadata = build_context_pack_from_bundle(
            bundle_path=args.bundle_file,
            prompt_path=args.prompt,
            requested_mode=args.mode,
            extra_paths=args.extra,
            max_payload_chars=args.max_payload_chars,
        )
    else:
        if args.archive_dir is None:
            raise SystemExit("--archive-dir is required unless --bundle-file is provided")
        run_dir = _find_run_dir(args.archive_dir, args.run_id)
        payload, metadata = build_context_pack(
            run_dir=run_dir,
            prompt_path=args.prompt,
            requested_mode=args.mode,
            extra_paths=args.extra,
            max_payload_chars=args.max_payload_chars,
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8")
    metadata_path = args.metadata_output or args.output.with_suffix(args.output.suffix + ".json")
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(metadata, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
