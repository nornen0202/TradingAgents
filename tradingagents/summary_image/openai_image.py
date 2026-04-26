from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any


def render_openai_summary_image(
    *,
    spec: dict[str, Any],
    output_path: Path,
    prompt_path: Path,
    metadata_path: Path,
    settings: Any,
) -> dict[str, Any]:
    """Generate an optional AI-styled PNG summary. Failures are metadata, not pipeline blockers."""
    prompt = build_image_prompt(spec)
    prompt_path.write_text(prompt, encoding="utf-8")
    metadata = {
        "status": "skipped",
        "model": str(getattr(settings, "image_model", "gpt-image-2") or "gpt-image-2"),
        "size": str(getattr(settings, "image_size", "1024x1536") or "1024x1536"),
        "quality": str(getattr(settings, "image_quality", "medium") or "medium"),
        "output_path": output_path.as_posix(),
    }
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        metadata["reason"] = "missing_openai_api_key"
        _write_metadata(metadata_path, metadata)
        return metadata

    try:
        from openai import OpenAI
    except Exception as exc:  # pragma: no cover - depends on optional runtime package
        metadata.update({"status": "failed", "error": f"openai_import_failed: {exc}"})
        _write_metadata(metadata_path, metadata)
        return metadata

    try:
        client = OpenAI(api_key=api_key, timeout=float(getattr(settings, "request_timeout", 180.0) or 180.0))
        response = _generate_image(client, metadata=metadata, prompt=prompt)
        image_payload = response.data[0]
        b64_value = getattr(image_payload, "b64_json", None)
        if not b64_value and isinstance(image_payload, dict):
            b64_value = image_payload.get("b64_json")
        if b64_value:
            output_path.write_bytes(base64.b64decode(b64_value))
        else:
            url_value = getattr(image_payload, "url", None)
            if not url_value and isinstance(image_payload, dict):
                url_value = image_payload.get("url")
            if not url_value:
                raise RuntimeError("image response did not include b64_json or url")
            _download_image(str(url_value), output_path)
        metadata["status"] = "generated"
    except Exception as exc:  # pragma: no cover - network/API dependent
        metadata.update({"status": "failed", "error": str(exc)})

    _write_metadata(metadata_path, metadata)
    return metadata


def _generate_image(client: Any, *, metadata: dict[str, Any], prompt: str) -> Any:
    kwargs = {
        "model": metadata["model"],
        "prompt": prompt,
        "size": metadata["size"],
        "quality": metadata["quality"],
        "n": 1,
    }
    try:
        return client.images.generate(**kwargs, response_format="b64_json")
    except Exception as exc:
        if "response_format" not in str(exc):
            raise
        return client.images.generate(**kwargs)


def _download_image(url: str, output_path: Path) -> None:
    import requests

    response = requests.get(url, timeout=60)
    response.raise_for_status()
    output_path.write_bytes(response.content)


def build_image_prompt(spec: dict[str, Any]) -> str:
    """Prompt for optional AI image generation. The SVG path remains the source of truth."""
    run = spec.get("run") or {}
    account = spec.get("account") or {}
    counts = spec.get("counts") or {}
    top = ", ".join(str(item.get("ticker")) for item in (spec.get("top_priority") or []) if item.get("ticker"))
    checkpoints = "; ".join(
        f"{item.get('ticker')}: {item.get('condition')}" for item in (spec.get("next_checkpoints") or []) if item.get("ticker")
    )
    risks = "; ".join(str(item) for item in (spec.get("risks") or [])[:4])
    return (
        "Use case: productivity-visual\n"
        "Asset type: Korean investor-facing portfolio report summary image for a website\n"
        "Primary request: Create a polished one-page infographic summary card. Use the exact facts below. "
        "This is not a live trading signal and must look like a report-only summary.\n"
        "Style/medium: clean financial dashboard infographic, white background, navy headings, restrained green/orange risk accents, crisp icon-like shapes.\n"
        "Composition/framing: portrait layout, six numbered sections, similar to a compact account operations report.\n"
        "Text accuracy: preserve tickers, numbers, and Korean labels exactly. Do not invent tickers or counts.\n"
        f"Title: {spec.get('title')}\n"
        f"Run: {run.get('run_id')} / {run.get('date')} / status {run.get('status')}\n"
        f"Account: value {account.get('account_value')}, cash {account.get('available_cash')}, buffer {account.get('min_cash_buffer')}, mode {account.get('mode')}\n"
        f"Counts: buy now {counts.get('add_now')}, pilot {counts.get('pilot_ready')}, close confirm {counts.get('close_confirm')}, "
        f"trim to fund {counts.get('trim_to_fund')}, reduce risk {counts.get('reduce_risk')}, stop/exit {int(counts.get('stop_loss') or 0) + int(counts.get('exit') or 0)}\n"
        f"Top priority: {top or '-'}\n"
        f"Next checkpoints: {checkpoints or '-'}\n"
        f"Risks: {risks or '-'}\n"
        f"Footer text: {spec.get('footer')}\n"
        "Avoid: raw JSON, hallucinated prices, broker order language, live execution wording, watermark, blurry text."
    )


def _write_metadata(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
