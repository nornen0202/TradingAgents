# TradingAgents/graph/signal_processing.py

from tradingagents.schemas import parse_structured_decision
from tradingagents.schemas.decision_status import is_unvalidated_decision


class SignalProcessor:
    """Processes structured trading signals deterministically."""

    def __init__(self):
        pass

    def process_signal(self, full_signal: str) -> str:
        decision = parse_structured_decision(full_signal)
        if is_unvalidated_decision(decision):
            return "REVIEW"
        return decision.rating.value
