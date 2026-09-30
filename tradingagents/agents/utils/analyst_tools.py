"""One tool contract for model binding and graph execution."""
from .core_stock_tools import get_stock_data, get_intraday_snapshot
from .technical_indicators_tools import get_indicators
from .fundamental_data_tools import get_fundamentals, get_balance_sheet, get_cashflow, get_income_statement
from .news_data_tools import get_company_news, get_macro_news, get_disclosures, get_insider_transactions, get_social_sentiment
from .macro_data_tools import get_macro_data
from .institutional_data_tools import (
    get_source_linked_financials, get_estimates_consensus, get_earnings_event_pack,
    get_transcript_evidence, get_peer_comps, get_credit_risk_context,
    get_diligence_context, get_public_equity_intelligence_summary,
)


ANALYST_TOOLS = {
    "market": (get_stock_data, get_indicators, get_intraday_snapshot),
    "social": (get_social_sentiment, get_company_news),
    "news": (get_macro_data, get_company_news, get_macro_news, get_disclosures),
    "fundamentals": (
        get_fundamentals, get_balance_sheet, get_cashflow, get_income_statement, get_insider_transactions,
        get_source_linked_financials, get_estimates_consensus, get_earnings_event_pack,
        get_transcript_evidence, get_peer_comps, get_credit_risk_context,
        get_diligence_context, get_public_equity_intelligence_summary,
    ),
}


def analyst_tools(kind: str) -> list:
    return list(ANALYST_TOOLS[kind])
