from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from tradingagents.portfolio.performance.etf_alternatives import ExternalCapitalFlow, load_external_capital_flows

from .models import CashflowSource, CashflowType, DatedCashflow


def load_dated_cashflows(path: str | Path | None, *, warnings: list[str] | None = None) -> list[DatedCashflow]:
    flows = load_external_capital_flows(path, warnings=warnings)
    source = _source_for_path(path)
    return [_to_dated_cashflow(index, flow, source=source) for index, flow in enumerate(flows, start=1)]


def _to_dated_cashflow(index: int, flow: ExternalCapitalFlow, *, source: CashflowSource) -> DatedCashflow:
    flow_type = _cashflow_type(flow.flow_type)
    return DatedCashflow(
        event_id=f"{source.value}:{flow.date}:{index}",
        event_date=date.fromisoformat(flow.date),
        event_time=None,
        type=flow_type,
        amount_krw=float(flow.signed_amount_krw),
        currency="KRW",
        source=source,
        description=str(flow.raw.get("description") or flow.raw.get("memo") or flow.raw.get("note") or "") or None,
        raw=flow.raw,
    )


def _cashflow_type(value: str) -> CashflowType:
    normalized = str(value or "").strip().lower()
    mapping = {
        "deposit": CashflowType.DEPOSIT,
        "withdrawal": CashflowType.WITHDRAWAL,
        "dividend": CashflowType.DIVIDEND,
        "interest": CashflowType.INTEREST,
        "fee": CashflowType.FEE,
        "tax": CashflowType.TAX,
        "fx_conversion_in": CashflowType.FX_CONVERSION_IN,
        "fx_conversion_out": CashflowType.FX_CONVERSION_OUT,
    }
    return mapping.get(normalized, CashflowType.UNKNOWN_EXTERNAL)


def _source_for_path(path: Any) -> CashflowSource:
    if not path:
        return CashflowSource.MANUAL_JSON
    suffix = Path(path).suffix.lower()
    return CashflowSource.MANUAL_CSV if suffix == ".csv" else CashflowSource.MANUAL_JSON
