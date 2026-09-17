"""Account-first research allocation. Scores prioritize research, never orders.

Only timestamped observations and completed, same-market historical analyses
can influence selection. The deterministic receipt makes every inclusion,
exclusion and degraded data source inspectable without another LLM call.
"""
from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import math
from pathlib import Path
import json
import re
from zoneinfo import ZoneInfo

import yfinance as yf
import pandas as pd

from tradingagents.scanner.prism_like_scanner import _ticker_identity_key
from tradingagents.schemas import parse_structured_decision, StructuredDecisionValidationError

SECTORS = ("Basic Materials", "Communication Services", "Consumer Cyclical",
           "Consumer Defensive", "Energy", "Financial Services", "Healthcare",
           "Industrials", "Real Estate", "Technology", "Utilities")
QUOTE_FIELDS = ("symbol", "currency", "regularMarketTime", "regularMarketPrice",
                "regularMarketVolume", "averageDailyVolume3Month", "fiftyDayAverage",
                "twoHundredDayAverage", "fiftyTwoWeekHigh", "regularMarketChangePercent",
                "earningsTimestampStart", "sector", "quoteType")


def identity(ticker):
    return _ticker_identity_key(str(ticker).upper())


def in_market(ticker, market):
    text = str(ticker).upper()
    if market == "KR":
        return bool(re.fullmatch(r"\d{6}(?:\.KS|\.KQ)?", text))
    return market == "US" and bool(re.fullmatch(r"[A-Z][A-Z0-9-]{0,14}(?:\.[A-Z])?", text))


def unique(values):
    result = {}
    for value in values:
        text = str(value).strip().upper()
        if text:
            result.setdefault(identity(text), text)
    return list(result.values())


def stamp(value):
    try:
        if isinstance(value, (float, int)):
            return datetime.fromtimestamp(value, timezone.utc)
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
    except (ValueError, TypeError, OverflowError, OSError):
        return None


def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (ValueError, TypeError):
        return None


def read_history(archive: Path, *, market, asof, days, profile_name=None):
    """Read only completed full analyses, never future/overlay or other profiles."""
    manifests = []
    # Production archives are runs/YYYY/run-id/run.json. Never recurse through
    # every ticker's engine/artifact tree to find the small run-level index.
    paths = sorted((Path(archive) / "runs").glob("*/*/run.json"), reverse=True)
    for path in paths[:2000]:
        try:
            prefix = path.parent.name[:8]
            if prefix.isdigit() and prefix < (asof - timedelta(days=days + 1)).strftime("%Y%m%d"):
                continue
            item = json.loads(path.read_text(encoding="utf-8"))
            settings = item.get("settings") or {}
            ended = stamp(item.get("finished_at"))
            if not ended or not asof - timedelta(days=days) <= ended <= asof:
                continue
            if str(settings.get("market", "")).upper() != market or settings.get("run_mode", "full") != "full":
                continue
            if settings.get("analysis_mode", "full") == "smoke":
                continue
            profile = settings.get("portfolio_profile_name") or (item.get("portfolio") or {}).get("profile")
            if profile_name and profile not in (None, profile_name):
                continue
            active = item.get("active_universe") or {}
            compact = {"run_id": item.get("run_id"), "status": item.get("status"),
                "active_universe": {"coverage": active.get("coverage"), "candidates": active.get("candidates", [])},
                "tickers": [{key: row.get(key) for key in ("ticker", "status", "decision", "quality_flags", "finished_at")}
                            for row in item.get("tickers", []) if isinstance(row, dict)]}
            manifests.append((ended, compact))
        except (OSError, ValueError, TypeError, AttributeError):
            continue
    manifests.sort(key=lambda pair: pair[0], reverse=True)
    observations, previous, cached_quotes = {}, [], {}
    for ended, item in manifests:
        active = item.get("active_universe") or {}
        if not previous and item.get("status") == "success" and (active.get("coverage") or {}).get("complete") is True:
            previous = unique(row.get("ticker") for row in item.get("tickers", []) if row.get("status") == "success" and in_market(row.get("ticker"), market))
        for candidate in active.get("candidates", []):
            quote = candidate.get("quote") or {}
            ticker = quote.get("symbol")
            if in_market(ticker, market):
                cached_quotes.setdefault(identity(ticker), quote)
        for row in item.get("tickers", []):
            ticker = row.get("ticker")
            key = identity(ticker)
            if key in observations or not in_market(ticker, market) or row.get("status") != "success":
                continue
            observed = stamp(row.get("finished_at")) or ended
            if observed > asof or "decision_unvalidated" in (row.get("quality_flags") or []):
                continue
            try:
                decision = parse_structured_decision(row.get("decision"))
                if "CODEX_PROVIDER_UNAVAILABLE" in decision.risk_action_reason_codes:
                    continue
            except (StructuredDecisionValidationError, TypeError, ValueError):
                continue
            observations[key] = {"ticker": ticker, "asof": observed.isoformat(),
                "run_id": item.get("run_id"), "rating": decision.rating.value,
                "setup_quality": decision.setup_quality.value,
                "entry_action": decision.entry_action.value,
                "risk_action": decision.risk_action.value,
                "quality_flags": list(row.get("quality_flags") or []),
                "trigger_prices": [level.price or level.high or level.low for level in decision.execution_levels.levels
                                   if level.level_type.value in {"BREAKOUT", "PULLBACK"}]}
    return observations, previous, cached_quotes


