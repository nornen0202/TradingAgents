import json
import pytest

from tradingagents.scheduled.trade_plan_sources import load_trade_plan_sources
from tradingagents.scheduled.trade_plan import build_trade_plan


@pytest.fixture
def source(tmp_path):
    run_id = "20260102T100000_github-actions-overlay-us"
    run = tmp_path / "runs" / "2026" / run_id
    private = run / "portfolio-private"
    private.mkdir(parents=True)
    snapshot = {
        "snapshot_id": "PRIVATE-SNAPSHOT",
        "account_id": "PRIVATE-ACCOUNT",
        "currency": "KRW",
        "as_of": "2026-01-02T10:02:00+09:00",
        "snapshot_health": "VALID",
        "available_cash_krw": 0,
        "buying_power_krw": 1000,
        "settled_cash_krw": 2000,
        "constraints": {"min_cash_buffer_krw": 50},
        "positions": [
            {
                "canonical_ticker": "LLY",
                "quantity": 0.436065,
                "available_qty": 0,
                "avg_cost_krw": 99,
                "broker_account_id": "PRIVATE-POSITION",
            }
        ],
        "cash_diagnostics": {"raw": {"secret": "SECRET"}},
        "pending_orders": [
            {
                "broker_order_id": "PRIVATE-ORDER",
                "canonical_ticker": "LLY",
                "side": "buy",
                "remaining_qty": 0.2,
            }
        ],
        "warnings": ["PRIVATE-WARNING"],
    }
    manifest = {
        "run_id": run_id,
        "settings": {"market": "US"},
        "status": "success",
        "started_at": "2026-01-02T10:00:00+09:00",
        "finished_at": "2026-01-02T10:03:00+09:00",
        "portfolio": {
            "status": "success",
            "artifacts": {
                "account_snapshot_json": "portfolio-private/account_snapshot.json"
            },
            "private_coverage_snapshot": {
                "snapshot_id": "PRIVATE-SNAPSHOT",
                "as_of": snapshot["as_of"],
                "holding_set_complete": True,
                "canonical_holding_tickers": ["LLY"],
            },
        },
    }
    market = {"market": "US", "run_id": run_id, "source": {"run_id": run_id}}

    def save():
        (run / "run.json").write_text(json.dumps(manifest), encoding="utf-8")
        (private / "account_snapshot.json").write_text(
            json.dumps(snapshot), encoding="utf-8"
        )

    save()
    return tmp_path, run, snapshot, manifest, market, save


def test_exact_snapshot_preserves_zero_and_fractional_quantity_without_identifiers(
    source,
):
    root, _, _, _, market, _ = source
    result = load_trade_plan_sources(root, market)
    assert result["status"] == "EXACT_RUN_ACCOUNT"
    assert result["account_snapshot"]["available_cash_krw"] == 0
    assert result["account_snapshot"]["positions"][0] == {
        "canonical_ticker": "LLY",
        "quantity": 0.436065,
        "available_qty": 0,
    }
    assert result["fx_krw_per_usd"] is None
    assert result["account_snapshot"]["pending_orders"] == [
        {"canonical_ticker": "LLY", "side": "buy", "remaining_qty": 0.2}
    ]
    assert "PRIVATE" not in json.dumps(result)
    assert "SECRET" not in json.dumps(result)


@pytest.mark.parametrize(
    "state", ["lookup_failed", "malformed", "unknown_ticker", "missing"]
)
def test_unverified_pending_orders_cannot_masquerade_as_available_cash(source, state):
    root, _, snapshot, _, market, save = source
    if state == "lookup_failed":
        snapshot["pending_orders"] = []
        snapshot["warnings"] = [
            "KIS overseas pending-order lookup failed; continuing with balance-only account snapshot."
        ]
    elif state == "malformed":
        snapshot["pending_orders"][0]["remaining_qty"] = float("nan")
    elif state == "unknown_ticker":
        snapshot["pending_orders"][0]["canonical_ticker"] = None
    else:
        snapshot.pop("pending_orders")
    save()
    result = load_trade_plan_sources(root, market)
    assert result["account_snapshot"] is None
    assert result["reason"] == "PENDING_ORDERS_UNVERIFIED"


@pytest.mark.parametrize(
    "manifest_status,portfolio_status,reason",
    [
        ("partial_failure", "success", "SOURCE_RUN_PARTIAL_FAILURE"),
        ("failed", "success", "SOURCE_RUN_INCOMPLETE"),
        ("success", "failed", "PORTFOLIO_RUN_INCOMPLETE"),
    ],
)
def test_analysis_failure_is_not_mislabeled_pending_order_failure(
    source, manifest_status, portfolio_status, reason
):
    root, _, snapshot, manifest, market, save = source
    snapshot["pending_orders"] = []
    snapshot["warnings"] = []
    manifest["status"] = manifest_status
    manifest["portfolio"]["status"] = portfolio_status
    save()
    inputs = load_trade_plan_sources(root, market)
    assert inputs["account_snapshot"] is None
    assert inputs["reason"] == reason
    market["rows"] = [
        {
            "ticker": "LLY",
            "is_held": True,
            "portfolio_action": {
                "action_now": "HOLD",
                "delta_krw_now": 0,
                "action_if_triggered": "REDUCE_IF_TRIGGERED",
                "delta_krw_if_triggered": -1000,
            },
        }
    ]
    plan = build_trade_plan(
        market,
        account_snapshot=inputs["account_snapshot"],
        account_source_reason=inputs["reason"],
    )
    assert plan["account_asof"] is None
    row = plan["rows"][0]
    assert row["quantity"] is None
    assert row["order_ready"] is False
    assert (
        "정상 완료" in row["reasons"][0] or "일부 종목 분석이 실패" in row["reasons"][0]
    )
    assert all("미체결" not in message for message in row["reasons"])


