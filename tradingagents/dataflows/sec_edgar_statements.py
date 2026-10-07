"""Bounded US financial statements from the SEC's filing-dated company facts.

Inspired by upstream TradingAgents' SEC vendor. Reuses this fork's SEC request
throttle and error handling while preserving the existing disclosure API.
"""

from __future__ import annotations

import csv
import io
import math
import re
from datetime import date, datetime, timezone
from functools import lru_cache

from .sec_edgar import _get_json, _ticker_map
from .vendor_exceptions import VendorInputError, VendorTransientError


_STATEMENTS = {
    "balance_sheet": [
        ("Total Assets", ("Assets",)),
        ("Current Assets", ("AssetsCurrent",)),
        ("Cash and Equivalents", ("CashAndCashEquivalentsAtCarryingValue",)),
        ("Total Liabilities", ("Liabilities",)),
        ("Current Liabilities", ("LiabilitiesCurrent",)),
        ("Stockholders Equity", ("StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest")),
    ],
    "income_statement": [
        ("Revenue", ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet")),
        ("Cost of Revenue", ("CostOfRevenue", "CostOfGoodsAndServicesSold")),
        ("Gross Profit", ("GrossProfit",)),
        ("Operating Income", ("OperatingIncomeLoss",)),
        ("Net Income", ("NetIncomeLoss",)),
        ("Diluted EPS", ("EarningsPerShareDiluted",)),
    ],
    "cashflow": [
        ("Operating Cash Flow", ("NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations")),
        ("Investing Cash Flow", ("NetCashProvidedByUsedInInvestingActivities",)),
        ("Financing Cash Flow", ("NetCashProvidedByUsedInFinancingActivities",)),
        ("Capital Expenditure", ("PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets")),
    ],
}
_ANNUAL_FORMS = {"10-K", "20-F", "40-F"}
_SPANS = {"annual": ((300, 400, ""),), "quarterly": ((60, 115, ""), (150, 200, " (6 months YTD)"), (240, 290, " (9 months YTD)"))}


@lru_cache(maxsize=16)
def _company_facts(cik: str, hour: str) -> dict:
    payload = _get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")
    facts = (payload.get("facts") or {}).get("us-gaap") or {}
    if not isinstance(facts, dict):
        raise VendorTransientError("SEC company facts have no usable US GAAP statements")
    # Keep only the fields used by these tools, rather than retaining full filings.
    relevant = {tag for rows in _STATEMENTS.values() for _, tags in rows for tag in tags}
    return {tag: value for tag, value in facts.items() if tag in relevant}


def _valid_fact(fact: dict, cutoff: str, freq: str, *, instant: bool) -> int | None:
    if not isinstance(fact, dict):
        return None
    try:
        end = date.fromisoformat(fact["end"])
        filed = date.fromisoformat(fact["filed"])
        if end.isoformat() > cutoff or filed.isoformat() > cutoff or filed < end:
            return None
        value = fact["val"]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            return None
        if instant:
            return 0 if not fact.get("start") else None
        start = date.fromisoformat(fact["start"])
    except (KeyError, TypeError, ValueError, OverflowError):
        return None
    days = (end - start).days
    return next((index for index, (lower, upper, _) in enumerate(_SPANS[freq]) if lower <= days <= upper), None)


def _as_of(facts: dict, tags: tuple[str, ...], cutoff: str, freq: str, *, instant: bool) -> tuple[dict, str]:
    """Select the latest public revision per period, never sum overlapping tags."""
    by_unit: dict[str, dict] = {}
    for tag in tags:
        entry = facts.get(tag)
        units = entry.get("units", {}) if isinstance(entry, dict) else {}
        if not isinstance(units, dict):
            continue
        for unit, rows in units.items():
            if not re.fullmatch(r"[A-Z]{3}(?:/shares)?", unit) or not isinstance(rows, list):
                continue
            values = by_unit.setdefault(unit, {})
            latest = {}
            annual_periods = set()
            for fact in rows:
                index = _valid_fact(fact, cutoff, freq, instant=instant)
                if index is None:
                    continue
                key = (fact["end"], index)
                if key in values:
                    continue
                if str(fact.get("form", "")).removesuffix("/A") in _ANNUAL_FORMS:
                    annual_periods.add(key)
                rank = (fact["filed"], str(fact.get("accn", "")))
                if key not in latest or rank >= (latest[key]["filed"], str(latest[key].get("accn", ""))):
                    latest[key] = fact
            values.update({key: fact for key, fact in latest.items() if freq != "annual" or key in annual_periods})
    for unit in sorted(by_unit, key=lambda unit: (not unit.startswith("USD"), unit)):
        if by_unit[unit]:
            return by_unit[unit], unit
    return {}, "USD"


def _statement(kind: str, ticker: str, freq: str, curr_date: str | None) -> str:
    freq = freq.lower()
    if freq not in _SPANS:
        raise VendorInputError("Statement frequency must be annual or quarterly")
    now = datetime.now(timezone.utc)
    cutoff = curr_date or now.date().isoformat()
    try:
        date.fromisoformat(cutoff)
    except (TypeError, ValueError) as exc:
        raise VendorInputError("Statement date must be YYYY-MM-DD") from exc
    canonical = ticker.strip().upper().replace(".", "-")
    cik = _ticker_map(now.date().isoformat()).get(canonical)
    if not cik:
        raise VendorTransientError(f"SEC statement coverage unavailable: {ticker} is not mapped to a US filer")
    facts = _company_facts(cik, now.strftime("%Y-%m-%dT%H"))
    lines = {label: _as_of(facts, tags, cutoff, freq, instant=kind == "balance_sheet") for label, tags in _STATEMENTS[kind]}
    chosen = {}
    for label, (values, _) in lines.items():
        chosen[label] = {}
        for end, index in values:
            chosen[label][end] = min(index, chosen[label].get(end, index))
    ends = sorted({end for selected in chosen.values() for end in selected})[-(8 if freq == "quarterly" else 4):]
    periods = sorted({(end, index) for selected in chosen.values() for end, index in selected.items() if end in ends})
    if not periods:
        raise VendorTransientError(f"SEC statement coverage unavailable: no {freq} {kind} facts filed by {cutoff} for {ticker}")
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(["Line item"] + [end + _SPANS[freq][index][2] for end, index in periods])
    filed_dates = set()
    for label, (values, unit) in lines.items():
        monetary = "/" not in unit
        cells = []
        for end, index in periods:
            fact = values.get((end, index)) if chosen[label].get(end) == index else None
            if fact is None:
                cells.append("")
            else:
                filed_dates.add(fact["filed"])
                cells.append(f"{fact['val'] / 1e6:.3f}" if monetary else f"{fact['val']:.4f}")
        writer.writerow([f"{label} ({unit}{' millions' if monetary else ''})"] + cells)
    return (
        f"# {kind.replace('_', ' ').title()} for {ticker.upper()} ({freq})\n"
        f"# SEC EDGAR facts filed on or before {cutoff}; latest revision available by that date.\n"
        f"# Filing dates represented: {', '.join(sorted(filed_dates))}.\n"
        "# Missing cells are unavailable, not zero. YTD spans are labeled; no quarters are derived.\n"
        "# Bounded US GAAP extract; foreign-taxonomy and untagged lines are not covered.\n"
        f"# Source: https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json\n\n"
        + buffer.getvalue()
    )


def get_balance_sheet(ticker: str, freq: str = "quarterly", curr_date: str | None = None) -> str:
    return _statement("balance_sheet", ticker, freq, curr_date)


def get_income_statement(ticker: str, freq: str = "quarterly", curr_date: str | None = None) -> str:
    return _statement("income_statement", ticker, freq, curr_date)


def get_cashflow(ticker: str, freq: str = "quarterly", curr_date: str | None = None) -> str:
    return _statement("cashflow", ticker, freq, curr_date)
