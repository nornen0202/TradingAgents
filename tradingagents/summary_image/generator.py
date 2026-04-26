from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tradingagents.portfolio.account_models import AccountSnapshot, PortfolioCandidate, PortfolioRecommendation

from .openai_image import render_openai_summary_image
from .render_svg import write_summary_svg
from .spec import build_portfolio_summary_image_spec


def generate_summary_image_artifacts(
    *,
    private_dir: Path,
    snapshot: AccountSnapshot,
    recommendation: PortfolioRecommendation,
    candidates: list[PortfolioCandidate],
    manifest: dict[str, Any],
    live_sell_side_delta: list[dict[str, Any]] | None,
    report_writer_payload: dict[str, Any] | None,
    settings: Any | None,
) -> dict[str, str]:
    if settings is None or not bool(getattr(settings, "enabled", True)):
        return {}

    private_dir.mkdir(parents=True, exist_ok=True)
    mode = str(getattr(settings, "mode", "deterministic_svg") or "deterministic_svg").strip().lower()
    spec = build_portfolio_summary_image_spec(
        snapshot=snapshot,
        recommendation=recommendation,
        candidates=candidates,
        manifest=manifest,
        live_sell_side_delta=live_sell_side_delta,
        report_writer_payload=report_writer_payload,
        redact_account_values=bool(getattr(settings, "redact_account_values", False)),
    )
    spec_path = private_dir / "summary_image_spec.json"
    svg_path = private_dir / "summary_card.svg"
    prompt_path = private_dir / "summary_image_prompt.txt"
    metadata_path = private_dir / "summary_image_metadata.json"
    png_path = private_dir / "summary_card_ai.png"

    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    artifacts = {"summary_image_spec_json": spec_path.as_posix()}

    if mode in {"deterministic_svg", "both"}:
        write_summary_svg(spec, svg_path)
        artifacts["summary_card_svg"] = svg_path.as_posix()

    if mode in {"openai_image", "both"}:
        metadata = render_openai_summary_image(
            spec=spec,
            output_path=png_path,
            prompt_path=prompt_path,
            metadata_path=metadata_path,
            settings=settings,
        )
        artifacts["summary_image_prompt_txt"] = prompt_path.as_posix()
        artifacts["summary_image_metadata_json"] = metadata_path.as_posix()
        if metadata.get("status") == "generated" and png_path.exists():
            artifacts["summary_card_ai_png"] = png_path.as_posix()

    return artifacts