def research_quotes(*, market, tickers, max_candidates):
    """Wide, sector-balanced discovery plus refresh of the existing candidate pool.

    Screens return quotes, not 4-agent analyses. Each request is bounded and
    failed sources are reported independently so account coverage survives.
    """
    quotes, warnings = {}, []
    region = yf.EquityQuery("eq", ["region", market.lower()])
    consecutive_failures = 0

    def fetch(query, label, *, size=50, sort="intradaymarketcap", sector=None):
        nonlocal consecutive_failures
        if consecutive_failures >= 3:
            return
        try:
            response = yf.screen(query, size=size, sortField=sort, sortAsc=False)
            rows = response.get("quotes", [])
            consecutive_failures = 0
            if not rows:
                warnings.append(f"empty_research_source:{label}")
            for row in rows:
                ticker = row.get("symbol")
                if not in_market(ticker, market):
                    continue
                quote = {field: row.get(field) for field in QUOTE_FIELDS}
                key = identity(ticker)
                quote["sector"] = sector or row.get("sector") or (quotes.get(key) or {}).get("sector")
                quote["source"] = "yahoo_screener"
                quotes[key] = quote
        except Exception as exc:
            # Source errors can contain request URLs. Persist only their type.
            warnings.append(f"research_source_failed:{label}:{type(exc).__name__}")
            consecutive_failures += 1

    for sector in SECTORS:
        fetch(yf.EquityQuery("and", [region, yf.EquityQuery("eq", ["sector", sector])]), sector, size=5, sector=sector)
    fetch(region, "liquid_leaders", size=30, sort="dayvolume")
    # Yahoo's public screener cannot query ticker symbols. Refresh remaining
    # seeds in a bounded OHLCV batch, rather than per-symbol fundamentals calls.
    existing = [t for t in unique(tickers) if in_market(t, market)
                and identity(t) not in quotes and not (market == "KR" and t.isdigit())][:max_candidates]
    if existing and consecutive_failures < 3:
        refreshed, failures = refresh_seed_quotes(existing, market=market)
        quotes.update(refreshed)
        warnings.extend(failures)
    if consecutive_failures >= 3:
        warnings.append("research_source_circuit_open")
    # Classify legacy/held seeds that did not appear in a sector screen.
    # Missing classifications remain explicit; never infer a sector from a name.
    seed_ids = {identity(t) for t in tickers}
    unknown = [q["symbol"] for key, q in quotes.items() if key in seed_ids and not q.get("sector")][:60]
    def sector_for(ticker):
        try:
            info = yf.Ticker(ticker).get_info()
            sector = info.get("sector")
            return ticker, sector if sector in SECTORS else None
        except Exception:
            return ticker, None
    if unknown:
        with ThreadPoolExecutor(max_workers=4) as executor:
            for ticker, sector in executor.map(sector_for, unknown):
                quotes[identity(ticker)]["sector"] = sector
        missing = sum(not quotes[identity(t)]["sector"] for t in unknown)
        if missing:
            warnings.append(f"seed_sector_unverified:{missing}")
    return quotes, warnings


