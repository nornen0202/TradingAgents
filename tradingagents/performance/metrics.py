from __future__ import annotations


def empty_action_performance_summary() -> dict[str, int]:
    return {
        "recommendations": 0,
        "outcomes": 0,
        "closed_trades": 0,
        "learned_intuitions": 0,
    }
