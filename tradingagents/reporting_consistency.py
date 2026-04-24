from __future__ import annotations

from typing import Any

from tradingagents.live.context_delta import render_report_vs_live_delta_markdown


def render_consistency_section(live_context_delta: dict[str, Any] | None) -> str:
    return render_report_vs_live_delta_markdown(live_context_delta)
