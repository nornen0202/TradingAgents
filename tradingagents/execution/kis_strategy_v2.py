"""Connect optional V2 sizing to the guarded native KIS strategy."""

from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import json
import re
from zoneinfo import ZoneInfo

from tradingagents.portfolio.kis import KisApiError, KisClient
from .demo_validation import MARKETS
from .experiments import _stamp
from .paper_policy_v2 import bind_v2_journal, size_v2_candidate

EVIDENCE_SCHEMA = "tradingagents.kis-v2-evidence/v1"
REGULAR_BENCHMARK_EVIDENCE_SCHEMA = "tradingagents.kis-v2-evidence/v2"
REGULAR_BENCHMARK = "KIS_REGULAR_MINUTE"
SETTLEMENT_SCHEMA = "tradingagents.kis-v2-reviewed-settlement/v1"
_MARKETS = {"KR": ("KRW", "krw"), "US": ("USD", "usd")}
_BENCHMARKS = {"KR": ("0001", "KIS_KR_INDEX"), "US": ("SPX", "KIS_US_INDEX")}


def configured_v2(config):
    rows = config.get("paper_policy_v2", {})
    if not isinstance(rows, dict) or set(rows) - set(_MARKETS):
        raise ValueError("KIS V2 settings must specify an explicit market")
    for market, row in rows.items():
        if (not isinstance(row, dict) or set(row) not in ({"policy", "watchlist"}, {"policy", "watchlist", "benchmark_basis"})
                or ("benchmark_basis" in row and row["benchmark_basis"] != REGULAR_BENCHMARK)
                or not isinstance(row["policy"], dict) or row["policy"].get("broker") != "kis_vts"
                or row["policy"].get("market") != market or row["policy"].get("currency") != _MARKETS[market][0]):
            raise ValueError("KIS V2 settings require one matching native policy and watchlist")
    return rows


def _reviewed_document(path, reference=None):
    with path.open("rb") as stream:
        raw = stream.read(128_001)
    if len(raw) > 128_000:
        raise ValueError("KIS V2 evidence exceeds its private read bound")
    digest = hashlib.sha256(raw).hexdigest()
    if reference is not None and reference != digest:
        raise ValueError("KIS V2 source bytes differ from the reviewed receipt")
    return json.loads(raw.decode("utf-8-sig")), digest


def current_v2_benchmark(market, *, clock, session):
    """Use a completed index minute from the same regular exchange session."""
    opened, closed = (_stamp(session.get(key)) for key in ("session_open", "session_close"))
    started = _stamp(clock())
    if (session.get("source") != "exchange_calendars" or session.get("phase") != "regular"
            or session.get("is_open") is not True or not opened <= started < closed):
        raise ValueError("KIS_V2_BENCHMARK_UNVERIFIED")
    client = KisClient.from_api_keys(environment="real")
    try:
        payload = client.regular_index_minutes(market)
        observed = _stamp(clock())
    except KisApiError:
        raise ValueError("KIS_V2_BENCHMARK_UNVERIFIED") from None
    finally:
        client.session.close()
    symbol, source = _BENCHMARKS[market]
    identity, price = ("bstp_cls_code", "bstp_nmix_prpr") if market == "KR" else ("stck_shrn_iscd", "optn_prpr")
    header, rows = payload.get("output1"), payload.get("output2")
    if (str(payload.get("rt_cd")) != "0" or not started <= observed < closed
            or not isinstance(header, dict) or header.get(identity) != symbol or not isinstance(rows, list)):
        raise ValueError("KIS_V2_BENCHMARK_UNVERIFIED")
    zone = ZoneInfo(MARKETS[market]["zone"])
    recent = {}
    for row in rows:
        if not isinstance(row, dict) or row.get("stck_bsop_date") != opened.astimezone(zone).strftime("%Y%m%d"):
            continue
        wire = row["stck_bsop_date"] + str(row.get("stck_cntg_hour", ""))
        if not re.fullmatch(r"[0-9]{14}", wire):
            raise ValueError("KIS_V2_BENCHMARK_UNVERIFIED")
        event = datetime.strptime(wire, "%Y%m%d%H%M%S").replace(tzinfo=zone)
        age = observed - event
        if event < opened or not timedelta(minutes=1) <= age < timedelta(seconds=120):
            continue
        level = Decimal(str(row.get(price)))
        if not level.is_finite() or level <= 0 or (event in recent and recent[event] != level):
            raise ValueError("KIS_V2_BENCHMARK_UNVERIFIED")
        recent[event] = level
    if not recent:
        raise ValueError("KIS_V2_BENCHMARK_UNVERIFIED")
    event = max(recent)
    return {"market": market, "symbol": symbol, "source": source, "unit": "index_points",
            "level": str(recent[event]), "event_at": event.isoformat(), "observed_at": observed.isoformat()}


