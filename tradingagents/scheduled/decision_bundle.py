from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from tradingagents.presentation import (
    present_account_action,
    present_execution_state,
    present_execution_timing,
    present_reason_code,
    present_strategy_category,
    sanitize_investor_text,
)


DECISION_BUNDLE_VERSION = 2
DEFAULT_MIN_FRESH_ROW_RATIO = 0.80
CURRENT_FRESHNESS = {"LIVE_CHECKPOINT", "CURRENT_SESSION", "CURRENT_RUN_FRESH", "FRESH"}
CONDITIONAL_FRESHNESS = {*CURRENT_FRESHNESS, "DELAYED_CHECKPOINT"}
CURRENT_ELIGIBILITY = {
    "LIVE_EXECUTION_READY",
    "ASOF_EXECUTION_READY",
    "LIVE_EXECUTION_OK",
    "ACTIONABLE",
    "ACTIONABLE_NOW",
    "PILOT_READY",
}
CONDITIONAL_ELIGIBILITY = {*CURRENT_ELIGIBILITY, "DELAYED_ANALYSIS_ONLY"}

_STRATEGY_ORDER = {
    "SELL": 0,
    "REDUCE": 1,
    "BUY_NOW": 2,
    "BUY_ON_CONFIRMATION": 3,
    "HOLD": 4,
    "WAIT_CLOSE": 5,
    "WAIT": 6,
    "AVOID": 7,
    "DATA_CHECK": 8,
}

_US_SECTOR_ETF = {
    "technology": "XLK",
    "information technology": "XLK",
    "semiconductor": "SOXX",
    "semiconductors": "SOXX",
    "financial": "XLF",
    "financials": "XLF",
    "industrial": "XLI",
    "industrials": "XLI",
    "healthcare": "XLV",
    "health care": "XLV",
    "consumer discretionary": "XLY",
    "consumer staples": "XLP",
    "energy": "XLE",
    "utilities": "XLU",
    "real estate": "XLRE",
    "communication services": "XLC",
    "materials": "XLB",
}


def build_and_write_decision_bundle(
    *,
    run_dir: Path,
    manifest: dict[str, Any],
    benchmark_loader: Callable[[set[str]], dict[str, dict[str, Any]]] | None = None,
    min_fresh_row_ratio: float = DEFAULT_MIN_FRESH_ROW_RATIO,
) -> dict[str, Any]:
    run_dir = Path(run_dir)
    context = _load_json(run_dir / "chatgpt_execution_context.json")
    portfolio_artifacts = ((manifest.get("portfolio") or {}).get("artifacts") or {})
    candidates_payload = _load_artifact_json(run_dir, portfolio_artifacts.get("portfolio_candidates_json"))
    recommendation_payload = _load_artifact_json(run_dir, portfolio_artifacts.get("portfolio_report_json"))
    bundle = build_decision_bundle(
        run_id=str(manifest.get("run_id") or run_dir.name),
        market=str(((manifest.get("settings") or {}).get("market") or manifest.get("market") or "")).upper(),
        generated_at=datetime.now().astimezone().isoformat(),
        analysis_source_run_id=str(manifest.get("overlay_source_run_id") or manifest.get("run_id") or run_dir.name),
        ticker_summaries=list(manifest.get("tickers") or []),
        execution_context=context,
        portfolio_candidates=list(candidates_payload.get("candidates") or []),
        portfolio_actions=list(recommendation_payload.get("actions") or []),
        benchmark_loader=benchmark_loader,
        min_fresh_row_ratio=min_fresh_row_ratio,
    )
    json_path = run_dir / "decision_bundle_v2.json"
    markdown_path = run_dir / "strategy_table_ko.md"
    status_path = run_dir / "decision_bundle_status.json"
    _write_json(json_path, bundle)
    markdown_path.write_text(render_strategy_table_markdown(bundle), encoding="utf-8")
    _write_json(
        status_path,
        {
            "artifact_type": "decision_bundle_status",
            "version": DECISION_BUNDLE_VERSION,
            "run_id": bundle["run_id"],
            "market": bundle["market"],
            "generated_at": bundle["generated_at"],
            "decision_ready": bundle["quality"]["decision_ready"],
            "quality": bundle["quality"],
            "bundle_sha256": _sha256_file(json_path),
        },
    )
    return {
        "version": DECISION_BUNDLE_VERSION,
        "decision_ready": bundle["quality"]["decision_ready"],
        "conditional_strategy_ready": bundle["quality"]["conditional_strategy_ready"],
        "quality_label_ko": bundle["quality"]["quality_label_ko"],
        "fresh_row_ratio": bundle["quality"]["fresh_row_ratio"],
        "conditional_row_ratio": bundle["quality"]["conditional_row_ratio"],
        "strategy_counts": bundle["summary"]["strategy_counts"],
        "top_strategy_rows": select_investor_strategy_rows(bundle["strategy_table"]),
        "artifacts": {
            "decision_bundle_v2_json": json_path.name,
            "strategy_table_ko_md": markdown_path.name,
            "decision_bundle_status_json": status_path.name,
        },
    }


