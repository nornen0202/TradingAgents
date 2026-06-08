from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .api_keys import get_api_key
from .config import get_config
from .institutional_models import (
    EarningsEventPack,
    EvidenceItem,
    ProviderDefinition,
    SourceRef,
    ThesisTracker,
)
from .interface import route_to_vendor
from .vendor_exceptions import VendorConfigurationError, VendorTransientError


CAP_FINANCIALS = "financials"
CAP_KPI = "kpi"
CAP_ESTIMATES = "estimates"
CAP_TRANSCRIPT = "transcript"
CAP_FILINGS = "filings"
CAP_CREDIT = "credit"
CAP_PEERS = "peers"
CAP_DILIGENCE = "diligence"
CAP_MARKET_DATA = "market_data"
CAP_MACRO = "macro"
CAP_SOCIAL = "social"

INSTITUTIONAL_CAPABILITIES = (
    CAP_FINANCIALS,
    CAP_KPI,
    CAP_ESTIMATES,
    CAP_TRANSCRIPT,
    CAP_FILINGS,
    CAP_CREDIT,
    CAP_PEERS,
    CAP_DILIGENCE,
    CAP_MARKET_DATA,
    CAP_MACRO,
    CAP_SOCIAL,
)

INSTITUTIONAL_PROVIDERS: tuple[ProviderDefinition, ...] = (
    ProviderDefinition("yfinance", "Yahoo Finance", (CAP_FINANCIALS, CAP_MARKET_DATA, CAP_SOCIAL), "free", priority=10),
    ProviderDefinition("alpha_vantage", "Alpha Vantage", (CAP_FINANCIALS, CAP_MARKET_DATA, CAP_MACRO), "free", ("ALPHA_VANTAGE_API_KEY",), 12),
    ProviderDefinition("opendart", "OpenDART", (CAP_FILINGS,), "free", ("OPENDART_API_KEY",), 14),
    ProviderDefinition("naver", "Naver", (CAP_SOCIAL,), "free", ("NAVER_CLIENT_ID", "NAVER_CLIENT_SECRET"), 16),
    ProviderDefinition("ecos", "Bank of Korea ECOS", (CAP_MACRO,), "free", priority=18),
    ProviderDefinition("krx", "KRX Open API", (CAP_MARKET_DATA, CAP_FILINGS), "free", priority=20),
    ProviderDefinition("sec_edgar", "SEC EDGAR", (CAP_FILINGS,), "free", priority=22),
    ProviderDefinition("kis", "Korea Investment Securities", (CAP_MARKET_DATA,), "free", ("KIS_APP_KEY", "KIS_APP_SECRET"), 24),
    ProviderDefinition("massive", "Massive/Polygon", (CAP_MARKET_DATA,), "free", ("MASSIVE_API_KEY",), 26),
    ProviderDefinition("alpaca", "Alpaca", (CAP_MARKET_DATA,), "free", ("ALPACA_API_KEY_ID", "ALPACA_SECRET_KEY"), 28),
    ProviderDefinition("daloopa", "Daloopa", (CAP_FINANCIALS, CAP_KPI, CAP_TRANSCRIPT, CAP_PEERS), "paid", ("DALOOPA_API_KEY",), 40),
    ProviderDefinition("quartr", "Quartr", (CAP_TRANSCRIPT, CAP_FILINGS, CAP_KPI), "paid", ("QUARTR_API_KEY",), 42),
    ProviderDefinition("factset", "FactSet", (CAP_FINANCIALS, CAP_ESTIMATES, CAP_TRANSCRIPT, CAP_PEERS), "paid", ("FACTSET_API_KEY", "FACTSET_USERNAME", "FACTSET_PASSWORD"), 44),
    ProviderDefinition("lseg", "LSEG Workspace", (CAP_FINANCIALS, CAP_ESTIMATES, CAP_TRANSCRIPT, CAP_PEERS, CAP_MARKET_DATA), "paid", ("LSEG_API_KEY", "LSEG_APP_KEY"), 46),
    ProviderDefinition("spglobal", "S&P Global", (CAP_FINANCIALS, CAP_ESTIMATES, CAP_FILINGS, CAP_PEERS), "paid", ("SPGLOBAL_API_KEY", "SP_GLOBAL_API_KEY"), 48),
    ProviderDefinition("moodys", "Moody's", (CAP_CREDIT,), "paid", ("MOODYS_API_KEY",), 50),
    ProviderDefinition("morningstar", "Morningstar", (CAP_FINANCIALS, CAP_ESTIMATES, CAP_PEERS), "paid", ("MORNINGSTAR_API_KEY",), 52),
    ProviderDefinition("pitchbook", "PitchBook", (CAP_PEERS, CAP_DILIGENCE), "paid", ("PITCHBOOK_API_KEY",), 60),
    ProviderDefinition("datasite", "Datasite", (CAP_DILIGENCE,), "paid", ("DATASITE_API_KEY", "DATASITE_CLIENT_ID"), 62),
    ProviderDefinition("hebbia", "Hebbia", (CAP_DILIGENCE, CAP_FILINGS), "paid", ("HEBBIA_API_KEY",), 64),
    ProviderDefinition("third_bridge", "Third Bridge", (CAP_DILIGENCE,), "paid", ("THIRD_BRIDGE_API_KEY",), 66),
)