def refresh_seed_quotes(tickers, *, market):
    quotes, warnings = {}, []
    try:
        data = yf.download(tickers, period="1y", group_by="ticker", auto_adjust=False,
                           progress=False, threads=4, timeout=15, multi_level_index=True)
    except Exception as exc:
        return {}, [f"seed_price_refresh_failed:{type(exc).__name__}"]
    for ticker in tickers:
        try:
            frame = data[ticker].dropna(how="all") if isinstance(data.columns, pd.MultiIndex) else data.dropna(how="all")
            close = pd.to_numeric(frame["Close"], errors="coerce")
            volume = pd.to_numeric(frame["Volume"], errors="coerce")
            if frame.empty or not number(close.iloc[-1]) or close.iloc[-1] <= 0:
                raise ValueError("missing latest close")
            latest = pd.Timestamp(frame.index[-1])
            if latest.tzinfo is None:
                latest = latest.tz_localize(ZoneInfo("Asia/Seoul" if market == "KR" else "America/New_York"))
            price = float(close.iloc[-1])
            quotes[identity(ticker)] = {"symbol": ticker, "currency": "KRW" if market == "KR" else "USD",
                "regularMarketTime": latest.timestamp(), "regularMarketPrice": price,
                "regularMarketVolume": number(volume.iloc[-1]),
                "averageDailyVolume3Month": number(volume.tail(63).mean()) if volume.notna().sum() >= 20 else None,
                "fiftyDayAverage": number(close.tail(50).mean()) if close.notna().sum() >= 50 else None,
                "twoHundredDayAverage": number(close.tail(200).mean()) if close.notna().sum() >= 200 else None,
                "regularMarketChangePercent": (price / close.iloc[-2] - 1) * 100 if len(close) > 1 and number(close.iloc[-2]) and close.iloc[-2] > 0 else None,
                "sector": None, "source": "yahoo_daily_bars", "price_timestamp_precision": "session_date"}
        except (KeyError, ValueError, TypeError, IndexError):
            warnings.append(f"seed_price_unavailable:{ticker}")
    return quotes, warnings