def build_decision_bundle(
    *,
    run_id: str,
    market: str,
    generated_at: str,
    analysis_source_run_id: str,
    ticker_summaries: list[dict[str, Any]],
    execution_context: dict[str, Any] | None = None,
    portfolio_candidates: list[dict[str, Any]] | None = None,
    portfolio_actions: list[dict[str, Any]] | None = None,
    benchmark_loader: Callable[[set[str]], dict[str, dict[str, Any]]] | None = None,
    min_fresh_row_ratio: float = DEFAULT_MIN_FRESH_ROW_RATIO,
) -> dict[str, Any]:
    context = execution_context or {}
    candidates = portfolio_candidates or []
    actions = portfolio_actions or []
    summary_by_ticker = {
        _ticker_key(item.get("ticker")): item
        for item in ticker_summaries
        if _ticker_key(item.get("ticker"))
    }
    context_by_ticker = {
        _ticker_key(item.get("ticker")): item
        for item in (context.get("tickers") or [])
        if isinstance(item, dict) and _ticker_key(item.get("ticker"))
    }
    candidate_by_ticker = {
        _ticker_key(item.get("canonical_ticker") or item.get("ticker")): item
        for item in candidates
        if _ticker_key(item.get("canonical_ticker") or item.get("ticker"))
    }
    action_by_ticker = {
        _ticker_key(item.get("canonical_ticker") or item.get("ticker")): item
        for item in actions
        if _ticker_key(item.get("canonical_ticker") or item.get("ticker"))
    }
    tickers = sorted(set(summary_by_ticker) | set(context_by_ticker) | set(candidate_by_ticker) | set(action_by_ticker))

    benchmark_symbols = _benchmark_symbols(
        market=market,
        tickers=tickers,
        candidates=candidate_by_ticker,
    )
    loader = benchmark_loader or _load_benchmark_context
    benchmark_context: dict[str, dict[str, Any]] = {}
    if context_by_ticker and benchmark_symbols:
        try:
            benchmark_context = loader(benchmark_symbols)
        except Exception:
            benchmark_context = {}

    rows = [
        _build_strategy_row(
            ticker=ticker,
            market=market,
            summary=summary_by_ticker.get(ticker) or {},
            context=context_by_ticker.get(ticker) or {},
            candidate=candidate_by_ticker.get(ticker) or {},
            action=action_by_ticker.get(ticker) or {},
            benchmark_context=benchmark_context,
        )
        for ticker in tickers
    ]
    rows.sort(key=lambda item: (_STRATEGY_ORDER.get(str(item.get("strategy_code") or ""), 99), int(item.get("portfolio_priority") or 9999), item["ticker"]))
    for index, row in enumerate(rows, start=1):
        row["table_priority"] = index

    quality = _build_quality(
        rows=rows,
        context=context,
        min_fresh_row_ratio=min_fresh_row_ratio,
    )
    strategy_counts: dict[str, int] = {}
    for row in rows:
        label = str(row.get("strategy_ko") or "판단 자료 부족")
        strategy_counts[label] = strategy_counts.get(label, 0) + 1
    return {
        "artifact_type": "decision_bundle",
        "version": DECISION_BUNDLE_VERSION,
        "run_id": run_id,
        "market": market,
        "generated_at": generated_at,
        "analysis_source_run_id": analysis_source_run_id,
        "execution_source_run_id": _execution_source_run_id(context),
        "checkpoint": context.get("checkpoint"),
        "checkpoint_timezone": context.get("checkpoint_timezone"),
        "quality": quality,
        "summary": {
            "ticker_count": len(rows),
            "strategy_counts": strategy_counts,
            "immediate_action_count": sum(row["strategy_code"] in {"BUY_NOW", "REDUCE", "SELL"} for row in rows),
        },
        "strategy_table": rows,
        "benchmark_context": benchmark_context,
        "display_policy": {
            "language": "ko",
            "machine_codes_preserved": True,
            "investor_facing_labels": "Korean",
        },
    }


