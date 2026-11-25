"""Same-session admission from the scheduled cohort and this VTS journal."""
from dataclasses import dataclass
from datetime import date
import re
from zoneinfo import ZoneInfo

from tradingagents.charting.bars import instant
from tradingagents.kis_strategy_contract import ZONES
from tradingagents.scheduled.research_refresh import digest, rows_by_ticker
from .paper_runtime import _read


def _symbol(ticker, market):
    pattern = r"[0-9]{6}\.K[QS]" if market == "KR" else r"[A-Z][A-Z0-9.\-]{0,11}"
    if not isinstance(ticker, str) or not re.fullmatch(pattern, ticker):
        raise ValueError("Unverified native ticker")
    return ticker[:6] if market == "KR" else ticker


@dataclass(frozen=True)
class DayUniverse:
    market: str
    account_scope: str
    session_date: date
    buys: frozenset
    owned: frozenset
    source_digest: str | None

    def permits(self, symbol, side, now, scope):
        return (scope == self.account_scope and now.astimezone(ZoneInfo(ZONES[self.market])).date() == self.session_date
                and (symbol in self.owned if side == "SELL" else side == "BUY" and symbol in self.buys))


def select(archive, source, market, session, now, scope, owned):
    """Choose 30 verified entry names. Long positions are separate, sell-only authority."""
    from .prism_candidate_runtime import SOURCE_ARTIFACTS, baseline

    zone = ZoneInfo(ZONES[market])
    opened, closed = instant(session.get("session_open")), instant(session.get("session_close"))
    if (opened is None or closed is None or not opened <= now < closed or session.get("source") != "exchange_calendars"
            or session.get("phase") != "regular" or session.get("is_open") is not True or not scope):
        raise ValueError("VTS daily universe requires an official current session and account scope")
    session_date = opened.astimezone(zone).date()
    held = {ticker for ticker, qty in owned.items() if qty > 0}
    held_symbols = frozenset(_symbol(ticker, market) for ticker in held)
    selected, identity = set(), None
    try:
        parent, _ = baseline(archive, source, market, now)
        original, manifest = _read(parent), _read(source / "run.json")
        active = original["active_universe"]
        selected = set(active["selected_tickers"])
        coverage = active["coverage"]
        selected_rows = set(rows_by_ticker(original))
        execution_rows = set(rows_by_ticker(manifest))
        produced = instant(active["asof"])
        original_started = instant(original["started_at"])
        if (len(active["selected_tickers"]) != 30 or len(selected) != 30 or selected != selected_rows
                or selected != execution_rows or active["market"].upper() != market
                or coverage.get("selection_complete") is not True or coverage.get("analysis_complete") is not True
                or coverage.get("analysis_expected_count") != 30 or coverage.get("analysis_successful_count") != 30
                or produced is None or original_started is None or not produced <= now
                or produced.astimezone(zone).date() != session_date or original_started.astimezone(zone).date() != session_date):
            raise ValueError("Incomplete or non-current active universe")
        document = _read(source / SOURCE_ARTIFACTS[1])
        instruments = [row["instrument"] for row in document["candidates"]]
        currency = "KRW" if market == "KR" else "USD"
        if (len(instruments) != 30 or {item["canonical_ticker"] for item in instruments} != selected
                or any((item.get("country"), item.get("currency")) != (market, currency) for item in instruments)):
            raise ValueError("Invalid native instrument scope")
        symbols = frozenset(_symbol(ticker, market) for ticker in selected)
        if len(symbols) != len(selected):
            raise ValueError("Duplicate native symbol")
        identity = digest(parent)
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        symbols, selected = frozenset(), set()
    policy = DayUniverse(market, scope, session_date, symbols, held_symbols, identity)
    return policy, selected | held
