"""Read the research origin carried by scheduled run manifests."""

from collections.abc import Mapping


def research_origin(manifest, row):
    """Return the origin and the original analysis clock, when recorded."""
    settings = manifest.get("settings") or {}
    mode = settings.get("run_mode") or manifest.get("run_mode")
    if mode == "overlay_only" or "overlay_research_source" in row:
        receipt = row.get("overlay_research_source")
        return "overlay_only", receipt.get("analysis_started_at") if isinstance(receipt, Mapping) else None
    if "research_reuse" in row:
        receipt = row["research_reuse"]
        return "reused_full", receipt.get("analysis_started_at") if isinstance(receipt, Mapping) else None
    if mode == "full" and row.get("status") == "success":
        return "full", row.get("started_at")
    return None, None
