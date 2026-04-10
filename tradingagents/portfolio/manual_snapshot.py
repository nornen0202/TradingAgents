from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .account_models import AccountConstraints, AccountSnapshot, PendingOrder, Position


def load_manual_snapshot(path: str | Path) -> AccountSnapshot:
    payload = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    return account_snapshot_from_payload(payload)


def account_snapshot_from_payload(payload: dict[str, Any]) -> AccountSnapshot:
    constraints_payload = payload.get("constraints") or {}
    positions = tuple(
        Position(
            broker_symbol=str(item.get("broker_symbol") or item.get("canonical_ticker") or ""),
            canonical_ticker=str(item.get("canonical_ticker") or ""),
            display_name=str(item.get("display_name") or item.get("canonical_ticker") or ""),
            sector=_optional_text(item.get("sector")),
            quantity=float(item.get("quantity", 0) or 0),
            available_qty=float(item.get("available_qty", item.get("quantity", 0)) or 0),
            avg_cost_krw=int(float(item.get("avg_cost_krw", 0) or 0)),
            market_price_krw=int(float(item.get("market_price_krw", 0) or 0)),
            market_value_krw=int(float(item.get("market_value_krw", 0) or 0)),
            unrealized_pnl_krw=int(float(item.get("unrealized_pnl_krw", 0) or 0)),
        )
        for item in (payload.get("positions") or [])
    )
    pending_orders = tuple(
        PendingOrder(
            broker_order_id=str(item.get("broker_order_id") or ""),
            broker_symbol=str(item.get("broker_symbol") or ""),
            canonical_ticker=_optional_text(item.get("canonical_ticker")),
            side=str(item.get("side") or "unknown"),
            qty=float(item.get("qty", 0) or 0),
            remaining_qty=float(item.get("remaining_qty", item.get("qty", 0)) or 0),
            status=str(item.get("status") or "unknown"),
        )
        for item in (payload.get("pending_orders") or [])
    )
    return AccountSnapshot(
        snapshot_id=str(payload.get("snapshot_id") or ""),
        as_of=str(payload.get("as_of") or ""),
        broker=str(payload.get("broker") or "manual"),
        account_id=str(payload.get("account_id") or "manual"),
        currency=str(payload.get("currency") or "KRW"),
        settled_cash_krw=int(float(payload.get("settled_cash_krw", payload.get("available_cash_krw", 0)) or 0)),
        available_cash_krw=int(float(payload.get("available_cash_krw", 0) or 0)),
        buying_power_krw=int(float(payload.get("buying_power_krw", payload.get("available_cash_krw", 0)) or 0)),
        pending_orders=pending_orders,
        positions=positions,
        constraints=AccountConstraints(
            min_cash_buffer_krw=int(float(constraints_payload.get("min_cash_buffer_krw", 0) or 0)),
            min_trade_krw=int(float(constraints_payload.get("min_trade_krw", 100_000) or 100_000)),
            max_single_name_weight=float(constraints_payload.get("max_single_name_weight", 0.35) or 0.35),
            max_sector_weight=float(constraints_payload.get("max_sector_weight", 0.50) or 0.50),
            max_daily_turnover_ratio=float(constraints_payload.get("max_daily_turnover_ratio", 0.30) or 0.30),
            max_order_count_per_day=int(float(constraints_payload.get("max_order_count_per_day", 5) or 5)),
            respect_existing_weights_softly=bool(constraints_payload.get("respect_existing_weights_softly", True)),
        ),
        warnings=tuple(str(item) for item in (payload.get("warnings") or [])),
    )


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
