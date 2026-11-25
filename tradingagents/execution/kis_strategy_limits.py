"""Shared native-currency limits for the KIS strategy and its offline replay."""

from dataclasses import asdict, dataclass
from decimal import Decimal
import json
import math

from .kis_demo import DemoError
from .paper import order_nav_limit

CAPS = {"KR": 100_000, "US": 500}
APPROVED_LIMIT_REVISION = "VTS_NATIVE_ORDER_LIMITS_20261125"
DAILY_LIMIT_REVISION = "VTS_NATIVE_DAILY_BUY_LIMITS_V1"
APPROVED_CAPS = {"KR": 3_000_000, "US": 3_000}
LEGACY_DAILY_BUY = {"KR": 300_000, "US": 1_000}
_SUFFIX = {"KR": "krw", "US": "usd"}


@dataclass(frozen=True)
class KisStrategyLimits:
    max_order_native: int
    cash_floor_native: int
    max_order_nav: float
    one_share_nav_ceiling: float


def approved_limits():
    return {market: KisStrategyLimits(cap, 0, .12, .20) for market, cap in APPROVED_CAPS.items()}


def configured_limits(config):
    raw = config.get("native_order_limits", {})
    if not isinstance(raw, dict) or set(raw) - set(CAPS):
        raise ValueError("Native strategy limits must identify each market explicitly")
    if "native_limit_revision" in config:
        revision = config["native_limit_revision"]
        expected = approved_limits()
        daily = config.get("native_daily_buy_limits")
        valid_daily = (json.dumps(daily, sort_keys=True) == json.dumps(APPROVED_CAPS, sort_keys=True)
                       if revision == DAILY_LIMIT_REVISION else "native_daily_buy_limits" not in config)
        if (not isinstance(revision, str) or revision not in {APPROVED_LIMIT_REVISION, DAILY_LIMIT_REVISION} or not valid_daily
                or config.get("mode") != "KIS_DEMO_STRATEGY"
                or config.get("real_orders_enabled") is not False
                or json.dumps(raw, sort_keys=True) != json.dumps({market: asdict(limits) for market, limits in expected.items()}, sort_keys=True)):
            raise ValueError("Approved VTS sizing requires the exact scoped native policy")
        return expected
    if "native_daily_buy_limits" in config:
        raise ValueError("Daily VTS limits require an approved native policy revision")
    limits = {}
    for market, row in raw.items():
        if not isinstance(row, dict) or set(row) != set(KisStrategyLimits.__dataclass_fields__):
            raise ValueError("Native limits require currency amount, cash floor, and both NAV limits")
        policy = KisStrategyLimits(**row)
        if (type(policy.max_order_native) is not int or not 1 <= policy.max_order_native <= CAPS[market]
                or type(policy.cash_floor_native) is not int or policy.cash_floor_native < 0
                or policy.max_order_nav is None):
            raise ValueError("Native amount must respect the market's hard cap and nonnegative cash floor")
        validate_buy_nav(policy.max_order_nav, policy.one_share_nav_ceiling, .35)
        limits[market] = policy
    return limits


def validate_buy_nav(normal, one_share, concentration):
    if normal is None and type(one_share) in (float, int) and one_share == 0:
        return  # Older native journals have no relative limit.
    if (type(normal) not in (int, float) or type(one_share) not in (int, float)
            or not 0 < normal <= concentration or not 0 <= one_share <= concentration):
        raise ValueError("Native buy NAV limits must remain within the concentration limit")


def broker_policy_fields(policy):
    fields = asdict(policy)
    if policy.max_order_nav is None:
        fields.pop("max_order_nav")
        fields.pop("one_share_nav_ceiling")
    return fields


