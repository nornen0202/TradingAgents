"""Connect optional V2 sizing to the guarded native KIS strategy."""

from decimal import Decimal
import hashlib
import json
import re

from .experiments import _stamp
from .paper_policy_v2 import bind_v2_journal, size_v2_candidate

EVIDENCE_SCHEMA = "tradingagents.kis-v2-evidence/v1"
SETTLEMENT_SCHEMA = "tradingagents.kis-v2-reviewed-settlement/v1"
_MARKETS = {"KR": ("KRW", "krw"), "US": ("USD", "usd")}
_BENCHMARKS = {"KR": ("0001", "KIS_KR_INDEX"), "US": ("SPX", "KIS_US_INDEX")}


def configured_v2(config):
    rows = config.get("paper_policy_v2", {})
    if not isinstance(rows, dict) or set(rows) - set(_MARKETS):
        raise ValueError("KIS V2 settings must specify an explicit market")
    for market, row in rows.items():
        if (not isinstance(row, dict) or set(row) != {"policy", "watchlist"}
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


def _buy_observation(root, market, currency, scope, ticker, now, seconds, account_cash):
    prefix = market.lower() + "-v2-"
    evidence, evidence_digest = _reviewed_document(root / (prefix + "evidence.json"))
    if (evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("market") != market
            or evidence.get("currency") != currency or evidence.get("account_scope") != scope
            or evidence.get("cash_basis") != "REVIEWED_SETTLED_CASH"
            or evidence.get("orders_reconciled") is not True or evidence.get("portfolio_complete") is not True):
        raise ValueError("KIS V2 requires complete scoped cash, order and portfolio evidence")
    market_index = evidence["benchmark"]
    settlement_reference = evidence.get("settlement_source_sha256")
    benchmark_reference = evidence.get("benchmark_source_sha256")
    if (market_index["market"] != market or (market_index["symbol"], market_index["source"]) != _BENCHMARKS[market]
            or market_index["unit"] != "index_points" or any(
                not isinstance(reference, str) or re.fullmatch(r"[0-9a-f]{64}", reference) is None
                for reference in (settlement_reference, benchmark_reference))):
        raise ValueError("KIS V2 lacks a benchmark identity or settlement source digest")
    settlement, _ = _reviewed_document(root / (prefix + "settlement.json"), settlement_reference)
    benchmark, _ = _reviewed_document(root / (prefix + "benchmark.json"), benchmark_reference)
    expected_settlement = {"schema": SETTLEMENT_SCHEMA, "account_scope": scope, "market": market, "currency": currency,
                           "observed_at": evidence["settlement_observed_at"], "settled_cash": evidence["settled_cash"]}
    if settlement != expected_settlement or benchmark != market_index:
        raise ValueError("KIS V2 review does not match its settlement and benchmark sources")
    level = Decimal(str(market_index["level"]))
    if not level.is_finite() or level <= 0:
        raise ValueError("KIS V2 benchmark level is unverified")
    acquired = _stamp(evidence["observed_at"])
    benchmark_event = _stamp(market_index["event_at"])
    benchmark_at = _stamp(market_index["observed_at"])
    if benchmark_event > benchmark_at:
        raise ValueError("KIS benchmark clock cannot precede the index event")
    for observed in (benchmark_event, benchmark_at, _stamp(evidence["settlement_observed_at"]),
                     _stamp(evidence["portfolio_observed_at"])):
        if not observed <= acquired <= now or not 0 <= (now - observed).total_seconds() <= seconds:
            raise ValueError("KIS V2 observation expired or unavailable")
    cash = Decimal(str(evidence["settled_cash"]))
    if not cash.is_finite() or not 0 <= cash <= Decimal(str(account_cash)):
        raise ValueError("KIS V2 settled cash exceeds the native balance")
    return str(cash), evidence["target_weights"][ticker], evidence_digest


def authorize_v2_size(root, market, settings, candidate, terms, quote, account, state, now):
    """Apply V2 after native sizing, then leave the final authority with the broker."""
    if settings is None:
        return terms["quantity"], {}
    policy, watchlist = settings["policy"], settings["watchlist"]
    scope = account["account_scope"]
    currency, suffix = _MARKETS[market]
    if policy["scope"] != scope or account.get("environment") != "demo" or account.get("complete") is not True:
        raise ValueError("KIS V2 account scope is unverified")
    bind_v2_journal(root, policy, watchlist, as_of=now.isoformat())
    ticker = candidate["ticker"]
    side, cash, target, evidence_hash = terms["side"], "0", 0, None
    if side == "BUY":
        evaluation = state["evaluation"]
        if evaluation["sample"]["sell_filled_orders"] and not evaluation["settlement_known"]:
            raise ValueError("Prior KIS strategy sales require settlement proof")
        cash, target, evidence_hash = _buy_observation(root, market, currency, scope, ticker, now,
            policy["max_quote_age_seconds"], account[f"cash_{suffix}"])
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
    return amount, {key: sized[key] for key in ("policy_sha256", "watchlist_sha256", "policy_version", "watchlist_version")} | {
        "reviewed_evidence_sha256": evidence_hash,
    }