def render_strategy_table_markdown(bundle: dict[str, Any]) -> str:
    quality = bundle.get("quality") or {}
    rows = select_investor_strategy_rows(list(bundle.get("strategy_table") or []))
    lines = [
        "# 종목별 투자 전략표",
        "",
        f"- 기준 run: `{bundle.get('run_id') or '-'}`",
        f"- 분석 기준 run: `{bundle.get('analysis_source_run_id') or '-'}`",
        f"- 실행 기준 run: `{bundle.get('execution_source_run_id') or '-'}`",
        f"- 데이터 상태: **{quality.get('quality_label_ko') or '판단 자료 부족'}**",
        f"- 현재 세션 핵심 데이터 충족률: **{float(quality.get('fresh_row_ratio') or 0) * 100:.1f}%**",
        f"- 조건부 전략 가능 비율: **{float(quality.get('conditional_row_ratio') or 0) * 100:.1f}%**",
        "",
        "| 우선 | 종목 | 보유 | 현재 전략 | 현재가 / 기준시각 | VWAP 대비 | 상대 거래량 | 거래대금 | 섹터·지수 동조 | 실행 조건 | 위험·무효화 | 데이터 상태 |",
        "|---:|---|---|---|---|---|---:|---:|---|---|---|---|",
    ]
    for display_priority, row in enumerate(rows, start=1):
        price_asof = f"{_fmt_number(row.get('last_price'))} / {row.get('market_data_asof') or '-'}"
        lines.append(
            "| {priority} | {ticker} | {held} | {strategy} | {price_asof} | {vwap} | {rvol} | {value} | {sync} | {condition} | {risk} | {status} |".format(
                priority=display_priority,
                ticker=row.get("ticker"),
                held="예" if row.get("is_held") else "아니오",
                strategy=_md_cell(row.get("strategy_ko")),
                price_asof=_md_cell(price_asof),
                vwap=_md_cell(row.get("vwap_position_ko")),
                rvol=_fmt_ratio(row.get("relative_volume")),
                value=_fmt_money(row.get("trading_value"), market=bundle.get("market")),
                sync=_md_cell(row.get("sync_summary_ko")),
                condition=_md_cell(row.get("execution_condition_ko")),
                risk=_md_cell(row.get("risk_condition_ko")),
                status=_md_cell(row.get("data_status_ko")),
            )
        )
    lines.extend(
        [
            "",
            "> 이 표는 투자 판단을 돕는 조건부 전략표이며 자동 주문 지시가 아닙니다. 데이터 상태가 '확인 전 대기'이면 매수·매도보다 데이터 재확인이 우선입니다.",
        ]
    )
    return "\n".join(lines) + "\n"


def select_investor_strategy_rows(rows: list[dict[str, Any]], *, max_new_candidates: int = 5) -> list[dict[str, Any]]:
    held_rows = [row for row in rows if row.get("is_held") is True]
    new_rows = [row for row in rows if row.get("is_held") is not True]
    selected = [*held_rows, *new_rows[: max(0, int(max_new_candidates))]]
    return [dict(row, display_priority=index) for index, row in enumerate(selected, start=1)]