def _buy_observation(root, market, currency, scope, ticker, now, seconds, account_cash, *, benchmark=None):
    prefix = market.lower() + "-v2-"
    evidence, evidence_digest = _reviewed_document(root / (prefix + "evidence.json"))
    schema = REGULAR_BENCHMARK_EVIDENCE_SCHEMA if benchmark is not None else EVIDENCE_SCHEMA
    if (evidence.get("schema") != schema or evidence.get("market") != market
            or evidence.get("currency") != currency or evidence.get("account_scope") != scope
            or evidence.get("cash_basis") != "REVIEWED_SETTLED_CASH"
            or evidence.get("orders_reconciled") is not True or evidence.get("portfolio_complete") is not True):
        raise ValueError("KIS V2 requires complete scoped cash, order and portfolio evidence")
    settlement_reference = evidence.get("settlement_source_sha256")
    market_index = evidence["benchmark"] if benchmark is None else benchmark
    if (market_index["market"] != market or (market_index["symbol"], market_index["source"]) != _BENCHMARKS[market]
            or market_index["unit"] != "index_points" or not isinstance(settlement_reference, str)
            or re.fullmatch(r"[0-9a-f]{64}", settlement_reference) is None):
        raise ValueError("KIS V2 lacks a benchmark identity or settlement source digest")
    settlement, _ = _reviewed_document(root / (prefix + "settlement.json"), settlement_reference)
    expected_settlement = {"schema": SETTLEMENT_SCHEMA, "account_scope": scope, "market": market, "currency": currency,
                           "observed_at": evidence["settlement_observed_at"], "settled_cash": evidence["settled_cash"]}
    if settlement != expected_settlement:
        raise ValueError("KIS V2 review does not match its settlement and benchmark sources")
    if benchmark is None:
        benchmark_reference = evidence.get("benchmark_source_sha256")
        if not isinstance(benchmark_reference, str) or re.fullmatch(r"[0-9a-f]{64}", benchmark_reference) is None:
            raise ValueError("KIS V2 lacks a benchmark source digest")
        reviewed_benchmark, _ = _reviewed_document(root / (prefix + "benchmark.json"), benchmark_reference)
        if reviewed_benchmark != market_index:
            raise ValueError("KIS V2 review does not match its settlement and benchmark sources")
    level = Decimal(str(market_index["level"]))
    if not level.is_finite() or level <= 0:
        raise ValueError("KIS V2 benchmark level is unverified")
    acquired = _stamp(evidence["observed_at"])
    benchmark_event = _stamp(market_index["event_at"])
    benchmark_at = _stamp(market_index["observed_at"])
    if (not benchmark_event <= benchmark_at <= now or (now - benchmark_event).total_seconds() > seconds
            or (benchmark is None and benchmark_at > acquired)
            or (benchmark is not None and benchmark_at - benchmark_event < timedelta(minutes=1))):
        raise ValueError("KIS V2 reviewed benchmark clock is unverified" if benchmark is None
                         else "KIS_V2_BENCHMARK_UNVERIFIED")
    for observed in (_stamp(evidence["settlement_observed_at"]), _stamp(evidence["portfolio_observed_at"])):
        if not observed <= acquired <= now or not 0 <= (now - observed).total_seconds() <= seconds:
            raise ValueError("KIS V2 observation expired or unavailable")
    cash = Decimal(str(evidence["settled_cash"]))
    if not cash.is_finite() or not 0 <= cash <= Decimal(str(account_cash)):
        raise ValueError("KIS V2 settled cash exceeds the native balance")
    return str(cash), evidence["target_weights"][ticker], evidence_digest


def current_v2_order_receipt(market, client, *, clock):
    """A complete dated VTS order query must show no remaining orders."""
    started = _stamp(clock())
    zone = ZoneInfo(MARKETS[market]["zone"])
    local_date = started.astimezone(zone).date()
    session_date = local_date.isoformat()
    rows = client.orders(local_date.strftime("%Y%m%d"))
    finished = _stamp(clock())
    if finished < started or finished.astimezone(zone).date() != local_date:
        raise ValueError("KIS V2 order inquiry crossed its observation window")
    remainder = "rmn_qty" if market == "KR" else "nccs_qty"
    if (not isinstance(rows, list) or any(not isinstance(row, dict) or not isinstance(row.get(remainder), str)
            or re.fullmatch(r"[0-9]+", row[remainder]) is None for row in rows)):
        raise ValueError("KIS V2 order remainder is unverified")
    # The overseas client already verifies the venue date and Korean wire time.
    if market == "KR":
        for row in rows:
            day, moment = row.get("ord_dt"), row.get("ord_tmd")
            if day != local_date.strftime("%Y%m%d") or not isinstance(moment, str) or not re.fullmatch(r"[0-9]{6}", moment):
                raise ValueError("KIS V2 order time is unverified")
            try:
                placed = datetime.strptime(day + moment, "%Y%m%d%H%M%S").replace(tzinfo=zone)
            except ValueError:
                raise ValueError("KIS V2 order time is unverified") from None
            if placed > finished:
                raise ValueError("KIS V2 order time is unverified")
    return {"mode": "demo", "market": market, "currency": _MARKETS[market][0],
            "account_scope": client.credentials.scope(), "source": "KIS_DEMO_ORDER_INQUIRY",
            "session_date": session_date, "observed_at": started.isoformat(), "ingested_at": finished.isoformat(),
            "open_order_count": sum(int(row[remainder]) != 0 for row in rows)}


