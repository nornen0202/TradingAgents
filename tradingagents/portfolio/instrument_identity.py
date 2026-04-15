from __future__ import annotations

from tradingagents.agents.utils.instrument_resolver import resolve_instrument

from .account_models import InstrumentIdentity


def resolve_identity(broker_symbol: str, display_name: str | None = None) -> InstrumentIdentity:
    broker_symbol = str(broker_symbol or "").strip()
    if not broker_symbol and not display_name:
        raise ValueError("Either broker_symbol or display_name is required.")

    last_error: Exception | None = None
    resolver_inputs: list[str] = []
    if _looks_like_symbol(broker_symbol):
        resolver_inputs.append(broker_symbol)
        if display_name and display_name.strip() and display_name.strip().upper() != broker_symbol.upper():
            resolver_inputs.append(display_name)
    else:
        if display_name and display_name.strip():
            resolver_inputs.append(display_name)
        if broker_symbol:
            resolver_inputs.append(broker_symbol)

    for candidate in resolver_inputs:
        if not candidate:
            continue
        try:
            profile = resolve_instrument(candidate)
            return InstrumentIdentity(
                broker_symbol=broker_symbol or profile.krx_code or profile.primary_symbol,
                canonical_ticker=profile.primary_symbol,
                yahoo_symbol=profile.yahoo_symbol or profile.primary_symbol,
                krx_code=profile.krx_code,
                dart_corp_code=profile.dart_corp_code,
                display_name=profile.display_name,
                exchange=profile.exchange,
                country=profile.country,
                currency=profile.currency,
            )
        except Exception as exc:  # pragma: no cover
            last_error = exc

    raise ValueError(f"Could not resolve instrument identity for '{broker_symbol}' / '{display_name}'.") from last_error


def _looks_like_symbol(value: str) -> bool:
    symbol = str(value or "").strip().upper()
    if not symbol:
        return False
    if " " in symbol:
        return False
    if symbol[0] == "." or symbol[-1] == "." or symbol.count(".") > 1:
        return False
    return all(ch.isalnum() or ch in {".", "-"} for ch in symbol)