def evaluate_candidate(ticker, quote, history, *, asof, settings, market, incumbent):
    quote = {key: (None if isinstance(value, float) and not math.isfinite(value) else value)
             for key, value in quote.items()}
    row = {"ticker": ticker, "score": 0.0, "eligible": False, "reasons": [],
           "sector": quote.get("sector") or "UNKNOWN", "quote": quote,
           "history": history, "incumbent": incumbent}
    price = number(quote.get("regularMarketPrice"))
    observed = stamp(quote.get("regularMarketTime"))
    if not price or price <= 0 or not observed or not asof - timedelta(days=settings.quote_max_age_days) <= observed <= asof:
        row["reasons"] = ["missing_stale_or_future_price"]
        return row
    if quote.get("currency") != ("KRW" if market == "KR" else "USD"):
        row["reasons"] = ["currency_not_verified"]
        return row
    volume = number(quote.get("averageDailyVolume3Month"))
    daily_value = price * volume if volume and volume > 0 else 0
    minimum = settings.min_daily_value_krw if market == "KR" else settings.min_daily_value_usd
    if not math.isfinite(daily_value) or daily_value < minimum:
        row["reasons"] = ["insufficient_verified_liquidity"]
        return row
    change = number(quote.get("regularMarketChangePercent"))
    if change is not None and abs(change) > 20:
        row["reasons"] = ["extreme_daily_move_requires_separate_review"]
        return row
    reasons = ["liquidity_verified"]
    score = min(15, 5 * math.log10(max(1, daily_value / minimum)) + 5)
    for field, points in (("fiftyDayAverage", 10), ("twoHundredDayAverage", 10)):
        average = number(quote.get(field))
        if average and average > 0 and price >= average:
            score += points
            reasons.append(f"above_{field}")
    average = number(quote.get("fiftyDayAverage"))
    if average and price / average > 1.20:
        score -= 12
        reasons.append("extended_above_medium_term_trend")
    event = stamp(quote.get("earningsTimestampStart"))
    if event and asof <= event <= asof + timedelta(days=7):
        score += 5
        reasons.append("upcoming_earnings_needs_research_not_buy_signal")
    if history:
        age = max(0, (asof - stamp(history["asof"])).total_seconds() / 86400)
        decay = max(0, 1 - age / settings.history_days)
        quality = {"BUY": 16, "OVERWEIGHT": 12, "HOLD": 2, "NO_TRADE": -5, "UNDERWEIGHT": -8, "SELL": -12}.get(history["rating"], 0)
        quality += {"COMPELLING": 8, "DEVELOPING": 3, "WEAK": -3}.get(history["setup_quality"], 0)
        if history["risk_action"] in {"EXIT", "STOP_LOSS", "REDUCE_RISK"}:
            quality -= 10
        if set(history["quality_flags"]) & {"no_tool_calls_detected", "decision_unvalidated", "intraday_snapshot_missing_same_day"}:
            quality -= 8
        score += quality * decay
        reasons.append("age_weighted_prior_analysis")
        if any(number(p) and abs(price / float(p) - 1) <= 0.03 for p in history["trigger_prices"] if number(p) and float(p) > 0):
            score += 6 * decay
            reasons.append("near_prior_entry_condition_requires_revalidation")
    if incumbent:
        score += 5
        reasons.append("continuity_bonus")
    row.update(score=round(score, 4), eligible=True, reasons=reasons, average_daily_value=daily_value)
    return row


