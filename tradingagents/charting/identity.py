"""Reject proven wrong-company research without borrowing future evidence."""

import json
from pathlib import Path

from tradingagents.agents.utils.instrument_resolver import resolve_instrument
from .bars import instant


def research_company_matches(directory, ticker, *, cutoff, market=None):
    directory = Path(directory).resolve()
    state_path = directory / "final_state.json"
    analysis_path = directory / "analysis.json"
    # Old archive-only chart captures may have no graph state. Their existing
    # availability rules remain intact; this gate rejects proven mismatches.
    if not state_path.exists() or not analysis_path.exists():
        return True
    if not state_path.resolve().is_relative_to(
        directory
    ) or not analysis_path.resolve().is_relative_to(directory):
        return False
    try:
        analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
        known = instant(analysis.get("finished_at"))
        if known is None or known > cutoff:
            return True  # Future/undated research cannot change a past view.
        state = json.loads(state_path.read_text(encoding="utf-8"))
        observed = state.get("company_of_interest")
        if observed is None:
            return True  # Legacy state without an identity is not a proof.
        return observed == resolve_instrument(ticker, market=market).primary_symbol
    except (OSError, ValueError, TypeError, AttributeError):
        return False
