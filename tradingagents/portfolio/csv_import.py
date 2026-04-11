from __future__ import annotations

import csv
from datetime import datetime

from .account_models import AccountSnapshot, PortfolioProfile, Position
from .instrument_identity import resolve_identity


def load_snapshot_from_positions_csv(profile: PortfolioProfile) -> AccountSnapshot:
    if profile.csv_positions_path is None:
        raise ValueError("csv_positions_path is not configured.")

    positions: list[Position] = []
    with profile.csv_positions_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            identity = resolve_identity(
                str(row.get("broker_symbol") or row.get("ticker") or row.get("symbol") or ""),
                str(row.get("display_name") or row.get("name") or "") or None,
            )
            positions.append(
                Position(
                    broker_symbol=identity.broker_symbol,
                    canonical_ticker=identity.canonical_ticker,
                    display_name=str(row.get("display_name") or identity.display_name),
                    sector=_optional_text(row.get("sector")),
                    quantity=float(row.get("quantity", 0) or 0),
                    available_qty=float(row.get("available_qty", row.get("quantity", 0)) or 0),
                    avg_cost_krw=int(float(row.get("avg_cost_krw", 0) or 0)),
                    market_price_krw=int(float(row.get("market_price_krw", 0) or 0)),
                    market_value_krw=int(float(row.get("market_value_krw", 0) or 0)),
                    unrealized_pnl_krw=int(float(row.get("unrealized_pnl_krw", 0) or 0)),
                )
            )

    now = datetime.now().astimezone()
    available_cash = profile.constraints.min_cash_buffer_krw
    return AccountSnapshot(
        snapshot_id=f"{now.strftime('%Y%m%dT%H%M%S')}_csv_{profile.name}",
        as_of=now.isoformat(),
        broker="csv_import",
        account_id=profile.name,
        currency="KRW",
        settled_cash_krw=available_cash,
        available_cash_krw=available_cash,
        buying_power_krw=available_cash,
        total_equity_krw=available_cash + sum(position.market_value_krw for position in positions),
        snapshot_health="VALID",
        cash_diagnostics={"source": "csv_import_default_cash"},
        pending_orders=tuple(),
        positions=tuple(positions),
        constraints=profile.constraints,
        warnings=("cash values defaulted from min_cash_buffer_krw because CSV import does not carry cash fields",),
    )


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
