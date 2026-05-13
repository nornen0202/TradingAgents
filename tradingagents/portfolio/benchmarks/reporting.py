from __future__ import annotations

from typing import Any


def comparison_status_label(comparison: dict[str, Any]) -> str:
    status = str(comparison.get("status") or "").strip()
    if status == "OK":
        return "계산 가능"
    if status == "cashflow_dates_required":
        return "입금일 원장 필요"
    return status or "미확인"
