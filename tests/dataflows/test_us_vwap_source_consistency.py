from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from tradingagents.dataflows.intraday import microstructure
from tradingagents.dataflows.intraday_market import DELAYED_ANALYSIS_ONLY


NOW = datetime(2026, 10, 1, 10, 0, tzinfo=ZoneInfo("America/New_York"))


class FrozenDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        return NOW.astimezone(tz) if tz is not None else NOW.replace(tzinfo=None)


class QuoteClient:
    def __init__(self, *, price=None, detail=None, bars=None):
        self.price = {"last": "100.6801", "high": "100.69", "low": "100.68", **(price or {})}
        self.detail = detail or {}
        self.bars = bars or []
        self.include_previous = None

    def overseas_price(self, symbol, *, exchange):
        return {"output": self.price}

    def overseas_price_detail(self, symbol, *, exchange):
        return {"output": self.detail}

    def overseas_time_itemchartprice(self, symbol, *, exchange, nmin, include_previous, nrec):
        self.include_previous = include_previous
        return {"output2": self.bars}, {}


def bar(clock, *, day="20261001", price=100.685, volume=100):
    return {
        "xymd": day, "xhms": clock, "last": str(price),
        "high": str(price), "low": str(price),
        "evol": str(volume), "eamt": str(price * volume),
    }


def regular_bars():
    return [bar(clock) for clock in ("100000", "095500", "095000", "094500", "094000", "093500", "093000")]


def snapshot(monkeypatch, client, *, interval="5m"):
    monkeypatch.setattr(microstructure, "datetime", FrozenDatetime)
    return microstructure.KISMicrostructureProvider(
        client=client, us_daily_volume_fallback=lambda _: 10000,
        us_supplement_provider=None,
    ).fetch("SGOV", interval=interval, market_timezone="America/New_York")


def test_cumulative_amount_and_volume_are_never_merged_across_responses(monkeypatch):
    client = QuoteClient(
        price={"tvol": "500"},
        detail={"tamt": "40274", "tvol": "400", "low": "100.68", "high": "100.69"},
    )
    result = snapshot(monkeypatch, client)
    assert result.session_vwap == pytest.approx(100.685)
    assert result.session_vwap != pytest.approx(40274 / 500)


def test_unpaired_amount_cannot_borrow_volume_from_other_response(monkeypatch):
    result = snapshot(monkeypatch, QuoteClient(price={"tvol": "500"}, detail={"tamt": "50342.5"}))
    assert result.session_vwap is None
    assert "session_vwap" in result.missing_reason


def test_public_sgov_range_conflict_is_rejected_at_source_not_repriced(monkeypatch):
    # Reproduces the published range/value contradiction, not a claim about its
    # unseen original broker response or the security's current price.
    bad_vwap = 100.99662260070097
    result = snapshot(monkeypatch, QuoteClient(price={"tvol": "1000", "tamt": str(bad_vwap * 1000)}))
    assert result.last_price == 100.6801
    assert result.session_vwap is None
    assert result.missing_reason["session_vwap"] == "source_vwap_price_range_inconsistent"
    assert result.execution_data_quality == DELAYED_ANALYSIS_ONLY


def test_documented_evol_eamt_fields_compute_regular_session_vwap(monkeypatch):
    bars = regular_bars()
    bars[0] = bar("100000", price=100.69, volume=200)
    bars[-1] = bar("093000", price=100.68)
    client = QuoteClient(bars=bars)
    result = snapshot(monkeypatch, client)
    assert client.include_previous == "0"
    assert result.session_vwap == pytest.approx((100.69 * 200 + 100.68 * 100 + 100.685 * 500) / 800)
    assert result.volume == 800


def test_prior_day_extended_hours_and_future_bars_never_enter_session_vwap(monkeypatch):
    client = QuoteClient(bars=regular_bars() + [
        bar("150000", day="20260930", price=200),
        bar("090000", price=300), bar("160500", price=400),
        bar("100500", price=500),
    ])
    result = snapshot(monkeypatch, client)
    assert result.session_vwap == pytest.approx(100.685)
    assert result.volume == 700


