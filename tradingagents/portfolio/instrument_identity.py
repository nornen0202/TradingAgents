from __future__ import annotations

from tradingagents.agents.utils.instrument_resolver import resolve_instrument

from .account_models import InstrumentIdentity


def resolve_identity(broker_symbol: str, display_name: str | None = None) -> InstrumentIdentity:
    broker_symbol = str(broker_symbol or "").strip()
    if not broker_symbol and not display_name:
        raise ValueError("Either broker_symbol or display_name is required.")

    last_error: Exception | None = None
    for candidate in (display_name, broker_symbol):
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