def provider_catalog() -> list[dict[str, Any]]:
    data_dir = _institutional_data_dir()
    return [
        provider.to_dict(
            configured=_provider_configured(provider),
            imported=_has_imported_payload(provider.id, data_dir=data_dir),
        )
        for provider in sorted(INSTITUTIONAL_PROVIDERS, key=lambda item: item.priority)
    ]


def providers_for_capability(capability: str) -> list[dict[str, Any]]:
    normalized = str(capability or "").strip().lower()
    return [
        provider
        for provider in provider_catalog()
        if normalized in {str(item).lower() for item in provider.get("capabilities", [])}
    ]


def route_to_institutional_provider(
    capability: str,
    ticker: str,
    curr_date: str | None = None,
    *,
    provider_chain: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Return the best available payload for an institutional capability.

    Paid vendors are optional. Their data is consumed from JSON exports or live
    adapters only when credentials are present. This keeps the default path
    free/public-data first and prevents missing licenses from breaking a run.
    """
    normalized_capability = str(capability or "").strip().lower()
    if normalized_capability not in INSTITUTIONAL_CAPABILITIES:
        raise ValueError(f"Unsupported institutional capability: {capability}")

    providers = _ordered_provider_chain(normalized_capability, provider_chain)
    for provider in providers:
        imported = _load_imported_payload(provider.id, ticker, normalized_capability)
        if imported:
            return _provider_payload(
                provider=provider,
                capability=normalized_capability,
                ticker=ticker,
                curr_date=curr_date,
                status="success",
                mode="imported",
                payload=imported,
            )

    for provider in providers:
        if provider.access != "free":
            continue
        payload = _fetch_free_capability(provider.id, normalized_capability, ticker, curr_date)
        if payload.get("status") == "success":
            return _provider_payload(
                provider=provider,
                capability=normalized_capability,
                ticker=ticker,
                curr_date=curr_date,
                status="success",
                mode="live_free",
                payload=payload,
            )

    configured_paid = [
        provider.id
        for provider in providers
        if provider.access == "paid" and _provider_configured(provider)
    ]
    return {
        "ticker": ticker,
        "capability": normalized_capability,
        "status": "unavailable",
        "mode": "none",
        "provider": None,
        "configured_paid_providers": configured_paid,
        "warnings": [
            "No free/public or imported institutional payload was available.",
            "Paid vendor adapters are optional and require credentials or exported JSON fixtures.",
        ],
    }


def build_public_equity_intelligence(
    *,
    ticker: str,
    curr_date: str,
    analysis_date: str | None = None,
    final_state: dict[str, Any] | None = None,
    tool_events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    asof = analysis_date or curr_date
    final_state = final_state or {}
    tool_events = tool_events or []
    imported_payloads = _load_all_imported_payloads(ticker)
    source_refs = _source_refs_from_tool_events(ticker=ticker, asof=asof, tool_events=tool_events)
    source_refs.extend(_source_refs_from_final_state(ticker=ticker, asof=asof, final_state=final_state))
    source_refs.extend(_source_refs_from_imports(imported_payloads))

    evidence_items = _evidence_from_final_state(ticker=ticker, asof=asof, final_state=final_state)
    evidence_items.extend(_evidence_from_imports(ticker=ticker, imported_payloads=imported_payloads))
    source_quality_score = _source_quality_score(
        source_refs=source_refs,
        evidence_items=evidence_items,
        imported_payloads=imported_payloads,
        tool_events=tool_events,
    )
    earnings_event_pack = _earnings_event_pack(
        ticker=ticker,
        asof=asof,
        imported_payloads=imported_payloads,
        source_refs=source_refs,
    )
    thesis_tracker = _thesis_tracker(
        ticker=ticker,
        asof=asof,
        final_state=final_state,
        evidence_items=evidence_items,
        source_quality_score=source_quality_score,
    )
    coverage = _coverage_summary(
        imported_payloads=imported_payloads,
        source_refs=source_refs,
        tool_events=tool_events,
        earnings_event_pack=earnings_event_pack,
    )
    return {
        "ticker": ticker,
        "asof": asof,
        "source_quality_score": source_quality_score,
        "source_cohort": _source_cohort(coverage),
        "coverage": coverage,
        "provider_catalog": provider_catalog(),
        "source_refs": [source.to_dict() for source in source_refs],
        "evidence_ledger": [item.to_dict() for item in evidence_items],
        "earnings_event_pack": earnings_event_pack.to_dict(),
        "thesis_tracker": thesis_tracker.to_dict(),
        "warnings": _intelligence_warnings(coverage, source_quality_score),
    }


def build_public_equity_intelligence_artifacts(
    *,
    ticker: str,
    curr_date: str,
    analysis_date: str | None = None,
    final_state: dict[str, Any] | None = None,
    tool_events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    intelligence = build_public_equity_intelligence(
        ticker=ticker,
        curr_date=curr_date,
        analysis_date=analysis_date,
        final_state=final_state,
        tool_events=tool_events,
    )
    return {
        "summary": {
            "ticker": ticker,
            "asof": intelligence["asof"],
            "source_quality_score": intelligence["source_quality_score"],
            "source_cohort": intelligence["source_cohort"],
            "coverage": intelligence["coverage"],
            "thesis_status": intelligence["thesis_tracker"]["status"],
            "security_readiness": intelligence["thesis_tracker"]["security_readiness"],
            "estimate_revision_direction": intelligence["coverage"].get("estimate_revision_direction"),
            "transcript_available": intelligence["coverage"].get("transcript_available", False),
            "warnings": intelligence["warnings"],
        },
        "source_quality": {
            key: intelligence[key]
            for key in ("ticker", "asof", "source_quality_score", "source_cohort", "coverage", "provider_catalog", "source_refs", "warnings")
        },
        "evidence_ledger": {
            "ticker": ticker,
            "asof": intelligence["asof"],
            "items": intelligence["evidence_ledger"],
            "source_quality_score": intelligence["source_quality_score"],
        },
        "earnings_event_pack": intelligence["earnings_event_pack"],
        "thesis_tracker": intelligence["thesis_tracker"],
        "full": intelligence,
    }


def render_capability_report(capability: str, ticker: str, curr_date: str | None = None) -> str:
    payload = route_to_institutional_provider(capability, ticker, curr_date)
    provider = payload.get("provider") or {}
    lines = [
        f"## Institutional capability: {capability}",
        f"- Ticker: {ticker}",
        f"- Status: {payload.get('status')}",
        f"- Mode: {payload.get('mode')}",
        f"- Provider: {provider.get('display_name') or provider.get('id') or 'unavailable'}",
    ]
    warnings = payload.get("warnings") or []
    if warnings:
        lines.append("- Warnings: " + "; ".join(str(item) for item in warnings))
    data = payload.get("payload")
    if isinstance(data, dict):
        preview = json.dumps(_truncate_payload(data), ensure_ascii=False, indent=2)
        lines.append("\n```json\n" + preview + "\n```")
    elif data:
        lines.append(str(data)[:3000])
    return "\n".join(lines)


def render_intelligence_markdown(payload: dict[str, Any]) -> str:
    summary = payload.get("summary") if "summary" in payload else payload
    coverage = summary.get("coverage") if isinstance(summary.get("coverage"), dict) else {}
    warnings = summary.get("warnings") or []
    lines = [
        "## Public Equity Intelligence",
        f"- Source quality: {summary.get('source_quality_score', 0):.2f}",
        f"- Source cohort: {summary.get('source_cohort') or 'unknown'}",
        f"- Thesis status: {summary.get('thesis_status') or 'unknown'}",
        f"- Security readiness: {summary.get('security_readiness') or 'unknown'}",
        f"- Transcript available: {bool(coverage.get('transcript_available'))}",
        f"- Estimate revision: {coverage.get('estimate_revision_direction') or 'unknown'}",
    ]
    if warnings:
        lines.append("- Warnings: " + "; ".join(str(item) for item in warnings))
    return "\n".join(lines)


def _ordered_provider_chain(capability: str, provider_chain: list[str] | tuple[str, ...] | None) -> list[ProviderDefinition]:
    by_id = {provider.id: provider for provider in INSTITUTIONAL_PROVIDERS}
    providers = [provider for provider in INSTITUTIONAL_PROVIDERS if capability in provider.capabilities]
    if provider_chain:
        ordered: list[ProviderDefinition] = []
        for provider_id in provider_chain:
            provider = by_id.get(str(provider_id).strip().lower())
            if provider and capability in provider.capabilities:
                ordered.append(provider)
        ordered_ids = {provider.id for provider in ordered}
        ordered.extend(provider for provider in providers if provider.id not in ordered_ids)
        providers = ordered
    return sorted(providers, key=lambda item: item.priority)


def _provider_payload(
    *,
    provider: ProviderDefinition,
    capability: str,
    ticker: str,
    curr_date: str | None,
    status: str,
    mode: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "ticker": ticker,
        "asof": curr_date,
        "capability": capability,
        "status": status,
        "mode": mode,
        "provider": provider.to_dict(
            configured=_provider_configured(provider),
            imported=_load_imported_payload(provider.id, ticker, capability) is not None,
        ),
        "payload": payload,
        "warnings": payload.get("warnings", []) if isinstance(payload, dict) else [],
    }


def _fetch_free_capability(provider_id: str, capability: str, ticker: str, curr_date: str | None) -> dict[str, Any]:
    try:
        if capability == CAP_FINANCIALS and provider_id in {"yfinance", "alpha_vantage"}:
            return {
                "status": "success",
                "raw": route_to_vendor("get_fundamentals", ticker, curr_date or datetime.now().date().isoformat()),
            }
        if capability == CAP_FILINGS and provider_id == "opendart":
            end_date = curr_date or datetime.now().date().isoformat()
            start_date = _date_minus_days(end_date, 365)
            return {
                "status": "success",
                "raw": route_to_vendor("get_disclosures", ticker, start_date, end_date),
            }
        if capability == CAP_MARKET_DATA and provider_id in {"yfinance", "alpha_vantage"}:
            end_date = curr_date or datetime.now().date().isoformat()
            start_date = _date_minus_days(end_date, 30)
            return {
                "status": "success",
                "raw": route_to_vendor("get_stock_data", ticker, start_date, end_date),
            }
        if capability == CAP_SOCIAL and provider_id in {"yfinance", "naver"}:
            end_date = curr_date or datetime.now().date().isoformat()
            start_date = _date_minus_days(end_date, 30)
            return {
                "status": "success",
                "raw": route_to_vendor("get_social_sentiment", ticker, start_date, end_date),
            }
        if capability == CAP_MACRO and provider_id in {"alpha_vantage", "ecos", "yfinance"}:
            return {
                "status": "success",
                "raw": route_to_vendor("get_macro_news", curr_date or datetime.now().date().isoformat(), 7, 10),
            }
    except (VendorConfigurationError, VendorTransientError, RuntimeError, ValueError) as exc:
        return {"status": "unavailable", "warnings": [str(exc)]}
    return {"status": "unavailable", "warnings": [f"{provider_id} has no live adapter for {capability}."]}


def _provider_configured(provider: ProviderDefinition) -> bool:
    if not provider.credential_envs:
        return provider.access == "free"
    return any(get_api_key(env_name) for env_name in provider.credential_envs)


def _institutional_data_dir() -> Path:
    config = get_config()
    configured = os.getenv("TRADINGAGENTS_INSTITUTIONAL_DATA_DIR") or str(config.get("institutional_data_dir") or "").strip()
    if configured:
        return Path(configured).expanduser()
    return Path(config.get("project_dir") or Path.cwd()) / "data" / "institutional"


def _safe_ticker(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "").strip().upper()).strip("_")


def _import_candidate_paths(provider_id: str, ticker: str, capability: str | None = None) -> list[Path]:
    base = _institutional_data_dir()
    safe = _safe_ticker(ticker)
    provider = str(provider_id).strip().lower()
    paths = [
        base / provider / safe / "institutional.json",
        base / provider / f"{safe}.json",
        base / safe / f"{provider}.json",
    ]
    if capability:
        cap = str(capability).strip().lower()
        paths = [
            base / provider / safe / f"{cap}.json",
            base / provider / f"{safe}_{cap}.json",
            base / safe / f"{provider}_{cap}.json",
            *paths,
        ]
    return paths


def _load_imported_payload(provider_id: str, ticker: str, capability: str | None = None) -> dict[str, Any] | None:
    for path in _import_candidate_paths(provider_id, ticker, capability):
        payload = _load_json_file(path)
        if not payload:
            continue
        payload.setdefault("_import_provider", provider_id)
        payload.setdefault("_import_path", str(path))
        return payload
    return None


def _load_all_imported_payloads(ticker: str) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for provider in INSTITUTIONAL_PROVIDERS:
        for capability in (None, *provider.capabilities):
            payload = _load_imported_payload(provider.id, ticker, capability)
            if not payload:
                continue
            import_path = str(payload.get("_import_path") or "")
            if import_path in seen_paths:
                continue
            seen_paths.add(import_path)
            payloads.append(payload)
    return payloads


def _has_imported_payload(provider_id: str, *, data_dir: Path | None = None) -> bool:
    root = data_dir or _institutional_data_dir()
    provider_root = root / str(provider_id).strip().lower()
    return provider_root.exists() and any(provider_root.rglob("*.json"))


def _load_json_file(path: Path) -> dict[str, Any] | None:
    try:
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
            return payload if isinstance(payload, dict) else None
    except Exception:
        return None
    return None


def _source_refs_from_tool_events(*, ticker: str, asof: str, tool_events: list[dict[str, Any]]) -> list[SourceRef]:
    refs: list[SourceRef] = []
    for event in tool_events:
        if event.get("status") not in {"success", "fallback"}:
            continue
        vendor = str(event.get("vendor") or "").strip()
        method = str(event.get("method") or "").strip()
        if not vendor or not method:
            continue
        refs.append(
            SourceRef(
                provider=vendor,
                title=f"{method} tool result for {ticker}",
                document_type="tool_result",
                date=asof,
                section=method,
                confidence=0.55 if event.get("status") == "success" else 0.25,
            )
        )
    return refs


def _source_refs_from_final_state(*, ticker: str, asof: str, final_state: dict[str, Any]) -> list[SourceRef]:
    refs: list[SourceRef] = []
    report_map = {
        "fundamentals_report": "fundamentals analyst report",
        "news_report": "news analyst report",
        "market_report": "market analyst report",
        "sentiment_report": "sentiment analyst report",
    }
    for key, title in report_map.items():
        if str(final_state.get(key) or "").strip():
            refs.append(
                SourceRef(
                    provider="TradingAgents",
                    title=f"{title} for {ticker}",
                    document_type="agent_report",
                    date=asof,
                    section=key,
                    confidence=0.45,
                )
            )
    return refs


def _source_refs_from_imports(imported_payloads: list[dict[str, Any]]) -> list[SourceRef]:
    refs: list[SourceRef] = []
    for payload in imported_payloads:
        raw_refs = payload.get("source_refs") or payload.get("sources") or []
        refs.extend(SourceRef.from_mapping(item) for item in raw_refs if isinstance(item, dict))
        provider = str(payload.get("_import_provider") or payload.get("provider") or "").strip()
        import_path = str(payload.get("_import_path") or "").strip()
        if provider and import_path:
            refs.append(
                SourceRef(
                    provider=provider,
                    title=Path(import_path).name,
                    document_type="vendor_import",
                    url=import_path,
                    confidence=0.7,
                )
            )
    return refs


def _evidence_from_final_state(*, ticker: str, asof: str, final_state: dict[str, Any]) -> list[EvidenceItem]:
    items: list[EvidenceItem] = []
    for key, label in (
        ("fundamentals_report", "Fundamental thesis evidence generated"),
        ("news_report", "Recent news evidence generated"),
        ("market_report", "Market structure evidence generated"),
        ("sentiment_report", "Sentiment evidence generated"),
    ):
        content = str(final_state.get(key) or "").strip()
        if not content:
            continue
        items.append(
            EvidenceItem(
                claim=label,
                ticker=ticker,
                source_refs=(
                    SourceRef(
                        provider="TradingAgents",
                        title=f"{key} for {ticker}",
                        document_type="agent_report",
                        date=asof,
                        section=key,
                        confidence=0.45,
                    ),
                ),
                direction="context",
                quality=0.45,
            )
        )
    return items


def _evidence_from_imports(*, ticker: str, imported_payloads: list[dict[str, Any]]) -> list[EvidenceItem]:
    items: list[EvidenceItem] = []
    for payload in imported_payloads:
        raw_items = payload.get("evidence_ledger") or payload.get("evidence") or payload.get("items") or []
        items.extend(EvidenceItem.from_mapping(item, ticker=ticker) for item in raw_items if isinstance(item, dict))
    return items


def _source_quality_score(
    *,
    source_refs: list[SourceRef],
    evidence_items: list[EvidenceItem],
    imported_payloads: list[dict[str, Any]],
    tool_events: list[dict[str, Any]],
) -> float:
    successful_tools = sum(1 for event in tool_events if event.get("status") == "success")
    imported_bonus = min(len(imported_payloads) * 0.08, 0.24)
    score = 0.0
    score += min(len(source_refs), 12) / 12 * 0.35
    score += min(len(evidence_items), 12) / 12 * 0.25
    score += min(successful_tools, 6) / 6 * 0.16
    score += imported_bonus
    if any(item.quality >= 0.8 for item in evidence_items):
        score += 0.05
    return round(max(0.0, min(score, 1.0)), 4)


def _earnings_event_pack(
    *,
    ticker: str,
    asof: str,
    imported_payloads: list[dict[str, Any]],
    source_refs: list[SourceRef],
) -> EarningsEventPack:
    for payload in imported_payloads:
        raw = payload.get("earnings_event_pack") or payload.get("earnings") or {}
        if not isinstance(raw, dict) or not raw:
            continue
        raw_sources = raw.get("source_refs") or raw.get("sources") or []
        refs = tuple(SourceRef.from_mapping(item) for item in raw_sources if isinstance(item, dict))
        return EarningsEventPack(
            ticker=ticker,
            asof=str(raw.get("asof") or asof),
            status=str(raw.get("status") or "available_imported"),
            actuals=dict(raw.get("actuals") or {}),
            guidance=dict(raw.get("guidance") or {}),
            consensus_delta=dict(raw.get("consensus_delta") or {}),
            transcript_available=bool(raw.get("transcript_available")),
            transcript_highlights=tuple(str(item) for item in (raw.get("transcript_highlights") or [])),
            next_catalysts=tuple(str(item) for item in (raw.get("next_catalysts") or [])),
            source_refs=refs,
            warnings=tuple(str(item) for item in (raw.get("warnings") or [])),
        )
    return EarningsEventPack(
        ticker=ticker,
        asof=asof,
        status="unavailable",
        source_refs=tuple(source_refs[:3]),
        warnings=(
            "No earnings event pack import was found.",
            "Add Quartr, Daloopa, FactSet, LSEG, or S&P exports to enable transcript and consensus analysis.",
        ),
    )


def _thesis_tracker(
    *,
    ticker: str,
    asof: str,
    final_state: dict[str, Any],
    evidence_items: list[EvidenceItem],
    source_quality_score: float,
) -> ThesisTracker:
    decision_text = str(final_state.get("final_trade_decision") or "").upper()
    weakened = [item.claim for item in evidence_items if item.direction.lower() in {"challenge", "weaken", "negative"}]
    strengthened = [item.claim for item in evidence_items if item.direction.lower() in {"support", "strengthen", "positive"}]
    status = "insufficient_evidence"
    if source_quality_score >= 0.65:
        status = "strengthened" if strengthened and not weakened else "mixed" if strengthened and weakened else "supported"
    elif source_quality_score >= 0.35:
        status = "developing"
    if "SELL" in decision_text or "UNDERWEIGHT" in decision_text:
        status = "weakened" if source_quality_score >= 0.35 else status
    security_readiness = "watch_only"
    if source_quality_score >= 0.7 and status in {"strengthened", "supported"}:
        security_readiness = "candidate_ready"
    elif source_quality_score >= 0.45:
        security_readiness = "conditional_only"
    return ThesisTracker(
        ticker=ticker,
        asof=asof,
        status=status,
        security_readiness=security_readiness,
        pillars=("business_quality", "event_risk", "valuation_or_setup"),
        falsifiers=("earnings_quality_breakdown", "guidance_cut", "thesis_invalidating_price_action"),
        strengthened_by=tuple(strengthened[:8]),
        weakened_by=tuple(weakened[:8]),
        evidence_count=len(evidence_items),
        source_quality_score=source_quality_score,
    )


def _coverage_summary(
    *,
    imported_payloads: list[dict[str, Any]],
    source_refs: list[SourceRef],
    tool_events: list[dict[str, Any]],
    earnings_event_pack: EarningsEventPack,
) -> dict[str, Any]:
    imported_providers = sorted(
        {str(payload.get("_import_provider") or payload.get("provider") or "").strip() for payload in imported_payloads if str(payload.get("_import_provider") or payload.get("provider") or "").strip()}
    )
    public_providers = sorted(
        {
            str(event.get("vendor") or "").strip()
            for event in tool_events
            if event.get("status") == "success" and str(event.get("vendor") or "").strip()
        }
    )
    estimate_revision_direction = "unknown"
    for payload in imported_payloads:
        estimate_revision_direction = str(
            payload.get("estimate_revision_direction")
            or ((payload.get("estimates") or {}).get("revision_direction") if isinstance(payload.get("estimates"), dict) else "")
            or estimate_revision_direction
        )
        if estimate_revision_direction != "unknown":
            break
    return {
        "source_ref_count": len(source_refs),
        "successful_tool_provider_count": len(public_providers),
        "public_providers": public_providers,
        "institutional_import_providers": imported_providers,
        "paid_provider_imported": bool(imported_providers),
        "transcript_available": earnings_event_pack.transcript_available,
        "earnings_event_status": earnings_event_pack.status,
        "estimate_revision_direction": estimate_revision_direction,
    }


def _source_cohort(coverage: dict[str, Any]) -> str:
    has_public = bool(coverage.get("public_providers"))
    has_paid = bool(coverage.get("paid_provider_imported"))
    if has_public and has_paid:
        return "public_plus_institutional_imports"
    if has_paid:
        return "institutional_imports"
    if has_public:
        return "public_only"
    return "analysis_only"


def _intelligence_warnings(coverage: dict[str, Any], score: float) -> list[str]:
    warnings: list[str] = []
    if score < 0.35:
        warnings.append("source_quality_below_review_threshold")
    if not coverage.get("transcript_available"):
        warnings.append("transcript_not_available")
    if coverage.get("estimate_revision_direction") in {None, "", "unknown"}:
        warnings.append("consensus_estimates_not_available")
    return warnings


def _truncate_payload(value: Any, *, max_chars: int = 2500) -> Any:
    text = json.dumps(value, ensure_ascii=False, default=str)
    if len(text) <= max_chars:
        return value
    return {"preview": text[:max_chars], "truncated": True}


def _date_minus_days(date_text: str, days: int) -> str:
    try:
        parsed = datetime.strptime(str(date_text), "%Y-%m-%d").date()
    except ValueError:
        parsed = datetime.now().date()
    return (parsed - timedelta(days=days)).isoformat()
