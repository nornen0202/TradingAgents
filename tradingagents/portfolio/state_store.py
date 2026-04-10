from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .account_models import AccountSnapshot, PortfolioCandidate, PortfolioRecommendation


def save_portfolio_outputs(
    *,
    private_dir: Path,
    snapshot: AccountSnapshot,
    candidates: list[PortfolioCandidate],
    recommendation: PortfolioRecommendation,
    portfolio_report_markdown: str,
    batch_metrics: dict[str, Any],
    warnings: list[str],
) -> dict[str, str]:
    private_dir.mkdir(parents=True, exist_ok=True)

    account_snapshot_path = private_dir / "account_snapshot.json"
    candidates_path = private_dir / "portfolio_candidates.json"
    report_path = private_dir / "portfolio_report.json"
    report_markdown_path = private_dir / "portfolio_report.md"
    proposed_orders_path = private_dir / "proposed_orders.json"
    audit_path = private_dir / "decision_audit.json"

    _write_json(account_snapshot_path, snapshot.to_dict())
    _write_json(candidates_path, {"candidates": [candidate.to_dict() for candidate in candidates]})
    _write_json(report_path, recommendation.to_dict())
    report_markdown_path.write_text(portfolio_report_markdown, encoding="utf-8")
    _write_json(proposed_orders_path, {"orders": _build_proposed_orders(snapshot, recommendation)})
    _write_json(
        audit_path,
        {
            "snapshot_id": snapshot.snapshot_id,
            "account_value_krw": snapshot.account_value_krw,
            "decision_distribution": batch_metrics.get("decision_distribution") or {},
            "stance_distribution": batch_metrics.get("stance_distribution") or {},
            "entry_action_distribution": batch_metrics.get("entry_action_distribution") or {},
            "warnings": list(warnings),
            "candidates": [candidate.to_dict() for candidate in candidates],
            "actions": [action.to_dict() for action in recommendation.actions],
        },
    )
    return {
        "account_snapshot_json": account_snapshot_path.as_posix(),
        "portfolio_candidates_json": candidates_path.as_posix(),
        "portfolio_report_json": report_path.as_posix(),
        "portfolio_report_md": report_markdown_path.as_posix(),
        "proposed_orders_json": proposed_orders_path.as_posix(),
        "decision_audit_json": audit_path.as_posix(),
    }


def _build_proposed_orders(snapshot: AccountSnapshot, recommendation: PortfolioRecommendation) -> list[dict[str, Any]]:
    orders: list[dict[str, Any]] = []
    for action in recommendation.actions:
        if action.delta_krw_now == 0:
            continue
        position = snapshot.find_position(action.canonical_ticker)
        estimated_price = int(position.market_price_krw if position else 0)
        qty = None
        if estimated_price > 0:
            qty = int(abs(action.delta_krw_now) // estimated_price)
            if qty <= 0:
                qty = None
        side = "buy" if action.delta_krw_now > 0 else "sell"
        orders.append(
            {
                "canonical_ticker": action.canonical_ticker,
                "display_name": action.display_name,
                "side": side,
                "action_now": action.action_now,
                "delta_krw_now": action.delta_krw_now,
                "estimated_market_price_krw": estimated_price or None,
                "estimated_qty": qty,
            }
        )
    return orders


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
