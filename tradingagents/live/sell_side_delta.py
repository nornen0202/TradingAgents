from __future__ import annotations

from typing import Any


_DOWNGRADE_ACTIONS = {
    "SUPPORT_FAIL": ("REDUCE_RISK", "SUPPORT_FAIL", ("SUPPORT_BROKEN",)),
    "FAILED_BREAKOUT": ("REDUCE_RISK", "FAILED_BREAKOUT", ("FAILED_BREAKOUT",)),
    "INVALIDATED": ("STOP_LOSS", "INVALIDATION_BROKEN", ("INVALIDATION_BROKEN",)),
}

_NEWS_DOWNGRADES = {
    "earnings_estimate_downgraded": ("REDUCE_RISK", "NEGATIVE_EARNINGS_GUIDANCE", ("NEGATIVE_EARNINGS_GUIDANCE",)),
    "regulatory_overhang": ("REDUCE_RISK", "NEGATIVE_DISCLOSURE_SHOCK", ("REGULATORY_OVERHANG",)),
    "sector_rotation": ("REDUCE_RISK", "SECTOR_HEADWIND", ("SECTOR_HEADWIND",)),
}


def build_sell_side_delta_candidates(
    *,
    live_context_delta: dict[str, Any] | None,
    held_tickers: set[str] | None = None,
) -> list[dict[str, Any]]:
    if not live_context_delta:
        return []
    held_tickers = {str(ticker).upper() for ticker in (held_tickers or set())}
    candidates: list[dict[str, Any]] = []
    for item in live_context_delta.get("ticker_deltas") or []:
        if not isinstance(item, dict):
            continue
        ticker = str(item.get("ticker") or "").strip()
        if not ticker:
            continue
        held = not held_tickers or ticker.upper() in held_tickers
        if not held:
            continue
        delta = _candidate_from_market_delta(item)
        if delta is None:
            delta = _candidate_from_news_delta(item)
        if delta is None:
            continue
        candidates.append(delta)
    return candidates


def render_risk_action_delta_markdown(candidates: list[dict[str, Any]]) -> str:
    lines = ["# Risk Action Delta", ""]
    if not candidates:
        lines.append("- No live sell-side downgrades were detected.")
        return "\n".join(lines)
    for candidate in candidates:
        evidence = candidate.get("evidence") if isinstance(candidate.get("evidence"), dict) else {}
        evidence_text = ", ".join(f"{key}={value}" for key, value in evidence.items() if value is not None) or "no numeric evidence"
        lines.append(
            f"- {candidate.get('ticker')}: {candidate.get('previous_action')} -> "
            f"{candidate.get('new_risk_action')} ({candidate.get('delta_type')}); {evidence_text}"
        )
    return "\n".join(lines)


def _candidate_from_market_delta(item: dict[str, Any]) -> dict[str, Any] | None:
    live_action = str(item.get("live_action") or "").upper()
    timing_state = str(item.get("execution_timing_state") or "").upper()
    key = live_action if live_action in _DOWNGRADE_ACTIONS else timing_state
    if key not in _DOWNGRADE_ACTIONS:
        return None
    new_action, delta_type, reason_codes = _DOWNGRADE_ACTIONS[key]
    return _delta_payload(
        item,
        new_risk_action=new_action,
        delta_type=delta_type,
        reason_codes=reason_codes,
    )


def _candidate_from_news_delta(item: dict[str, Any]) -> dict[str, Any] | None:
    tags = [str(tag).strip() for tag in (item.get("news_delta") or []) if str(tag).strip()]
    for tag in tags:
        if tag not in _NEWS_DOWNGRADES:
            continue
        new_action, delta_type, reason_codes = _NEWS_DOWNGRADES[tag]
        return _delta_payload(
            item,
            new_risk_action=new_action,
            delta_type=delta_type,
            reason_codes=reason_codes,
        )
    return None


def _delta_payload(
    item: dict[str, Any],
    *,
    new_risk_action: str,
    delta_type: str,
    reason_codes: tuple[str, ...],
) -> dict[str, Any]:
    contract_evidence = item.get("contract_evidence") if isinstance(item.get("contract_evidence"), dict) else {}
    evidence = {
        "last_price": item.get("live_price"),
        "support_level": contract_evidence.get("support_level"),
        "invalidation_level": contract_evidence.get("invalidation_level"),
        "breakout_level": contract_evidence.get("breakout_level"),
        "relative_volume": item.get("relative_volume"),
    }
    return {
        "ticker": str(item.get("ticker") or ""),
        "previous_action": str(item.get("base_action") or "WAIT"),
        "new_risk_action": new_risk_action,
        "delta_type": delta_type,
        "reason_codes": list(reason_codes),
        "evidence": evidence,
    }
