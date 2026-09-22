"""Local paper execution from KIS-derived snapshots. No broker write capability.

Each account has its own SQLite ledger. All cash/prices use the snapshot's KRW
valuation basis (including US positions). This is a shadow simulator, not KIS VTS.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import sqlite3


@dataclass(frozen=True)
class PaperLimits:
    cash_floor: float = 2_500_000
    max_order_nav: float = 0.01
    max_sell_order_nav: float = 0.20
    one_share_nav_ceiling: float = (
        0.0  # Optional, separately configured paper experiment.
    )
    max_single_name: float = 0.35
    max_daily_turnover: float = 0.10
    max_daily_orders: int = 5
    max_daily_loss: float = 0.02
    daily_loss_reduce_only: bool = True
    max_quote_age_seconds: int = 120
    slippage_bps: float = 10
    fee_bps: float = 5
    sell_tax_bps: float = 20  # Conservative research assumption, not a tax quote.

    def __post_init__(self):
        if type(self.daily_loss_reduce_only) is not bool:
            raise ValueError("daily_loss_reduce_only must be boolean")
        if any(
            not math.isfinite(float(v)) or float(v) < 0 for v in asdict(self).values()
        ):
            raise ValueError("Limits must be finite and nonnegative")
        if not 0 < self.max_order_nav <= 1 or not 0 < self.max_single_name <= 1:
            raise ValueError("Invalid position limits")
        if (
            not 0 < self.max_sell_order_nav <= 1
            or not 0 <= self.one_share_nav_ceiling <= self.max_single_name
        ):
            raise ValueError("Invalid sell/whole-share limits")
        if not 0 < self.max_daily_turnover <= 1 or not 0 < self.max_daily_loss <= 1:
            raise ValueError("Invalid daily limits")
        if type(self.max_daily_orders) is not int or self.max_daily_orders <= 0:
            raise ValueError("Daily order count must be a positive integer")


def stamp(value: str) -> datetime:
    result = datetime.fromisoformat(value)
    if result.tzinfo is None:
        raise ValueError("Timezone-aware timestamp required")
    return result


def positive(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value > 0
    )


class PaperBroker:
    def __init__(self, path: Path, limits: PaperLimits | None = None):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, isolation_level=None, timeout=20)
        self.db.row_factory = sqlite3.Row
        self.limits = limits or PaperLimits()
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS state(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS positions(ticker TEXT PRIMARY KEY, qty REAL NOT NULL, price REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY, ticker TEXT NOT NULL, side TEXT NOT NULL,
                qty INTEGER NOT NULL, limit_price REAL NOT NULL, created_at TEXT NOT NULL,
                status TEXT NOT NULL, reason TEXT NOT NULL, expires_at TEXT NOT NULL,
                filled_at TEXT, fill_price REAL, cost REAL);
            CREATE TABLE IF NOT EXISTS observations(at TEXT PRIMARY KEY, nav REAL NOT NULL, cash REAL NOT NULL);
        """)

    def close(self):
        self.db.close()

    def _get(self, key, default=None):
        row = self.db.execute("SELECT value FROM state WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def _set(self, key, value):
        self.db.execute(
            "INSERT OR REPLACE INTO state VALUES (?,?)", (key, json.dumps(value))
        )

    def seed(self, snapshot: dict):
        """One-time clone; never re-import a changing live account over paper fills."""
        stamp(snapshot["as_of"])
        if snapshot.get("snapshot_health", "VALID") not in {
            "VALID",
            "CAPITAL_CONSTRAINED",
        }:
            raise ValueError("Complete valid account snapshot required")
        if snapshot.get("pending_orders"):
            raise ValueError("Resolve source pending orders before cloning account")
        cash = snapshot.get("available_cash_krw")
        if not isinstance(cash, (int, float)) or not math.isfinite(cash) or cash < 0:
            raise ValueError("Valid cash required")
        positions = snapshot.get("positions", [])
        seen = set()
        for p in positions:
            ticker, qty, price = (
                p["canonical_ticker"],
                p["quantity"],
                p["market_price_krw"],
            )
            if ticker in seen or not positive(qty) or not positive(price):
                raise ValueError("Unique positive positions and marks required")
            seen.add(ticker)
        # Preserve valuation-only foreign cash/other cash without assuming it is
        # buying power. Never silently seed a different NAV from the source.
        marked = sum(p["quantity"] * p["market_price_krw"] for p in positions)
        total = snapshot.get("account_value_krw", marked + cash)
        if not positive(total) or total < marked:
            raise ValueError("Cannot reconcile account NAV and position marks")
        valuation_cash = total - marked
        buying_power = snapshot.get("buying_power_krw", cash)
        if (
            not isinstance(buying_power, (float, int))
            or not math.isfinite(buying_power)
            or buying_power < 0
        ):
            raise ValueError("Valid buying power required")
        spendable = min(cash, buying_power, valuation_cash)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            if self._get("seeded"):
                raise ValueError("Paper ledger already seeded")
            self._set("cash", valuation_cash)
            self._set("spendable", spendable)
            self._set("seeded", True)
            self._set("seed_asof", snapshot["as_of"])
            self._set("seed_nav", total)
            self._set("limits", asdict(self.limits))
            for p in positions:
                self.db.execute(
                    "INSERT INTO positions VALUES (?,?,?)",
                    (p["canonical_ticker"], p["quantity"], p["market_price_krw"]),
                )
            self.db.execute("COMMIT")
        except Exception:
            self.db.execute("ROLLBACK")
            raise

    def step(
        self, *, now: str, quotes: dict, signals: list[dict], halted: bool = False
    ):
        """Fill at a strictly later fresh snapshot; then queue explicit signals.

        A quote requires price_krw, as_of, session='regular', executable=True and
        spread_bps. Quotes/flags are trusted adapter inputs, never inferred from prose.
        Paper orders expire at the local calendar-day boundary; each ledger uses
        market-local now. US fills use fixed quote FX normalization, not FX trading.
        """
        at = stamp(now)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            if not self._get("seeded"):
                raise ValueError("Seed account first")
            if self._get("limits") != asdict(self.limits):
                raise ValueError("Limits changed: use a separate paper experiment")
            previous = self._get("last_step")
            if at < stamp(self._get("seed_asof")):
                raise ValueError("Cannot observe before account snapshot")
            if previous and at <= stamp(previous):
                raise ValueError("Clock must advance")
            valid = {}
            for ticker, q in quotes.items():
                age = (at - stamp(q["as_of"])).total_seconds()
                spread = q.get("spread_bps")
                if (
                    0 <= age <= self.limits.max_quote_age_seconds
                    and positive(q.get("price_krw"))
                    and q.get("session") == "regular"
                    and q.get("executable") is True
                    and isinstance(spread, (float, int))
                    and math.isfinite(spread)
                    and 0 <= spread <= 100
                ):
                    valid[ticker] = q
            for ticker, q in valid.items():
                self.db.execute(
                    "UPDATE positions SET price=? WHERE ticker=?",
                    (q["price_krw"], ticker),
                )
            cash = self._get("cash")
            spendable = self._get("spendable")
            nav = (
                cash
                + self.db.execute(
                    "SELECT coalesce(sum(qty*price),0) FROM positions"
                ).fetchone()[0]
            )
            day = at.date().isoformat()
            if self._get("day") != day:
                self._set("day", day)
                baseline = (
                    self._get("seed_nav", nav)
                    if not previous
                    and stamp(self._get("seed_asof")).date() == at.date()
                    else nav
                )
                self._set("day_start_nav", baseline)
                self._set("turnover", 0)
                self._set("order_count", 0)
                self._set("daily_stopped", False)
            risk_stop = self._get("daily_stopped", False) or nav <= self._get(
                "day_start_nav"
            ) * (1 - self.limits.max_daily_loss)
            self._set("daily_stopped", risk_stop)
            missing_marks = any(
                r["qty"] and r["ticker"] not in valid
                for r in self.db.execute("SELECT * FROM positions")
            )
            # A kill switch also cancels pending paper orders, including risk sells.
            for order in self.db.execute(
                "SELECT * FROM orders WHERE status='PENDING'"
            ).fetchall():
                if (
                    halted
                    or (
                        risk_stop
                        and (
                            order["side"] == "BUY"
                            or not self.limits.daily_loss_reduce_only
                        )
                    )
                    or at >= stamp(order["expires_at"])
                    or stamp(order["created_at"]).date() != at.date()
                ):
                    self.db.execute(
                        "UPDATE orders SET status='CANCELLED',reason=? WHERE id=?",
                        ("kill_or_daily_stop_or_expired", order["id"]),
                    )
                    continue
                q = valid.get(order["ticker"])
                if not q or stamp(q["as_of"]) <= stamp(order["created_at"]):
                    continue
                sign = 1 if order["side"] == "BUY" else -1
                fill = q["price_krw"] * (
                    1 + sign * (q["spread_bps"] / 2 + self.limits.slippage_bps) / 10000
                )
                if (sign == 1 and fill > order["limit_price"]) or (
                    sign == -1 and fill < order["limit_price"]
                ):
                    continue
                qty = order["qty"]
                holding = self.db.execute(
                    "SELECT qty FROM positions WHERE ticker=?", (order["ticker"],)
                ).fetchone()
                held = holding[0] if holding else 0
                fees = (
                    qty
                    * fill
                    * (
                        self.limits.fee_bps
                        + (self.limits.sell_tax_bps if sign < 0 else 0)
                    )
                    / 10000
                )
                if sign > 0 and (
                    missing_marks
                    or qty * fill + fees > spendable
                    or cash - qty * fill - fees < self.limits.cash_floor
                    or (held + qty) * q["price_krw"] > nav * self.limits.max_single_name
                ):
                    continue
                if sign < 0 and qty > held:
                    raise ValueError("Paper position would become short")
                if (
                    self._get("turnover") + qty * fill
                    > self._get("day_start_nav") * self.limits.max_daily_turnover
                    or qty * fill
                    > nav * order_nav_limit(self.limits, order["side"], qty)
                ):
                    continue
                cash -= sign * qty * fill + fees
                spendable -= sign * qty * fill + fees
                self.db.execute(
                    "INSERT INTO positions VALUES (?,?,?) ON CONFLICT(ticker) DO UPDATE SET qty=excluded.qty, price=excluded.price",
                    (order["ticker"], held + sign * qty, q["price_krw"]),
                )
                self.db.execute(
                    "UPDATE orders SET status='FILLED',filled_at=?,fill_price=?,cost=? WHERE id=?",
                    (now, fill, fees, order["id"]),
                )
                self._set("turnover", self._get("turnover") + qty * fill)
                nav = (
                    cash
                    + self.db.execute(
                        "SELECT coalesce(sum(qty*price),0) FROM positions"
                    ).fetchone()[0]
                )
                risk_stop = risk_stop or nav <= self._get("day_start_nav") * (
                    1 - self.limits.max_daily_loss
                )
                self._set("daily_stopped", risk_stop)
            for s in signals:
                key = hashlib.sha256(
                    f"{s['signal_id']}|{s['ticker']}|{s['action']}".encode()
                ).hexdigest()
                if self.db.execute(
                    "SELECT 1 FROM orders WHERE id=?", (key,)
                ).fetchone():
                    continue
                q = valid.get(s["ticker"])
                action = s["action"]
                reason = None
                if halted or (
                    risk_stop
                    and (action == "BUY" or not self.limits.daily_loss_reduce_only)
                ):
                    reason = "kill_or_daily_stop"
                elif (
                    action not in {"BUY", "REDUCE", "SELL"}
                    or s.get("execution_ready") is not True
                ):
                    reason = "no_explicit_executable_action"
                elif (
                    not s.get("valid_until")
                    or at >= stamp(s["valid_until"])
                    or at < stamp(s["available_at"])
                ):
                    reason = "signal_expired_or_future"
                elif not q:
                    reason = "quote_not_executable"
                elif self._get("order_count") >= self.limits.max_daily_orders:
                    reason = "daily_order_limit"
                elif self.db.execute(
                    "SELECT 1 FROM orders WHERE ticker=? AND status='PENDING'",
                    (s["ticker"],),
                ).fetchone():
                    reason = "pending_order_exists"
                elif action == "BUY" and missing_marks:
                    reason = "incomplete_account_marks"
                holding = self.db.execute(
                    "SELECT qty FROM positions WHERE ticker=?", (s["ticker"],)
                ).fetchone()
                held = holding[0] if holding else 0
                side = "BUY" if action == "BUY" else "SELL"
                price = q["price_krw"] if q else 0
                # Explicit requested integer quantity; never guess lots from prose.
                requested = s.get("quantity")
                qty = requested if type(requested) is int and requested > 0 else 0
                if not reason and not qty:
                    reason = s.get("sizing_reason") or "missing_integer_quantity"
                if not reason:
                    cap = math.floor(
                        nav * order_nav_limit(self.limits, side, qty) / price
                    )
                    qty = min(qty, cap, math.floor(held) if side == "SELL" else qty)
                    if qty <= 0:
                        reason = "whole_share_budget_or_holdings"
                    elif side == "BUY" and (
                        qty
                        * price
                        * (
                            1
                            + (
                                self.limits.fee_bps
                                + self.limits.slippage_bps
                                + q["spread_bps"] / 2
                            )
                            / 10000
                        )
                        > spendable
                        or cash
                        - qty
                        * price
                        * (
                            1
                            + (
                                self.limits.fee_bps
                                + self.limits.slippage_bps
                                + q["spread_bps"] / 2
                            )
                            / 10000
                        )
                        < self.limits.cash_floor
                        or (held + qty) * price > nav * self.limits.max_single_name
                    ):
                        reason = "cash_floor_or_concentration"
                limit = price * (1.003 if side == "BUY" else 0.997) if price else 0
                self.db.execute(
                    "INSERT INTO orders(id,ticker,side,qty,limit_price,created_at,status,reason,expires_at) VALUES (?,?,?,?,?,?,?,?,?)",
                    (
                        key,
                        s["ticker"],
                        side,
                        qty,
                        limit,
                        now,
                        "REJECTED" if reason else "PENDING",
                        reason or "next_snapshot_required",
                        s.get("valid_until") or now,
                    ),
                )
                if not reason:
                    self._set("order_count", self._get("order_count") + 1)
            self._set("cash", cash)
            self._set("spendable", spendable)
            self._set("last_step", now)
            nav = (
                cash
                + self.db.execute(
                    "SELECT coalesce(sum(qty*price),0) FROM positions"
                ).fetchone()[0]
            )
            self.db.execute("INSERT INTO observations VALUES (?,?,?)", (now, nav, cash))
            self.db.execute("COMMIT")
            return {
                "mode": "LOCAL_PAPER_ONLY",
                "broker_orders_sent": 0,
                "as_of": now,
                "nav_krw": nav,
                "cash_krw": cash,
                "marks_complete": not missing_marks,
                "trading_state": "HALTED"
                if halted or (risk_stop and not self.limits.daily_loss_reduce_only)
                else "REDUCING"
                if risk_stop
                else "ACTIVE",
                "orders": [
                    dict(r)
                    for r in self.db.execute(
                        "SELECT * FROM orders ORDER BY created_at,id"
                    )
                ],
            }
        except Exception:
            self.db.execute("ROLLBACK")
            raise


def order_nav_limit(limits: PaperLimits, side: str, quantity: int):
    if side == "SELL":
        return limits.max_sell_order_nav
    if quantity == 1:
        return max(limits.max_order_nav, limits.one_share_nav_ceiling)
    return limits.max_order_nav


def kis_demo_order_preview(*, ticker: str, side: str, quantity: int, limit_price: int):
    """Credential-free KR KIS VTS mapping for integration tests. Never sends.

    Account number/product code must be bound in a future separately reviewed
    sandbox transport. The real endpoint deliberately does not exist here.
    """
    if len(ticker) != 6 or not ticker.isascii() or not ticker.isdigit():
        raise ValueError("Six-digit KR security required")
    if (
        side not in {"BUY", "SELL"}
        or type(quantity) is not int
        or quantity <= 0
        or type(limit_price) is not int
        or limit_price <= 0
    ):
        raise ValueError("Positive integer quantity/limit and BUY/SELL required")
    return {
        "send_enabled": False,
        "environment": "demo",
        "base_url": "https://openapivts.koreainvestment.com:29443",
        "path": "/uapi/domestic-stock/v1/trading/order-cash",
        "tr_id": "VTTC0012U" if side == "BUY" else "VTTC0011U",
        "body": {
            "PDNO": ticker,
            "ORD_DVSN": "00",
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(limit_price),
            "EXCG_ID_DVSN_CD": "KRX",
        },
    }