def _build_strategy_row(
    *,
    ticker: str,
    market: str,
    summary: dict[str, Any],
    context: dict[str, Any],
    candidate: dict[str, Any],
    action: dict[str, Any],
    benchmark_context: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    gate = context.get("asof_execution_gate") if isinstance(context.get("asof_execution_gate"), dict) else {}
    generated_current = context.get("generated_in_current_run") is True
    freshness = str(context.get("freshness_class") or "").upper()
    eligibility = str(context.get("execution_eligibility") or "").upper()
    core_ready = bool(gate.get("core_fields_present")) and generated_current and freshness in CURRENT_FRESHNESS
    execution_ready = core_ready and eligibility in CURRENT_ELIGIBILITY
    conditional_ready = (
        bool(gate.get("core_fields_present"))
        and generated_current
        and freshness in CONDITIONAL_FRESHNESS
        and eligibility in CONDITIONAL_ELIGIBILITY
    )
    is_held = bool(candidate.get("is_held"))
    strategy_code = _strategy_code(
        context=context,
        candidate=candidate,
        action=action,
        is_held=is_held,
        execution_ready=execution_ready,
        conditional_ready=conditional_ready,
    )
    last_price = _float_or_none(context.get("last_price"))
    session_vwap = _float_or_none(context.get("session_vwap"))
    vwap_distance_pct = (
        (last_price / session_vwap - 1.0) * 100.0
        if last_price is not None and session_vwap is not None and session_vwap > 0
        else None
    )
    sector = str(candidate.get("sector") or "").strip()
    stock_change_pct = _float_or_none(context.get("price_change_pct"))
    sector_symbol = _sector_benchmark(market=market, sector=sector)
    index_symbol = _index_benchmark(market=market, ticker=ticker)
    sector_sync = _sync_payload(stock_change_pct, benchmark_context.get(sector_symbol) if sector_symbol else None, sector_symbol)
    index_sync = _sync_payload(stock_change_pct, benchmark_context.get(index_symbol), index_symbol)
    reason_codes = [str(item) for item in (context.get("reason_codes") or []) if str(item).strip()]
    data_status = _data_status_ko(
        context=context,
        execution_ready=execution_ready,
        conditional_ready=conditional_ready,
    )
    return {
        "table_priority": 0,
        "portfolio_priority": action.get("priority"),
        "ticker": ticker,
        "display_name": candidate.get("display_name") or summary.get("ticker_name") or ticker,
        "is_held": is_held,
        "sector": sector or None,
        "strategy_code": strategy_code,
        "strategy_ko": present_strategy_category(strategy_code),
        "last_price": last_price,
        "market_data_asof": context.get("market_data_asof"),
        "session_vwap": session_vwap,
        "vwap_distance_pct": vwap_distance_pct,
        "vwap_position_ko": _vwap_position_ko(vwap_distance_pct),
        "relative_volume": _float_or_none(context.get("relative_volume")),
        "intraday_volume": _int_or_none(context.get("intraday_volume")),
        "avg20_daily_volume": _float_or_none(context.get("avg20_daily_volume")),
        "trading_value": _float_or_none(context.get("trading_value")),
        "price_change_pct": stock_change_pct,
        "spread_bps": _float_or_none(context.get("spread_bps")),
        "sector_sync": sector_sync,
        "index_sync": index_sync,
        "sync_summary_ko": _sync_summary(sector_sync, index_sync),
        "execution_condition_ko": _execution_condition(context=context, candidate=candidate, action=action),
        "risk_condition_ko": _risk_condition(context=context, candidate=candidate, action=action),
        "data_status_ko": data_status,
        "decision_state_ko": present_execution_state(context.get("decision_state")),
        "execution_timing_ko": present_execution_timing(context.get("execution_timing_state")),
        "reason_codes_ko": [present_reason_code(item) for item in reason_codes],
        "raw_codes": {
            "decision_state": context.get("decision_state"),
            "decision_now": context.get("decision_now"),
            "decision_if_triggered": context.get("decision_if_triggered"),
            "execution_timing_state": context.get("execution_timing_state"),
            "portfolio_action_now": action.get("action_now"),
            "portfolio_action_if_triggered": action.get("action_if_triggered"),
            "reason_codes": reason_codes,
        },
        "quality": {
            "generated_in_current_run": generated_current,
            "freshness_class": context.get("freshness_class"),
            "execution_eligibility": context.get("execution_eligibility"),
            "core_fields_present": bool(gate.get("core_fields_present")),
            "execution_ready": execution_ready,
            "conditional_strategy_ready": conditional_ready,
        },
    }


def _strategy_code(
    *,
    context: dict[str, Any],
    candidate: dict[str, Any],
    action: dict[str, Any],
    is_held: bool,
    execution_ready: bool,
    conditional_ready: bool,
) -> str:
    action_now = str(action.get("action_now") or candidate.get("suggested_action_now") or "").upper()
    risk_action = str(action.get("risk_action") or candidate.get("risk_action") or "").upper()
    decision_now = str(context.get("decision_now") or "").upper()
    decision_state = str(context.get("decision_state") or "").upper()
    timing = str(context.get("execution_timing_state") or "").upper()
    if action_now in {"EXIT_NOW", "STOP_LOSS_NOW"} or decision_now == "EXIT_NOW":
        return "SELL"
    if action_now in {"REDUCE_NOW", "TRIM_NOW", "TAKE_PROFIT_NOW"} or decision_now == "REDUCE_NOW":
        return "REDUCE"
    if risk_action in {"STOP_LOSS", "EXIT"} and timing in {"SUPPORT_FAIL", "INVALIDATED"}:
        return "SELL" if is_held else "AVOID"
    if timing == "SUPPORT_FAIL" or decision_state == "INVALIDATED":
        return "REDUCE" if is_held else "AVOID"
    triggered_action = str(action.get("action_if_triggered") or candidate.get("suggested_action_if_triggered") or context.get("decision_if_triggered") or "").upper()
    if not execution_ready and not conditional_ready:
        return "DATA_CHECK"
    if not execution_ready:
        if decision_state == "TRIGGERED_PENDING_CLOSE":
            return "WAIT_CLOSE"
        if action_now in {"ADD_NOW", "STARTER_NOW"} or decision_now in {"ADD_NOW", "STARTER_NOW"}:
            return "BUY_ON_CONFIRMATION"
        if triggered_action in {"ADD", "STARTER", "ADD_IF_TRIGGERED", "STARTER_IF_TRIGGERED"}:
            return "BUY_ON_CONFIRMATION"
        if is_held:
            return "HOLD"
        if action_now == "AVOID" or risk_action in {"REDUCE_RISK", "STOP_LOSS", "EXIT"}:
            return "AVOID"
        return "WAIT"
    if action_now in {"ADD_NOW", "STARTER_NOW"} or decision_now in {"ADD_NOW", "STARTER_NOW"}:
        return "BUY_NOW"
    if decision_state == "TRIGGERED_PENDING_CLOSE":
        return "WAIT_CLOSE"
    if triggered_action in {"ADD", "STARTER", "ADD_IF_TRIGGERED", "STARTER_IF_TRIGGERED"} and decision_state in {"ARMED", "WAIT"}:
        return "BUY_ON_CONFIRMATION"
    if is_held:
        return "HOLD"
    if action_now == "AVOID" or risk_action in {"REDUCE_RISK", "STOP_LOSS", "EXIT"}:
        return "AVOID"
    return "WAIT"


def _build_quality(*, rows: list[dict[str, Any]], context: dict[str, Any], min_fresh_row_ratio: float) -> dict[str, Any]:
    total = len(rows)
    ready_rows = sum(bool((row.get("quality") or {}).get("execution_ready")) for row in rows)
    conditional_rows = sum(bool((row.get("quality") or {}).get("conditional_strategy_ready")) for row in rows)
    fresh_ratio = ready_rows / total if total else 0.0
    conditional_ratio = conditional_rows / total if total else 0.0
    decision_ready = bool(total and context and fresh_ratio >= float(min_fresh_row_ratio))
    conditional_strategy_ready = bool(
        total and context and conditional_ratio >= float(min_fresh_row_ratio)
    )
    if decision_ready:
        label = "장중 투자 판단 가능"
    elif conditional_strategy_ready:
        label = "장중 조건부 전략 가능, 주문 전 재확인"
    elif context:
        label = "일부 또는 지연 데이터, 확인 후 판단"
    else:
        label = "연구 자료만 제공, 장중 데이터 대기"
    missing_spread = sum(row.get("spread_bps") is None for row in rows)
    missing_sector_sync = sum((row.get("sector_sync") or {}).get("status_code") in {"NO_BENCHMARK", "NO_STOCK_CHANGE"} for row in rows)
    return {
        "decision_ready": decision_ready,
        "conditional_strategy_ready": conditional_strategy_ready,
        "quality_label_ko": label,
        "minimum_fresh_row_ratio": float(min_fresh_row_ratio),
        "fresh_row_ratio": round(fresh_ratio, 4),
        "conditional_row_ratio": round(conditional_ratio, 4),
        "ready_rows": ready_rows,
        "conditional_rows": conditional_rows,
        "total_rows": total,
        "missing_spread_rows": missing_spread,
        "missing_sector_sync_rows": missing_sector_sync,
        "current_context_present": bool(context),
    }


def _execution_condition(*, context: dict[str, Any], candidate: dict[str, Any], action: dict[str, Any]) -> str:
    conditions = action.get("trigger_conditions") or candidate.get("trigger_conditions") or []
    readable = [sanitize_investor_text(item, language="Korean") for item in conditions if str(item).strip()]
    if readable:
        return " / ".join(readable[:2])
    reasons = [present_reason_code(item) for item in (context.get("reason_codes") or []) if str(item).strip()]
    return " / ".join(reasons[:2]) if reasons else "추가 실행 조건 없음"


def _risk_condition(*, context: dict[str, Any], candidate: dict[str, Any], action: dict[str, Any]) -> str:
    invalidation_conditions = action.get("invalidation_conditions") or candidate.get("invalidation_conditions") or []
    readable_invalidation = [
        sanitize_investor_text(item, language="Korean")
        for item in invalidation_conditions
        if str(item).strip()
    ]
    if readable_invalidation:
        return " / ".join(readable_invalidation[:2])
    risk_action = str(action.get("risk_action") or candidate.get("risk_action") or "").upper()
    risk_level = action.get("risk_action_level") or candidate.get("risk_action_level") or {}
    if isinstance(risk_level, dict):
        level = risk_level.get("price") or risk_level.get("level") or risk_level.get("value")
        if level not in (None, ""):
            explicit_risk_actions = {
                "REDUCE_NOW",
                "TAKE_PROFIT_NOW",
                "STOP_LOSS_NOW",
                "TRIM_NOW",
                "EXIT_NOW",
                "TRIM_TO_FUND",
                "REDUCE_RISK",
                "TAKE_PROFIT",
                "STOP_LOSS",
                "EXIT",
            }
            response = (
                present_account_action(risk_action)
                if risk_action in explicit_risk_actions
                else "전략 재평가"
            )
            return f"{_fmt_number(level)} 이탈 시 {response}"
    timing = str(context.get("execution_timing_state") or "").upper()
    if timing == "SUPPORT_FAIL":
        return "지지선 이탈 상태, 비중 축소 우선 검토"
    if risk_action and risk_action != "NONE":
        return present_account_action(risk_action)
    return "현재 명시된 위험 행동 없음"


def _data_status_ko(*, context: dict[str, Any], execution_ready: bool, conditional_ready: bool) -> str:
    if execution_ready:
        return "현재 세션 데이터 사용 가능"
    if conditional_ready:
        return "현재 세션 조건부 데이터, 주문 전 호가·상태 재확인"
    if not context:
        return "장중 데이터 없음"
    if context.get("generated_in_current_run") is False:
        return "과거 데이터, 현재 판단에 사용 금지"
    gate = context.get("asof_execution_gate") if isinstance(context.get("asof_execution_gate"), dict) else {}
    missing = gate.get("missing_core_fields") or []
    if missing:
        return "핵심 데이터 누락: " + ", ".join(_field_label_ko(item) for item in missing)
    return "데이터 신선도 또는 실행 자격 재확인 필요"


def _benchmark_symbols(*, market: str, tickers: list[str], candidates: dict[str, dict[str, Any]]) -> set[str]:
    symbols = {_index_benchmark(market=market, ticker=ticker) for ticker in tickers}
    for ticker in tickers:
        sector = str((candidates.get(ticker) or {}).get("sector") or "")
        sector_symbol = _sector_benchmark(market=market, sector=sector)
        if sector_symbol:
            symbols.add(sector_symbol)
    return {symbol for symbol in symbols if symbol}


def _sector_benchmark(*, market: str, sector: str) -> str | None:
    if str(market).upper() != "US":
        return None
    normalized = " ".join(str(sector or "").strip().lower().replace("_", " ").split())
    if "semiconductor" in normalized:
        return "SOXX"
    return _US_SECTOR_ETF.get(normalized)


def _index_benchmark(*, market: str, ticker: str) -> str:
    if str(market).upper() == "US":
        return "SPY"
    return "^KQ11" if str(ticker).upper().endswith(".KQ") else "^KS11"


def _load_benchmark_context(symbols: set[str]) -> dict[str, dict[str, Any]]:
    if not symbols:
        return {}
    import yfinance as yf

    ordered = sorted(symbols)
    data = yf.download(
        tickers=ordered,
        period="1d",
        interval="5m",
        group_by="ticker",
        auto_adjust=False,
        progress=False,
        threads=True,
    )
    result: dict[str, dict[str, Any]] = {}
    for symbol in ordered:
        frame = data
        if getattr(data.columns, "nlevels", 1) > 1:
            if symbol not in data.columns.get_level_values(0):
                continue
            frame = data[symbol]
        if "Close" not in frame or frame["Close"].dropna().empty:
            continue
        closes = frame["Close"].dropna()
        first = float(closes.iloc[0])
        last = float(closes.iloc[-1])
        result[symbol] = {
            "symbol": symbol,
            "asof": closes.index[-1].isoformat() if hasattr(closes.index[-1], "isoformat") else str(closes.index[-1]),
            "last_price": last,
            "change_pct": ((last / first) - 1.0) * 100.0 if first > 0 else None,
            "source": "yfinance_5m",
        }
    return result


def _sync_payload(stock_change_pct: float | None, benchmark: dict[str, Any] | None, symbol: str | None) -> dict[str, Any]:
    if not symbol or not benchmark:
        return {"benchmark": symbol, "status_code": "NO_BENCHMARK", "status_ko": "비교 지표 미수집"}
    benchmark_change = _float_or_none(benchmark.get("change_pct"))
    if stock_change_pct is None:
        return {
            "benchmark": symbol,
            "benchmark_change_pct": benchmark_change,
            "status_code": "NO_STOCK_CHANGE",
            "status_ko": "종목 등락률 미수집",
        }
    if benchmark_change is None:
        return {"benchmark": symbol, "status_code": "NO_BENCHMARK", "status_ko": "비교 지표 미수집"}
    if stock_change_pct > 0 and benchmark_change > 0:
        code, label = "ALIGNED_UP", "동반 상승"
    elif stock_change_pct < 0 and benchmark_change < 0:
        code, label = "ALIGNED_DOWN", "동반 하락"
    elif abs(benchmark_change) < 0.05:
        code, label = "BENCHMARK_FLAT", "비교 지표 보합"
    else:
        code, label = "DIVERGED", "비동조"
    return {
        "benchmark": symbol,
        "benchmark_asof": benchmark.get("asof"),
        "stock_change_pct": stock_change_pct,
        "benchmark_change_pct": benchmark_change,
        "relative_strength_pct": stock_change_pct - benchmark_change,
        "status_code": code,
        "status_ko": label,
    }


def _sync_summary(sector_sync: dict[str, Any], index_sync: dict[str, Any]) -> str:
    sector = f"섹터 {sector_sync.get('status_ko')}" if sector_sync.get("benchmark") else "섹터 비교 없음"
    index = f"지수 {index_sync.get('status_ko')}"
    return f"{sector} / {index}"


def _vwap_position_ko(distance_pct: float | None) -> str:
    if distance_pct is None:
        return "VWAP 미확인"
    if distance_pct >= 0:
        return f"VWAP 위 +{distance_pct:.2f}%"
    return f"VWAP 아래 {distance_pct:.2f}%"


def _execution_source_run_id(context: dict[str, Any]) -> str | None:
    for ticker in context.get("tickers") or []:
        if not isinstance(ticker, dict):
            continue
        value = ticker.get("microstructure_source_run_id") or ticker.get("published_in_run_id")
        if value:
            return str(value)
    return None


def _load_artifact_json(run_dir: Path, value: Any) -> dict[str, Any]:
    if not value:
        return {}
    path = Path(str(value))
    if not path.is_absolute():
        path = run_dir / path
    return _load_json(path)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ticker_key(value: Any) -> str:
    return str(value or "").strip().upper()


def _float_or_none(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    parsed = _float_or_none(value)
    return int(parsed) if parsed is not None else None


def _field_label_ko(value: Any) -> str:
    return {
        "last_price": "현재가",
        "session_vwap": "VWAP",
        "relative_volume": "상대 거래량",
        "spread_bps": "매수·매도 호가 차이",
    }.get(str(value), str(value).replace("_", " "))


def _fmt_number(value: Any) -> str:
    parsed = _float_or_none(value)
    if parsed is None:
        return "-"
    return f"{parsed:,.2f}".rstrip("0").rstrip(".")


def _fmt_ratio(value: Any) -> str:
    parsed = _float_or_none(value)
    return f"{parsed:.2f}배" if parsed is not None else "-"


def _fmt_money(value: Any, *, market: Any) -> str:
    parsed = _float_or_none(value)
    if parsed is None:
        return "-"
    unit = "원" if str(market).upper() == "KR" else "달러"
    if parsed >= 100_000_000:
        return f"{parsed / 100_000_000:.1f}억 {unit}"
    if parsed >= 10_000:
        return f"{parsed / 10_000:.1f}만 {unit}"
    return f"{parsed:,.0f} {unit}"


def _md_cell(value: Any) -> str:
    return str(value or "-").replace("|", "/").replace("\n", " ")