def select_adaptive_universe(*, config, universe, tickers, asof, requested_limit=0,
                             quotes=None, history_bundle=None):
    settings = config.universe
    if not 1 <= settings.max_tickers <= 30:
        raise ValueError("Adaptive universe hard limit must be between 1 and 30")
    market = config.run.market.upper()
    if market not in {"US", "KR"}:
        raise ValueError("Adaptive universe requires an explicit US or KR market")
    if universe.account_snapshot_status != "loaded":
        raise RuntimeError("ADAPTIVE_ACCOUNT_UNAVAILABLE: cannot guarantee mandatory holding coverage")
    holdings = unique(universe.holding_tickers)
    if any(not in_market(t, market) for t in holdings):
        raise RuntimeError("ADAPTIVE_HOLDING_MARKET_MISMATCH: verify account market configuration")
    if len(holdings) > settings.max_tickers:
        raise RuntimeError("ADAPTIVE_HOLDINGS_EXCEED_CAP: all holdings cannot fit within the 30-ticker cap")
    asof = stamp(asof)
    history, previous, cached = history_bundle if history_bundle is not None else read_history(
        config.storage.archive_dir, market=market, asof=asof, days=settings.history_days,
        profile_name=getattr(config.portfolio, "profile_name", None))
    holding_keys = {identity(t) for t in holdings}
    previous_keys = {identity(t) for t in previous}
    seeds = unique([*holdings, *previous, *tickers, *(h["ticker"] for h in history.values())])
    warnings = []
    if quotes is None:
        explicit = getattr(config.run, "explicit_trade_date", None)
        if explicit and explicit < asof.date().isoformat():
            raise RuntimeError("ADAPTIVE_HISTORICAL_RUN_UNSUPPORTED: use a historical universe snapshot with adaptive selection disabled")
        quotes, warnings = research_quotes(market=market, tickers=seeds, max_candidates=settings.max_candidates)
        asof = max(asof, datetime.now(timezone.utc))
    quotes = dict(quotes)
    for key, quote in cached.items():
        if key not in quotes:
            quotes[key] = {**quote, "source": "archived_quote"}
    pool = unique([*holdings, *previous, *tickers, *(q["symbol"] for q in quotes.values()), *(h["ticker"] for h in history.values())])
    pool = [t for t in pool if in_market(t, market)]
    # Reserve discovery capacity even when legacy seed files grow very large.
    discovered = [q["symbol"] for q in quotes.values() if identity(q["symbol"]) not in {identity(t) for t in seeds}]
    ordered_pool = unique([*holdings, *previous, *discovered[:60], *pool])
    pool = ordered_pool[:settings.max_candidates]
    rows = [evaluate_candidate(t, quotes.get(identity(t), {}), history.get(identity(t)),
             asof=asof, settings=settings, market=market, incumbent=identity(t) in previous_keys) for t in pool]
    by_key = {identity(row["ticker"]): row for row in rows}
    # Use an exchange-qualified alias when available without consuming another slot.
    selected = [next((t for t in unique([*tickers, *pool]) if identity(t) == identity(h)), h) for h in holdings]
    limit = min(settings.max_tickers, max(len(holdings), requested_limit)) if requested_limit > 0 else settings.max_tickers
    ranked = sorted((r for r in rows if r["eligible"] and identity(r["ticker"]) not in holding_keys), key=lambda r: (-r["score"], r["ticker"]))
    sectors = Counter(by_key[identity(t)]["sector"] for t in selected if identity(t) in by_key)
    selected_keys = set(holding_keys)
    new_count = 0
    reasons = {key: "mandatory_account_holding" for key in holding_keys}

    def add(row, reason):
        nonlocal new_count
        key, sector = identity(row["ticker"]), row["sector"]
        if key in selected_keys or len(selected) >= limit:
            return False
        if sector != "UNKNOWN" and sectors[sector] >= settings.max_per_sector:
            return False
        if previous and key not in previous_keys and new_count >= settings.max_new_nonholdings:
            return False
        selected.append(row["ticker"])
        selected_keys.add(key)
        sectors[sector] += 1
        new_count += int(key not in previous_keys)
        reasons[key] = reason
        return True

    if universe.mode != "account_only":
        # A small exploration budget breaks feedback loops from only revisiting winners.
        explored = 0
        for row in ranked:
            if explored >= min(settings.exploration_slots, max(0, limit - len(holdings))):
                break
            if identity(row["ticker"]) not in history and identity(row["ticker"]) not in previous_keys and add(row, "fresh_candidate_exploration"):
                explored += 1
        for row in ranked:
            add(row, "evidence_rank_and_continuity")
    for row in rows:
        key = identity(row["ticker"])
        row["selected"] = key in selected_keys
        if key in reasons:
            row["selection_reason"] = reasons[key]
        elif not row["eligible"]:
            row["selection_reason"] = "failed_data_or_liquidity_gate"
        elif row["sector"] != "UNKNOWN" and sectors[row["sector"]] >= settings.max_per_sector:
            row["selection_reason"] = "sector_research_limit"
        elif previous and key not in previous_keys and new_count >= settings.max_new_nonholdings:
            row["selection_reason"] = "run_replacement_limit"
        else:
            row["selection_reason"] = "below_research_capacity_cutoff"
    watch = [t for t in selected if identity(t) not in holding_keys]
    # Preserve the prior public/private boundary for holdings that were already
    # independently public research seeds. Account-only holdings stay private.
    public_seed_ids = {identity(t) for t in [*universe.configured_tickers, *getattr(universe, "profile_watch_tickers", ())]}
    public_watch = [t for t in selected if identity(t) not in holding_keys or identity(t) in public_seed_ids]
    omitted = [t for t in pool if identity(t) not in selected_keys]
    metadata = {"mode": "adaptive_required_coverage", "policy_version": 1,
        "market": market, "asof": asof.isoformat(), "ticker_universe_mode": "config_plus_account",
        "account_snapshot_status": universe.account_snapshot_status,
        "account_snapshot_health": universe.account_snapshot_health,
        "configured_count": len(pool), "candidate_pool_count": len(pool),
        "configured_input_count": len(universe.configured_tickers), "account_holding_count": len(holdings),
        "requested_limit": requested_limit, "effective_limit": limit, "hard_limit": settings.max_tickers,
        "active_count": len(selected), "omitted_count": len(omitted),
        "holding_tickers": selected[:len(holdings)], "expected_holding_tickers": holdings,
        "watchlist_tickers": watch, "expected_watchlist_tickers": public_watch,
        "missing_holding_tickers": [], "missing_watchlist_tickers": [], "omitted_tickers": omitted,
        "selected_tickers": selected, "previous_tickers": previous, "new_nonholding_count": new_count,
        "candidates": rows, "research_warnings": warnings,
        "deferred_by_candidate_pool_limit": ordered_pool[settings.max_candidates:],
        "excluded_other_market": [t for t in unique(tickers) if not in_market(t, market)],
        "unknown_sector_count": sum(row["sector"] == "UNKNOWN" for row in rows if row["selected"]),
        "underfilled": len(selected) < limit, "scores_are_profit_probabilities": False,
        "coverage": {"complete": True, "holding_expected_count": len(holdings),
            "holding_selected_count": len(holdings), "holding_missing_count": 0,
            "watchlist_expected_count": len(public_watch), "watchlist_selected_count": len(public_watch), "watchlist_missing_count": 0}}
    return selected, omitted, metadata