def bind_broker_policy(db, scope, market, fields, revision):
    """Preserve the original policy and order history under a recorded VTS amendment."""
    encoded = json.dumps(fields, sort_keys=True)
    previous = db.execute("SELECT policy FROM paper_policy WHERE scope=?", (scope,)).fetchone()
    if revision is None:
        if previous and previous[0] != encoded:
            raise DemoError("Policy changed; use a separately named paper journal")
        db.execute("INSERT OR IGNORE INTO paper_policy VALUES (?,?)", (scope, encoded))
        return
    limit = approved_limits()[market]
    amount_key = f"max_order_{_SUFFIX[market]}"
    daily_key = f"max_daily_buy_{_SUFFIX[market]}"
    baseline = {key: value for key, value in fields.items() if key not in {"max_order_nav", "one_share_nav_ceiling"}}
    baseline[amount_key] = CAPS[market]
    if revision == DAILY_LIMIT_REVISION:
        baseline[daily_key] = LEGACY_DAILY_BUY[market]
    baseline_encoded = json.dumps(baseline, sort_keys=True)
    amended = {amount_key: limit.max_order_native, "max_order_nav": limit.max_order_nav,
               "one_share_nav_ceiling": limit.one_share_nav_ceiling}
    if revision == DAILY_LIMIT_REVISION:
        amended[daily_key] = APPROVED_CAPS[market]
    if (revision not in {APPROVED_LIMIT_REVISION, DAILY_LIMIT_REVISION} or fields != baseline | amended
            or fields.get(f"cash_floor_{_SUFFIX[market]}") != limit.cash_floor_native
            or (previous and previous[0] != baseline_encoded)):
        raise DemoError("Approved VTS revision does not match the original risk policy")
    db.execute("""CREATE TABLE IF NOT EXISTS paper_policy_revisions(
        scope TEXT NOT NULL, revision TEXT NOT NULL, baseline TEXT NOT NULL, policy TEXT NOT NULL,
        PRIMARY KEY(scope, revision))""")
    db.execute("""CREATE TRIGGER IF NOT EXISTS paper_policy_revisions_no_update BEFORE UPDATE ON paper_policy_revisions
        BEGIN SELECT RAISE(ABORT,'VTS policy revisions are immutable'); END""")
    db.execute("""CREATE TRIGGER IF NOT EXISTS paper_policy_revisions_no_delete BEFORE DELETE ON paper_policy_revisions
        BEGIN SELECT RAISE(ABORT,'VTS policy revisions are immutable'); END""")
    saved = db.execute("SELECT baseline,policy FROM paper_policy_revisions WHERE scope=? AND revision=?", (scope, revision)).fetchone()
    if saved and tuple(saved) != (baseline_encoded, encoded):
        raise DemoError("Approved VTS revision conflicts with its journal evidence")
    db.execute("INSERT OR IGNORE INTO paper_policy VALUES (?,?)", (scope, baseline_encoded))
    db.execute("INSERT OR IGNORE INTO paper_policy_revisions VALUES (?,?,?,?)", (scope, revision, baseline_encoded, encoded))


def size_with_native_limits(market, terms, account, limits):
    """Reduce an already authorized integer quantity to the configured native bounds."""
    if limits is None:
        return terms["quantity"]
    price = Decimal(str(terms["limit_price"]))
    quantity = min(terms["quantity"], int(limits.max_order_native // price))
    if terms["side"] == "SELL":
        return quantity
    suffix = _SUFFIX[market]
    unit_cost = reserved_cost(price, 30)
    nav = Decimal(str(account[f"nav_{suffix}"]))
    cash = Decimal(str(account[f"cash_{suffix}"])) - limits.cash_floor_native
    qty_cash = math.floor(cash / unit_cost)
    affordable = max(0, min(quantity, qty_cash))
    qty_nav = math.floor(nav * Decimal(str(order_nav_limit(limits, "BUY", affordable))) / unit_cost)
    if affordable > 1 and qty_nav == 0 and unit_cost <= nav * Decimal(str(limits.one_share_nav_ceiling)):
        return 1
    return max(0, min(affordable, qty_nav))


def reserved_cost(notional, reserve_bps):
    return Decimal(str(notional)) * (1 + Decimal(reserve_bps) / 10_000)


def within_buy_nav(notional, quantity, nav, policy):
    return (policy.max_order_nav is None or reserved_cost(notional, policy.reserve_cost_bps)
            <= Decimal(str(nav)) * Decimal(str(order_nav_limit(policy, "BUY", quantity))))


def within_daily_buy_limit(committed, requested, *, cap, reserve_bps, revision):
    total = Decimal(str(committed)) + Decimal(str(requested))
    if revision == DAILY_LIMIT_REVISION:
        total = reserved_cost(total, reserve_bps)
    return total <= cap


def daily_buy_commitment(original, observed, revision):
    """Release only a broker-confirmed cancelled remainder from the daily budget."""
    quantity = original["quantity"]
    if revision == DAILY_LIMIT_REVISION and observed["order_status"] == "CANCELLED":
        filled = observed["filled"]
        if type(filled) is int and 0 <= filled <= quantity:
            quantity = filled
    return quantity * Decimal(str(original["limit_price"]))


def make_strategy_broker(market, path, client, clock, tickers, limits, *, revision=None):
    options = {}
    if limits is not None:
        suffix = _SUFFIX[market]
        options = {f"max_order_{suffix}": limits.max_order_native, f"cash_floor_{suffix}": limits.cash_floor_native,
                   "max_order_nav": limits.max_order_nav, "one_share_nav_ceiling": limits.one_share_nav_ceiling}
        if revision == DAILY_LIMIT_REVISION:
            options[f"max_daily_buy_{suffix}"] = APPROVED_CAPS[market]
    if market == "KR":
        from .kis_paper import KisPaperBroker, PaperOrderPolicy
        policy = PaperOrderPolicy(tuple(ticker[:6] for ticker in tickers), **options)
        return KisPaperBroker(path, client, policy, paper_enabled=True, clock=clock, strategy_policy_revision=revision)
    from .kis_paper_us import KisPaperUSBroker, USPaperOrderPolicy
    policy = USPaperOrderPolicy((), allowed_tickers=tickers, **options)
    return KisPaperUSBroker(path, client, policy, paper_enabled=True, clock=clock, strategy_policy_revision=revision)
