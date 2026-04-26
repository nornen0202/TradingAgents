from __future__ import annotations

from pathlib import Path
from typing import Any

from .market_delta import build_market_delta, is_live_action_change, top_add_candidates, top_trim_candidates
from .news_delta import build_news_delta
from .sell_side_delta import build_sell_side_delta_candidates


def build_live_context_delta(
    *,
    run_dir: Path,
    manifest: dict[str, Any],
) -> dict[str, Any] | None:
    ticker_summaries = [item for item in (manifest.get("tickers") or []) if isinstance(item, dict)]
    if not ticker_summaries:
        return None

    ticker_deltas: list[dict[str, Any]] = []
    for ticker_summary in ticker_summaries:
        market_delta = build_market_delta(run_dir=run_dir, ticker_summary=ticker_summary)
        if not market_delta:
            continue
        news_delta = build_news_delta(
            ticker=str(ticker_summary.get("ticker") or ""),
            market=str(((manifest.get("settings") or {}).get("market")) or ""),
            as_of=str((ticker_summary.get("execution_update") or {}).get("execution_asof") or manifest.get("started_at") or ""),
            analysis_payload=ticker_summary,
        )
        market_delta["news_delta"] = news_delta
        if is_live_action_change(market_delta) or news_delta:
            ticker_deltas.append(market_delta)

    if not ticker_deltas:
        return None

    execution_asof_values = [
        str((item.get("execution_update") or {}).get("execution_asof") or "").strip()
        for item in ticker_summaries
        if isinstance(item.get("execution_update"), dict)
    ]
    execution_asof_values = [value for value in execution_asof_values if value]

    payload = {
        "as_of": execution_asof_values[0] if execution_asof_values else str(manifest.get("started_at") or ""),
        "base_run_id": str(manifest.get("run_id") or ""),
        "market": str(((manifest.get("settings") or {}).get("market")) or "").upper(),
        "ticker_deltas": ticker_deltas,
        "portfolio_delta": {
            "top_add_candidates": top_add_candidates(ticker_deltas),
            "top_trim_candidates": top_trim_candidates(ticker_deltas),
            "changed_since_base": any(
                str(item.get("base_action") or "").upper() != str(item.get("live_action") or "").upper()
                for item in ticker_deltas
            ),
        },
    }
    payload["sell_side_delta_candidates"] = build_sell_side_delta_candidates(live_context_delta=payload)
    return payload


def render_report_vs_live_delta_markdown(live_context_delta: dict[str, Any] | None) -> str:
    if not live_context_delta:
        return "\n".join(
            [
                "## 리포트 원판 vs 최신 장중 재분석",
                "",
                "- 최신 재분석 미수행",
                "- 이 리포트는 live execution override를 반영하지 않았습니다.",
            ]
        )

    ticker_deltas = live_context_delta.get("ticker_deltas") or []
    changed = [
        str(item.get("ticker") or "")
        for item in ticker_deltas
        if str(item.get("base_action") or "").upper() != str(item.get("live_action") or "").upper()
    ]
    reason_codes: list[str] = []
    for item in ticker_deltas:
        for code in item.get("reason_codes") or []:
            normalized = str(code).strip().upper()
            if normalized and normalized not in reason_codes:
                reason_codes.append(normalized)

    base_run_id = str(live_context_delta.get("base_run_id") or "-")
    base_date = base_run_id[:8]
    if len(base_date) == 8 and base_date.isdigit():
        base_date = f"{base_date[:4]}-{base_date[4:6]}-{base_date[6:]}"
    return "\n".join(
        [
            "## 리포트 원판 vs 최신 장중 재분석",
            "",
            f"- 원판 thesis 기준: {base_date}",
            f"- 최신 live context 기준: {live_context_delta.get('as_of') or '-'}",
            (
                f"- 결론이 달라진 종목: {', '.join(changed)}"
                if changed
                else "- 결론이 달라진 종목: 없음"
            ),
            (
                f"- 변경 이유: {', '.join(reason_codes[:6])}"
                if reason_codes
                else "- 변경 이유: live price/volume delta only"
            ),
        ]
    )
