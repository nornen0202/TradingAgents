"""Shared native-currency limits for the KIS strategy and its offline replay."""

from dataclasses import asdict, dataclass
import math

from .paper import order_nav_limit

CAPS = {"KR": 100_000, "US": 500}
_SUFFIX = {"KR": "krw", "US": "usd"}


@dataclass(frozen=True)
class KisStrategyLimits:
    max_order_native: int
    cash_floor_native: int
    max_order_nav: float
    one_share_nav_ceiling: float


def configured_limits(config):
    raw = config.get("native_order_limits", {})
    if not isinstance(raw, dict) or set(raw) - set(CAPS):
        raise ValueError("Native strategy limits must identify each market explicitly")
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


def size_with_native_limits(market, terms, account, limits):
    """Reduce an already authorized integer quantity to the configured native bounds."""
    if limits is None:
        return terms["quantity"]
    price = terms["limit_price"]
    quantity = min(terms["quantity"], math.floor(limits.max_order_native / price))
    if terms["side"] == "SELL":
        return quantity
    suffix = _SUFFIX[market]
    unit_cost = price * 1.003
    qty_nav = account[f"nav_{suffix}"] * order_nav_limit(limits, "BUY", terms["quantity"]) / unit_cost
    qty_cash = (account[f"cash_{suffix}"] - limits.cash_floor_native) / unit_cost
    return max(0, min(quantity, math.floor(qty_nav), math.floor(qty_cash)))


def make_strategy_broker(market, path, client, clock, tickers, limits):
    options = {}
    if limits is not None:
        suffix = _SUFFIX[market]
        options = {f"max_order_{suffix}": limits.max_order_native, f"cash_floor_{suffix}": limits.cash_floor_native,
                   "max_order_nav": limits.max_order_nav, "one_share_nav_ceiling": limits.one_share_nav_ceiling}
    if market == "KR":
        from .kis_paper import KisPaperBroker, PaperOrderPolicy
        policy = PaperOrderPolicy(tuple(ticker[:6] for ticker in tickers), **options)
        return KisPaperBroker(path, client, policy, paper_enabled=True, clock=clock)
    from .kis_paper_us import KisPaperUSBroker, USPaperOrderPolicy
    policy = USPaperOrderPolicy((), allowed_tickers=tickers, **options)
    return KisPaperUSBroker(path, client, policy, paper_enabled=True, clock=clock)
