"""One point-in-time snapshot supplies both replay and the chart viewer."""
from __future__ import annotations

from datetime import datetime, timezone

from .bars import finite, instant
from .report import build_review
from .identity import research_company_matches


def get_replay_snapshot(ticker, as_of_ts, *, ticker_dir, db_paths=(), anchor=None, clock=None, phase_hook=None,
                        journal_proof_hook=None):
    from tradingagents.performance.replay import replay_action_history
    from tradingagents.dataflows.market_policy import observation_status, latest_regular_session_context, research_observation_policy
    cutoff = instant(as_of_ts)
    if cutoff is None:
        raise ValueError("as_of_ts requires a timezone")
    now = instant(clock() if clock is not None else datetime.now(timezone.utc))
    if now is None or cutoff > now:
        raise ValueError("Snapshot cutoff cannot be in the future")
    if not research_company_matches(ticker_dir, ticker, cutoff=cutoff):
        raise ValueError("Snapshot research company does not match the requested instrument")
    if phase_hook is not None:
        phase_hook("REPLAY")
    proof_args = {"proof_hook": journal_proof_hook} if journal_proof_hook is not None else {}
    history = replay_action_history(db_paths, analysis_as_of=cutoff.isoformat(), ticker=ticker, **proof_args) if db_paths else {}
    if phase_hook is not None:
        phase_hook("BUILD")
    review = build_review(ticker_dir, analysis_as_of=cutoff, anchor=anchor, lifecycle=history)
    if review["ticker"].upper() != ticker.upper():
        raise ValueError("Snapshot ticker does not match its archive")
    markers = []
    for event in history.get("events", []):
        payload = event["payload"]
        kind = event["kind"]
        category = {"actual": "REAL_FILL", "demo": "DEMO_FILL", "paper": "PAPER_FILL"}.get(event["mode"], "PAPER_FILL") if kind == "FILL" else "SIGNAL"
        if kind not in {"FILL", "SIGNAL"}:
            continue
        side = str(payload.get("side") or payload.get("action") or kind)
        sell = side.upper() in {"SELL", "EXIT", "REDUCE_RISK", "STOP_LOSS", "TAKE_PROFIT"}
        prefix = {"REAL_FILL": "실제 체결", "DEMO_FILL": "데모 체결", "PAPER_FILL": "모의 체결", "SIGNAL": "추천"}[category]
        markers.append({"time": int(instant(event["occurred_at"]).timestamp()), "position": "aboveBar" if sell else "belowBar",
                        "shape": "arrowDown" if sell else "arrowUp", "text": f"{prefix} · {side}",
                        "color": "#c53b51" if sell else "#13785f", "category": category})
    for event in review["events"]["events"]:
        at = instant(event.get("first_seen_at") or event.get("published_at") or event.get("known_at"))
        if at:
            markers.append({"time": int(at.timestamp()), "position": "aboveBar", "shape": "circle",
                            "text": str(event.get("title", "공시")), "category": "EVENT_GUARD"})
    execution = review["execution"]
    if execution.get("reason_codes"):
        at = instant(execution.get("execution_asof"))
        if at:
            markers.append({"time": int(at.timestamp()), "position": "aboveBar", "shape": "square",
                            "text": ", ".join(execution["reason_codes"]), "category": "BLOCK_REASON"})
    levels = []
    stored_vwap = finite(execution.get("session_vwap"))
    if stored_vwap is not None and stored_vwap > 0:
        levels.append({"price": stored_vwap, "label": "당일 VWAP · 실행 엔진", "style": "DOTTED",
                       "market_data_asof": execution.get("market_data_asof"),
                       "event_time": execution.get("market_data_asof"), "ingested_at": execution.get("ingested_at"),
                       "evaluated_at": execution.get("execution_asof")})
    for item in review["plan"].get("structured_levels") or []:
        if not isinstance(item, dict):
            continue
        for field in ("price", "low", "high"):
            value = finite(item.get(field))
            if value is not None and value > 0:
                levels.append({"price": value, "label": str(item.get("label") or item.get("level_type") or "계획"), "style": "DASHED"})
    for field, label in (("breakout_trigger", "돌파 기준"), ("breakout_level", "돌파 기준"),
                         ("invalidation_price", "무효화"), ("invalid_if_close_below", "종가 무효화"),
                         ("invalid_if_intraday_below", "장중 무효화")):
        value = finite(review["plan"].get(field))
        if value is not None and value > 0:
            levels.append({"price": value, "label": label, "style": "DASHED"})
    zone = review["plan"].get("pullback_buy_zone")
    if isinstance(zone, dict):
        for field, label in (("low", "눌림 계획 하단"), ("high", "눌림 계획 상단")):
            value = finite(zone.get(field))
            if value is not None and value > 0:
                levels.append({"price": value, "label": label, "style": "DASHED"})
    state = execution.get("decision_state")
    from tradingagents.agents.utils.instrument_resolver import resolve_instrument
    try:
        instrument = resolve_instrument(ticker)
        market = "KR" if instrument.country.upper() in {"KR", "KOR", "KOREA"} else "US"
    except ValueError:
        market = "KR" if ticker[:6].isdigit() else "US"
    context = latest_regular_session_context(market, as_of=cutoff)
    daily = [bar for item in review["series"] if item["interval"] == "1d" for bar in item["bars"]]
    source_time = execution.get("market_data_asof")
    interval = "1m"
    if not context["session"].get("is_open") and daily:
        source_time = max((instant(bar["timestamp"]) for bar in daily)).isoformat()
        interval = "1d"
    elif source_time is None:
        all_bars = [bar for item in review["series"] for bar in item["bars"]]
        if all_bars:
            latest = max(all_bars, key=lambda bar: instant(bar["timestamp"]))
            source_time, interval = latest["timestamp"], latest["interval"]
    research = research_observation_policy(source_time, as_of=cutoff, session=context["session"], interval=interval,
                                           latest_regular_close_at=context["latest_regular_close_at"],
                                           verified_session=context["verified_session"])
    # Preserve the engine verdict verbatim. The viewer must not derive execution readiness.
    return {**review, "as_of_evaluated_at": cutoff.isoformat(), "execution_verdict": state,
            "block_reasons": execution.get("reason_codes", []), "price_levels": levels,
            "freshness_status": observation_status(execution.get("market_data_asof"), as_of=cutoff)["status"],
            "research_status": research["category"], "research_receipt": research,
            "markers": sorted(markers, key=lambda marker: (marker["time"], marker["category"])),
            "evidence_summary": {"facts": [e for e in review["evidence"] if e["kind"] == "fact"],
                                 "inferences": [e for e in review["evidence"] if e["kind"] != "fact"],
                                 "unverified_count": review["unverified_evidence_count"]}}