def test_loader_never_returns_raw_exception_text(source, monkeypatch):
    import tradingagents.scheduled.trade_plan_sources as sources

    root, _, _, _, market, _ = source

    def fail(path):
        raise ValueError("PRIVATE-ACCOUNT C:/private/account_snapshot.json")

    monkeypatch.setattr(sources, "_object", fail)
    result = load_trade_plan_sources(root, market)
    assert result["reason"] == "EXACT_RUN_ACCOUNT_NOT_VERIFIED"
    assert "PRIVATE-ACCOUNT" not in json.dumps(result)
    assert "C:/private" not in json.dumps(result)


@pytest.mark.parametrize(
    "change",
    [
        "cross_run",
        "coverage_time",
        "coverage_incomplete",
        "holdings_missing",
        "source_mismatch",
        "invalid_quantity",
        "duplicate",
        "future",
        "market",
        "missing_cash",
    ],
)
def test_rejects_unverified_binding_or_incomplete_sizing(source, change):
    root, _, snapshot, manifest, market, save = source
    if change == "cross_run":
        manifest["portfolio"]["artifacts"]["account_snapshot_json"] = (
            "../another/portfolio-private/account_snapshot.json"
        )
    elif change == "coverage_time":
        manifest["portfolio"]["private_coverage_snapshot"]["as_of"] = (
            "2026-01-02T10:01:00+09:00"
        )
    elif change == "coverage_incomplete":
        manifest["portfolio"]["private_coverage_snapshot"]["holding_set_complete"] = (
            False
        )
    elif change == "holdings_missing":
        manifest["portfolio"]["private_coverage_snapshot"][
            "canonical_holding_tickers"
        ] = ["LLY", "AAPL"]
    elif change == "source_mismatch":
        market["source"]["run_id"] = "other"
    elif change == "invalid_quantity":
        snapshot["positions"][0]["available_qty"] = float("nan")
    elif change == "duplicate":
        snapshot["positions"].append(snapshot["positions"][0])
    elif change == "future":
        manifest["finished_at"] = "2099-01-02T10:03:00+09:00"
    elif change == "market":
        manifest["settings"]["market"] = "KR"
    else:
        snapshot.pop("buying_power_krw")
    save()
    result = load_trade_plan_sources(root, market)
    assert result["account_snapshot"] is None
    assert result["status"] == "UNAVAILABLE"


def test_explicit_reference_fx_and_invalid_direction(source):
    root, _, snapshot, _, market, save = source
    snapshot["cash_diagnostics"]["fx_quote"] = {
        "base_currency": "USD",
        "quote_currency": "KRW",
        "rate": 1391.5,
        "observed_at": "2026-01-02T10:02:10+09:00",
        "source": "kis.inquire_present_balance.output2.frst_bltn_exrt",
        "kind": "BROKER_REFERENCE_RATE",
    }
    save()
    result = load_trade_plan_sources(root, market)
    assert result["fx_krw_per_usd"] == 1391.5
    assert result["fx_status"] == "BROKER_REFERENCE_RATE"
    snapshot["cash_diagnostics"]["fx_quote"]["base_currency"] = "JPY"
    save()
    result = load_trade_plan_sources(root, market)
    assert result["account_snapshot"] is not None
    assert result["fx_krw_per_usd"] is None


def test_rejects_outside_absolute_path_even_when_valid_snapshot(source):
    root, run, snapshot, manifest, market, save = source
    outside = root / "account_snapshot.json"
    outside.write_text(json.dumps(snapshot), encoding="utf-8")
    manifest["portfolio"]["artifacts"]["account_snapshot_json"] = str(outside)
    save()
    assert load_trade_plan_sources(root, market)["account_snapshot"] is None
    manifest["portfolio"]["artifacts"]["account_snapshot_json"] = str(
        run / "portfolio-private/account_snapshot.json"
    )
    save()
    assert load_trade_plan_sources(root, market)["account_snapshot"] is not None


def test_rejects_oversized_snapshot_and_traversal_id(source):
    root, run, _, _, market, _ = source
    (run / "portfolio-private/account_snapshot.json").write_text(
        " " * (2 * 1024 * 1024 + 1)
    )
    assert load_trade_plan_sources(root, market)["account_snapshot"] is None
    market["run_id"] = "../outside"
    market["source"]["run_id"] = "../outside"
    assert load_trade_plan_sources(root, market)["account_snapshot"] is None


def test_rejects_conflicting_duplicate_run(source):
    root, run, _, manifest, market, _ = source
    duplicate = root / "runs" / "duplicate" / run.name
    duplicate.mkdir(parents=True)
    (duplicate / "run.json").write_text(json.dumps(manifest))
    assert load_trade_plan_sources(root, market)["account_snapshot"] is None


def test_known_sizing_constraints_are_preserved(source):
    root, _, snapshot, _, market, save = source
    snapshot["constraints"].update(
        min_trade_krw=100_000, max_order_count_per_day=5, max_single_name_weight=0.35
    )
    save()
    loaded = load_trade_plan_sources(root, market)["account_snapshot"]["constraints"]
    assert loaded["min_trade_krw"] == 100_000
    assert loaded["max_order_count_per_day"] == 5
    assert loaded["max_single_name_weight"] == 0.35
    snapshot["constraints"]["max_single_name_weight"] = 1.2
    save()
    assert load_trade_plan_sources(root, market)["account_snapshot"] is None