def render_selection_report(receipt):
    labels = {"mandatory_account_holding": "보유 종목 필수 포함",
        "fresh_candidate_exploration": "새 후보 조사 자리",
        "evidence_rank_and_continuity": "분석 근거·연속성 우선순위",
        "failed_data_or_liquidity_gate": "가격·유동성 자료 확인 부족",
        "sector_research_limit": "업종 편중 제한",
        "run_replacement_limit": "이번 실행의 신규 편입 제한",
        "below_research_capacity_cutoff": "오늘의 분석 상한 밖"}
    lines = ["# 오늘의 분석 종목 선정", "",
        f"시장: {receipt['market']} / 선정 기준시각: {receipt['asof']}", "",
        f"후보 {receipt['candidate_pool_count']}개 중 {receipt['active_count']}개 선정. 보유 {receipt['account_holding_count']}개는 필수 포함, 전체 상한은 {receipt['hard_limit']}개입니다.",
        "점수는 조사할 순서를 정하는 기준이며 수익 확률·매수 추천·계좌 비중이 아닙니다. 제외는 매도 지시가 아닙니다.",
        "보유 종목은 자료 부족이나 낮은 점수와 무관하게 점검합니다. 상한보다 적어도 자료·업종·교체 제한을 완화해 채우지 않습니다.", ""]
    for selected, title in ((True, "선정 종목"), (False, "오늘 제외한 후보")):
        lines += [f"## {title}", "", "| 종목 | 선정·제외 이유 | 업종 | 조사 점수 |", "|---|---|---|---|"]
        for row in receipt["candidates"]:
            if row["selected"] != selected:
                continue
            score = "필수 점검" if row["selection_reason"] == "mandatory_account_holding" else f"{row['score']:.1f}"
            sector = "확인되지 않음" if row["sector"] == "UNKNOWN" else row["sector"]
            lines.append(f"| {row['ticker']} | {labels[row['selection_reason']]} | {sector} | {score} |")
        lines += [""]
    lines += ["## 자료 상태", "", f"선정 종목 중 업종 미확인: {receipt['unknown_sector_count']}개. 업종 제한은 확인된 분류에만 적용됩니다."]
    if receipt["research_warnings"]:
        lines += ["일부 최신 조사 자료를 얻지 못했습니다. JSON 기록의 research_warnings와 각 후보의 quote/source를 확인하세요."]
    else:
        lines += ["이번 조회에서 조사 공급자 오류는 보고되지 않았습니다."]
    return "\n".join(lines)