def authorize_v2_size(root, market, settings, candidate, terms, quote, account, state, now, *, order_receipt, benchmark=None):
    """Apply V2 after native sizing, then leave the final authority with the broker."""
    if settings is None:
        return terms["quantity"], {}
    policy, watchlist = settings["policy"], settings["watchlist"]
    scope = account["account_scope"]
    currency, suffix = _MARKETS[market]
    if (policy["scope"] != scope or account.get("environment") != "demo" or account.get("complete") is not True
            or (account.get("market"), account.get("currency")) != (market, currency)
            or quote.get("currency") != currency):
        raise ValueError("KIS V2 account scope is unverified")
    account_at, account_ingested = (_stamp(account.get(key)) for key in ("observed_at", "ingested_at"))
    observed, ingested = (_stamp(order_receipt.get(key)) for key in ("observed_at", "ingested_at"))
    if (order_receipt.get("source") != "KIS_DEMO_ORDER_INQUIRY" or order_receipt.get("mode") != "demo"
            or order_receipt.get("market") != market or order_receipt.get("currency") != currency
            or order_receipt.get("account_scope") != scope or order_receipt.get("session_date")
            != now.astimezone(ZoneInfo(MARKETS[market]["zone"])).date().isoformat()
            or type(order_receipt.get("open_order_count")) is not int or order_receipt["open_order_count"] != 0
            or not account_at <= account_ingested <= observed <= ingested <= now
            or (now - account_at).total_seconds() >= policy["max_quote_age_seconds"]):
        raise ValueError("KIS_V2_ACCOUNT_ORDER_STATE_UNVERIFIED")
    bind_v2_journal(root, policy, watchlist, as_of=now.isoformat())
    ticker = candidate["ticker"]
    side, cash, target, evidence_hash = terms["side"], "0", 0, None
    if side == "BUY":
        if (settings.get("benchmark_basis") == REGULAR_BENCHMARK) != (benchmark is not None):
            raise ValueError("KIS_V2_BENCHMARK_UNVERIFIED")
        evaluation = state["evaluation"]
        if evaluation["sample"]["sell_filled_orders"] and not evaluation["settlement_known"]:
            raise ValueError("Prior KIS strategy sales require settlement proof")
        cash, target, evidence_hash = _buy_observation(root, market, currency, scope, ticker, now,
            policy["max_quote_age_seconds"], account[f"cash_{suffix}"], benchmark=benchmark)
    position = next((row for row in account["positions"] if row["ticker"] == terms["ticker"]), {})
    context = {"market": market, "currency": currency, "scope": scope}
    capacity = {**context, "mode": "isolated_paper", "reconciled": True,
                "observed_at": account["observed_at"], "nav": account[f"nav_{suffix}"],
                "settlement_verified": evidence_hash is not None, "portfolio_complete": evidence_hash is not None,
                "benchmark_fresh": evidence_hash is not None, "settled_cash": cash, "pending_buy_notional": 0,
                "pending_buys_by_ticker": {}, "positions": {ticker: {
                    "owned": position.get("quantity", 0), "sellable": position.get("sellable_quantity", 0), "pending_sell": 0}}}
    signal = candidate["signal"]
    source = {**context, "ticker": ticker, "action_now": signal["decision_now"],
              "observed_at": signal["available_at"], "execution_ready": signal["execution_ready"],
              "target_weight": target, "quantity": terms["quantity"], "verified_risk_reduction": side == "SELL"}
    price = terms["limit_price"]
    native_quote = {**context, "ticker": ticker, "observed_at": quote["observed_at"],
                    "regular_executable": quote.get("execution_ready") is True and quote.get("session") == "regular",
                    "ask": price, "bid": price}
    sized = size_v2_candidate(policy, watchlist, capacity, source, native_quote, as_of=now.isoformat())
    if sized["status"] != "PAPER_CANDIDATE" or sized.get("side") != side:
        raise ValueError(sized["status"])
    amount = int(sized["quantity"])
    evidence = {key: sized[key] for key in ("policy_sha256", "watchlist_sha256", "policy_version", "watchlist_version")} | {
        "reviewed_evidence_sha256": evidence_hash, "order_inquiry_observed_at": observed.isoformat(),
    }
    if benchmark is not None:
        evidence["benchmark"] = benchmark
    return amount, evidence
