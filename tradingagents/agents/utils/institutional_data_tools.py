from __future__ import annotations

import json
from typing import Annotated

from langchain_core.tools import tool

from tradingagents.dataflows.institutional import (
    CAP_CREDIT,
    CAP_DILIGENCE,
    CAP_ESTIMATES,
    CAP_FINANCIALS,
    CAP_PEERS,
    CAP_TRANSCRIPT,
    build_public_equity_intelligence_artifacts,
    build_public_equity_intelligence,
    render_capability_report,
    render_intelligence_markdown,
)


def _json_preview(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


@tool
def get_source_linked_financials(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
) -> str:
    """
    Retrieve source-linked public/optional institutional financial context.
    Defaults to free/public providers and uses imported paid-vendor JSON when available.
    """
    return render_capability_report(CAP_FINANCIALS, ticker, curr_date)


@tool
def get_estimates_consensus(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
) -> str:
    """
    Retrieve consensus estimates and revision context from imported institutional providers when available.
    """
    return render_capability_report(CAP_ESTIMATES, ticker, curr_date)


@tool
def get_earnings_event_pack(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
) -> str:
    """
    Build an earnings event pack covering actuals, guidance, consensus delta, transcripts, and next catalysts.
    """
    payload = build_public_equity_intelligence(ticker=ticker, curr_date=curr_date)
    return _json_preview(payload["earnings_event_pack"])


@tool
def get_transcript_evidence(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
) -> str:
    """
    Retrieve earnings-call or investor-event transcript evidence from Quartr/Daloopa/FactSet/LSEG/S&P imports.
    """
    return render_capability_report(CAP_TRANSCRIPT, ticker, curr_date)


@tool
def get_peer_comps(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
) -> str:
    """
    Retrieve peer comparison and valuation context from public data or imported FactSet/LSEG/S&P/PitchBook data.
    """
    return render_capability_report(CAP_PEERS, ticker, curr_date)


@tool
def get_credit_risk_context(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
) -> str:
    """
    Retrieve credit and downside-risk context, including Moody's imports when available.
    """
    return render_capability_report(CAP_CREDIT, ticker, curr_date)


@tool
def get_diligence_context(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
) -> str:
    """
    Retrieve diligence context from PitchBook, Datasite, Third Bridge, Hebbia, or local imported documents.
    """
    return render_capability_report(CAP_DILIGENCE, ticker, curr_date)


@tool
def get_public_equity_intelligence_summary(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
) -> str:
    """
    Summarize source quality, evidence coverage, earnings availability, and thesis readiness.
    """
    payload = build_public_equity_intelligence_artifacts(ticker=ticker, curr_date=curr_date)
    return render_intelligence_markdown(payload)