def test_rolling_window_missing_open_cannot_be_called_session_vwap(monkeypatch):
    result = snapshot(monkeypatch, QuoteClient(bars=[bar("100000"), bar("095500")]), interval="1m")
    assert result.session_vwap is None
    assert result.missing_reason["session_vwap"] == "regular_session_bar_coverage_incomplete"


def test_missing_bar_dates_do_not_inherit_today(monkeypatch):
    result = snapshot(monkeypatch, QuoteClient(bars=[{"xhms": "093000", "evol": "100", "eamt": "10068.5"}]))
    assert result.session_vwap is None


def test_candidate_without_its_own_range_is_not_validated_against_other_response(monkeypatch):
    result = snapshot(monkeypatch, QuoteClient(detail={"tvol": "1000", "tamt": "100685"}))
    assert result.session_vwap is None
    assert result.missing_reason["session_vwap"] == "source_vwap_price_range_unavailable"


def test_previous_day_bar_timestamp_remains_stale_even_after_filtering(monkeypatch):
    result = snapshot(monkeypatch, QuoteClient(bars=[bar("150000", day="20260930")]))
    assert result.session_vwap is None
    assert result.asof == "2026-09-30T15:00:00-04:00"
    assert result.quote_delay_seconds == 19 * 60 * 60


@pytest.mark.parametrize("omit", [{"094500"}, {"095500", "100000"}])
def test_missing_middle_or_tail_bars_cannot_be_called_session_vwap(monkeypatch, omit):
    bars = [row for row in regular_bars() if row["xhms"] not in omit]
    result = snapshot(monkeypatch, QuoteClient(bars=bars))
    assert result.session_vwap is None
    assert result.missing_reason["session_vwap"] == "regular_session_bar_coverage_incomplete"


def test_identical_duplicate_bars_do_not_double_count_volume(monkeypatch):
    result = snapshot(monkeypatch, QuoteClient(bars=regular_bars() + [bar("094500")]))
    assert result.session_vwap == pytest.approx(100.685)
    assert result.volume == 700


def test_conflicting_duplicate_bar_timestamp_blocks_fallback(monkeypatch):
    result = snapshot(monkeypatch, QuoteClient(bars=regular_bars() + [bar("094500", volume=200)]))
    assert result.session_vwap is None
    assert result.missing_reason["minute_bars"] == "conflicting_duplicate_bar_timestamp"


def test_missing_halt_status_is_unknown_not_clear(monkeypatch):
    result = snapshot(monkeypatch, QuoteClient())
    assert result.halt_status == {"status": "unknown", "is_clear": False}
    assert result.missing_reason["halt_status"] == "halt_status_not_confirmed_by_snapshot"


def test_explicit_clear_halt_status_is_preserved(monkeypatch):
    result = snapshot(monkeypatch, QuoteClient(price={"halt_yn": "0"}))
    assert result.halt_status["is_clear"] is True
    assert "halt_status" not in result.missing_reason


@pytest.mark.parametrize("value", [None, "", " "])
def test_empty_halt_field_is_unknown_not_clear(monkeypatch, value):
    result = snapshot(monkeypatch, QuoteClient(price={"halt_yn": value}))
    assert result.halt_status["is_clear"] is False
    assert result.missing_reason["halt_status"] == "halt_status_not_confirmed_by_snapshot"


def test_early_close_bounds_exclude_after_hours_bars():
    now = datetime(2026, 11, 27, 14, 0, tzinfo=ZoneInfo("America/New_York"))
    missing = {}
    bounds = microstructure._us_session_bounds(now)
    rows = [bar("130000", day="20261127"), bar("130500", day="20261127", price=300)]
    selected = microstructure._us_regular_session_bars(rows, now_local=now, bounds=bounds, missing=missing)
    assert [row["xhms"] for row in selected] == ["130000"]
