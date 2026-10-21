from __future__ import annotations

from datetime import date, timedelta

import pytest

from tradingagents.dataflows.intraday.microstructure import KISMicrostructureProvider, render_microstructure_report
from tradingagents.dataflows.intraday.us_microstructure_sources import USMicrostructureSupplement
from tradingagents.dataflows.intraday_market import DELAYED_ANALYSIS_ONLY


class FakeKisClient:
    def domestic_price(self, code):
        return {
            "output": {
                "stck_prpr": "105",
                "stck_hgpr": "108",
                "stck_lwpr": "99",
                "acml_vol": "1000",
                "acml_tr_pbmn": "102000",
                "vi_cls_code": "0",
                "mrkt_warn_cls_code": "0",
            }
        }

    def domestic_time_itemchartprice(self, code, *, input_hour, include_past_data):
        today = date.today().strftime("%Y%m%d")
        return {
            "output2": [
                {"stck_bsop_date": today, "stck_cntg_hour": "100000", "stck_prpr": "105", "cntg_vol": "500"},
                {"stck_bsop_date": today, "stck_cntg_hour": "093500", "stck_prpr": "99", "cntg_vol": "500"},
            ]
        }

    def domestic_asking_price(self, code):
        return {
            "output1": {
                "bidp1": "104",
                "askp1": "106",
                "bidp_rsqn1": "600",
                "askp_rsqn1": "400",
            }
        }

    def domestic_time_itemconclusion(self, code, *, input_hour):
        return {"output2": [{"cntg_vol": "100", "ccld_dvsn": "매수"}, {"cntg_vol": "50", "ccld_dvsn": "매도"}]}

    def domestic_investor_trend_estimate(self, code):
        return {"output2": [{"bsop_hour": "100000", "frgn_ntby_qty": "1000", "orgn_ntby_qty": "500"}]}

    def domestic_program_trade_by_stock(self, code):
        return {"output": [{"bsop_hour": "100000", "pgtr_ntby_qty": "300"}]}

    def domestic_comp_program_trade_today(self, *, market_class, input_hour):
        return {"output": [{"bsop_hour": "100000", "arbt_ntby_qty": "200"}]}

    def domestic_daily_itemchartprice(self, code, *, start_date, end_date):
        return {"output2": [{"acml_vol": "1000"} for _ in range(20)]}

    def overseas_price(self, symbol, *, exchange, auth=""):
        if exchange != "NAS":
            raise RuntimeError("wrong exchange")
        return {
            "output": {
                "LAST": "200",
                "HIGH": "205",
                "LOW": "195",
                "TVOL": "10000",
                "TAMT": "1990000",
                "halt_yn": "0",
                "STRN": "125",
            }
        }

    def overseas_price_detail(self, symbol, *, exchange, auth=""):
        return {"output": {"LAST": "200"}}

    def overseas_time_itemchartprice(self, symbol, *, exchange, nmin, include_previous, nrec):
        today = date.today().strftime("%Y%m%d")
        return (
            {
                "output2": [
                    {"XYMD": today, "XHMS": "100000", "LAST": "200", "TVOL": "5000"},
                    {"XYMD": today, "XHMS": "093500", "LAST": "198", "TVOL": "5000"},
                ]
            },
            {},
        )

    def overseas_asking_price(self, symbol, *, exchange, auth=""):
        return {"output1": {"pbid1": "199", "pask1": "201", "vbid1": "700", "vask1": "300"}}

    def overseas_quot_inquire_ccnl(self, symbol, *, exchange, today="1"):
        return ({"output1": [{"EVOL": "100", "MTYP": "2"}]}, {})

    def overseas_volume_power(self, *, exchange):
        return ({"output2": [{"symb": "AAPL", "rank": "1"}]}, {})

    def fetch_overseas_daily_price_history(self, *, symbol, exchange_code, start_date, end_date):
        return [{"TVOL": "10000"} for _ in range(20)]


class FakeNysKisClient(FakeKisClient):
    def overseas_price(self, symbol, *, exchange, auth=""):
        if exchange == "NAS":
            return {"output": {"rsym": f"DNAS{symbol}"}}
        if exchange != "NYS":
            raise RuntimeError("wrong exchange")
        return {
            "output": {
                "LAST": "193",
                "HIGH": "194",
                "LOW": "188",
                "TVOL": "12000",
                "TAMT": "2292000",
                "halt_yn": "0",
                "STRN": "130",
            }
        }


class RealisticDomesticTapeKisClient(FakeKisClient):
    def domestic_price(self, code):
        payload = super().domestic_price(code)
        payload["output"].pop("cttr", None)
        payload["output"].pop("tbuy_cntg_strength", None)
        payload["output"]["mrkt_warn_cls_code"] = "00"
        return payload

    def domestic_time_itemconclusion(self, code, *, input_hour):
        return {
            "output2": [
                {
                    "stck_cntg_hour": "145835",
                    "stck_prpr": "105",
                    "askp": "106",
                    "bidp": "104",
                    "tday_rltv": "109.30",
                    "acml_vol": "1000",
                    "cnqn": "7",
                }
            ]
        }


class IncompleteUsKisClient(FakeKisClient):
    def overseas_price(self, symbol, *, exchange, auth=""):
        if exchange != "NAS":
            raise RuntimeError("wrong exchange")
        return {
            "output": {
                "LAST": "200",
                "HIGH": "205",
                "LOW": "195",
                "TVOL": "10000",
                "TAMT": "1990000",
                "halt_yn": "0",
            }
        }

    def overseas_asking_price(self, symbol, *, exchange, auth=""):
        return {"output1": {}}

    def overseas_quot_inquire_ccnl(self, symbol, *, exchange, today="1"):
        return ({"output1": []}, {})

    def fetch_overseas_daily_price_history(self, *, symbol, exchange_code, start_date, end_date):
        return []


class FakeReadyUsSupplementProvider:
    def fetch(self, symbol, *, now_local, interval):
        return USMicrostructureSupplement(
            avg20_daily_volume=10000.0,
            spread_bps=10.0,
            orderbook_imbalance=0.25,
            execution_strength=140.0,
            trade_tape_summary={"rows": 2, "method": "quote_rule_then_tick_rule"},
            raw_source_names=("massive.aggregates_daily", "massive.last_nbbo", "massive.trades"),
            limited_reason={"execution_strength": "estimated_from_massive_trades_and_nbbo_quote"},
        )


class FakeLimitedUsSupplementProvider:
    def fetch(self, symbol, *, now_local, interval):
        return USMicrostructureSupplement(
            avg20_daily_volume=10000.0,
            spread_bps=10.0,
            orderbook_imbalance=0.25,
            execution_strength=140.0,
            trade_tape_summary={"rows": 2, "method": "quote_rule_then_tick_rule"},
            raw_source_names=("alpaca.iex.daily_bars", "alpaca.iex.latest_quote", "alpaca.iex.trades"),
            limited_reason={
                "daily_volume": "alpaca_feed=iex; non_consolidated",
                "orderbook": "alpaca_feed=iex; non_consolidated",
                "execution_strength": "alpaca_feed=iex; non_consolidated",
            },
            pilot_blockers=("orderbook_iex_limited", "execution_strength_iex_limited"),
        )


def test_kr_microstructure_snapshot_normalizes_kis_fields():
    snapshot = KISMicrostructureProvider(client=FakeKisClient()).fetch(
        "005930.KS",
        market_timezone="Asia/Seoul",
        checkpoint_id="10:35",
    )

    assert snapshot.market == "KR"
    assert snapshot.session_vwap == 102.0
    assert snapshot.relative_volume is not None
    assert snapshot.spread_bps is not None
    assert snapshot.orderbook_imbalance is not None
    assert snapshot.execution_strength == 200.0
    assert snapshot.investor_flow_status == "available"
    assert snapshot.program_flow_status == "available"
    assert snapshot.vi_status["is_clear"] is True
    assert snapshot.market_alert_status["is_clear"] is True


class DomesticVwapClient(FakeKisClient):
    def __init__(self, *, price=None, bars=None):
        self.price = price or {}
        self.bars = bars or []

    def domestic_price(self, code):
        payload = super().domestic_price(code)
        payload["output"].update(self.price)
        return payload

    def domestic_time_itemchartprice(self, code, *, input_hour, include_past_data):
        return {"output2": self.bars}


@pytest.mark.parametrize("day", ["20261013", "20261014"])
def test_kr_cumulative_minute_amount_never_supplies_session_vwap(day):
    # Reproduces zero pre-open quote totals with prior-session minute bars.
    # The same rolling window is also insufficient during the current session.
    result = KISMicrostructureProvider(client=DomesticVwapClient(
        price={"stck_prpr": "232000", "stck_hgpr": "0", "stck_lwpr": "0",
               "acml_vol": "0", "acml_tr_pbmn": "0"},
        bars=[
            {"stck_bsop_date": day, "stck_cntg_hour": "195900",
             "stck_prpr": "234000", "cntg_vol": "5448", "acml_tr_pbmn": "5916362713500"},
            {"stck_bsop_date": day, "stck_cntg_hour": "195800",
             "stck_prpr": "234000", "cntg_vol": "3307", "acml_tr_pbmn": "5915088589500"},
        ],
    )).fetch("005930.KS", market_timezone="Asia/Seoul")
    assert result.last_price == 232000
    assert result.session_vwap is None
    assert result.missing_reason["session_vwap"] == "cumulative_traded_value_or_volume_unavailable"
    assert result.execution_data_quality == DELAYED_ANALYSIS_ONLY
    assert result.asof.startswith(f"{day[:4]}-{day[4:6]}-{day[6:8]}")


@pytest.mark.parametrize("price,reason", [
    ({"acml_vol": "0"}, "cumulative_traded_value_or_volume_unavailable"),
    ({"acml_vol": None}, "cumulative_traded_value_or_volume_unavailable"),
    ({"acml_tr_pbmn": None}, "cumulative_traded_value_or_volume_unavailable"),
    ({"acml_tr_pbmn": "1000000000"}, "source_vwap_price_range_inconsistent"),
    ({"acml_tr_pbmn": "0"}, "source_vwap_price_range_inconsistent"),
    ({"acml_tr_pbmn": "-102000"}, "source_vwap_price_range_inconsistent"),
    ({"acml_tr_pbmn": "inf"}, "source_vwap_price_range_inconsistent"),
    ({"acml_tr_pbmn": "nan"}, "source_vwap_price_range_inconsistent"),
    ({"stck_lwpr": None}, "source_vwap_price_range_unavailable"),
    ({"stck_hgpr": None}, "source_vwap_price_range_unavailable"),
    ({"stck_lwpr": "0", "stck_hgpr": "0"}, "source_vwap_price_range_inconsistent"),
    ({"stck_lwpr": "108", "stck_hgpr": "99"}, "source_vwap_price_range_inconsistent"),
    ({"stck_hgpr": "inf"}, "source_vwap_price_range_inconsistent"),
])
def test_kr_invalid_cumulative_vwap_cannot_borrow_bar_range_or_volume(price, reason):
    result = KISMicrostructureProvider(client=DomesticVwapClient(
        price=price,
        bars=[{"stck_prpr": "102", "stck_hgpr": "108", "stck_lwpr": "99",
               "cntg_vol": "1000", "tr_pbmn": "102000"}],
    )).fetch("005930.KS", market_timezone="Asia/Seoul")
    assert result.session_vwap is None
    assert result.missing_reason["session_vwap"] == reason
    assert result.execution_data_quality == DELAYED_ANALYSIS_ONLY


def test_bar_vwap_never_divides_cumulative_amount_by_interval_volume():
    from tradingagents.dataflows.intraday.microstructure import _vwap_from_bars

    assert _vwap_from_bars([
        {"stck_prpr": "100", "cntg_vol": "10", "acml_tr_pbmn": "9000000"},
        {"stck_prpr": "103", "cntg_vol": "20", "acml_tr_pbmn": "10000000"},
    ]) == 102


def test_kr_microstructure_uses_kis_tday_rltv_and_clear_00_market_alert_code():
    snapshot = KISMicrostructureProvider(client=RealisticDomesticTapeKisClient()).fetch(
        "005930.KS",
        market_timezone="Asia/Seoul",
        checkpoint_id="14:35",
    )

    assert snapshot.execution_strength == 109.3
    assert snapshot.market_alert_status["is_clear"] is True
    assert snapshot.execution_data_quality != DELAYED_ANALYSIS_ONLY
    assert "execution_strength" not in snapshot.missing_reason
    assert "market_alert_status" not in snapshot.missing_reason


def test_us_microstructure_marks_kr_flow_fields_not_applicable():
    snapshot = KISMicrostructureProvider(client=FakeKisClient()).fetch(
        "AAPL",
        market_timezone="America/New_York",
        checkpoint_id="10:00",
    )

    assert snapshot.market == "US"
    assert snapshot.exchange == "NAS"
    assert snapshot.session_vwap == 199.0
    assert snapshot.relative_volume is not None
    assert snapshot.spread_bps is not None
    assert snapshot.execution_strength == 125.0
    assert snapshot.halt_status["is_clear"] is True
    assert snapshot.investor_flow_status == "not_applicable"
    assert snapshot.program_flow_status == "not_applicable"
    assert snapshot.volume_power_rank["rank"] == 1


def test_us_microstructure_keeps_probing_until_price_row_has_last_price():
    snapshot = KISMicrostructureProvider(client=FakeNysKisClient()).fetch(
        "CRM",
        market_timezone="America/New_York",
        checkpoint_id="13:00",
    )

    assert snapshot.market == "US"
    assert snapshot.exchange == "NYS"
    assert snapshot.last_price == 193.0
    assert snapshot.halt_status["is_clear"] is True


def test_us_microstructure_quality_degrades_when_required_fields_are_missing():
    snapshot = KISMicrostructureProvider(
        client=IncompleteUsKisClient(),
        us_daily_volume_fallback=lambda _symbol: None,
    ).fetch(
        "NTAP",
        market_timezone="America/New_York",
        checkpoint_id="13:00",
    )

    assert snapshot.execution_data_quality == DELAYED_ANALYSIS_ONLY
    assert snapshot.data_quality == DELAYED_ANALYSIS_ONLY
    assert snapshot.investor_flow_status == "not_applicable"
    assert snapshot.program_flow_status == "not_applicable"
    assert snapshot.halt_status["is_clear"] is True
    assert snapshot.missing_reason["relative_volume"] == "avg20_daily_volume_unavailable"
    assert snapshot.missing_reason["orderbook"] == "kis_orderbook_fields_unavailable"
    assert snapshot.missing_reason["execution_strength"] == "kis_trade_strength_field_unavailable"


def test_us_microstructure_uses_yfinance_daily_volume_fallback_for_rvol():
    snapshot = KISMicrostructureProvider(
        client=IncompleteUsKisClient(),
        us_daily_volume_fallback=lambda _symbol: 10000.0,
    ).fetch(
        "NTAP",
        market_timezone="America/New_York",
        checkpoint_id="13:00",
    )

    assert snapshot.relative_volume is not None
    assert snapshot.avg20_daily_volume == 10000.0
    assert "relative_volume" not in snapshot.missing_reason
    assert "yfinance.daily_history" in snapshot.raw_source_names
    assert snapshot.execution_data_quality == DELAYED_ANALYSIS_ONLY


def test_us_microstructure_uses_external_supplement_for_missing_orderbook_and_strength():
    snapshot = KISMicrostructureProvider(
        client=IncompleteUsKisClient(),
        us_daily_volume_fallback=lambda _symbol: None,
        us_supplement_provider=FakeReadyUsSupplementProvider(),
    ).fetch(
        "NTAP",
        market_timezone="America/New_York",
        checkpoint_id="13:00",
    )

    assert snapshot.relative_volume is not None
    assert snapshot.spread_bps == 10.0
    assert snapshot.orderbook_imbalance == 0.25
    assert snapshot.execution_strength == 140.0
    assert snapshot.execution_data_quality == ""
    assert "orderbook" not in snapshot.missing_reason
    assert snapshot.missing_reason["execution_strength"] == "estimated_from_massive_trades_and_nbbo_quote"
    assert "massive.last_nbbo" in snapshot.raw_source_names


def test_us_microstructure_external_limited_feed_blocks_realtime_quality():
    snapshot = KISMicrostructureProvider(
        client=IncompleteUsKisClient(),
        us_daily_volume_fallback=lambda _symbol: None,
        us_supplement_provider=FakeLimitedUsSupplementProvider(),
    ).fetch(
        "NTAP",
        market_timezone="America/New_York",
        checkpoint_id="13:00",
    )

    assert snapshot.spread_bps == 10.0
    assert snapshot.execution_strength == 140.0
    assert snapshot.execution_data_quality == DELAYED_ANALYSIS_ONLY
    assert snapshot.missing_reason["orderbook"] == "alpaca_feed=iex; non_consolidated"
    assert "alpaca.iex.latest_quote" in snapshot.raw_source_names


def test_microstructure_report_shows_external_sources_and_limited_fields():
    snapshot = KISMicrostructureProvider(
        client=IncompleteUsKisClient(),
        us_daily_volume_fallback=lambda _symbol: None,
        us_supplement_provider=FakeReadyUsSupplementProvider(),
    ).fetch(
        "NTAP",
        market_timezone="America/New_York",
        checkpoint_id="13:00",
    )

    report = render_microstructure_report(snapshot)

    assert "| Spread bps | 10 |" in report
    assert "| Execution strength | 140 |" in report
    assert "- execution_strength: estimated_from_massive_trades_and_nbbo_quote" in report
    assert "massive.last_nbbo" in report


@pytest.mark.parametrize("bar_time,book_time,expected_asof", [
    ("103000", "233025", "2026-10-20T10:30:00-04:00"),
    ("103100", "233025", "2026-10-20T10:31:00-04:00"),
    ("103000", "232955", "2026-10-20T23:29:55+09:00"),
])
@pytest.mark.parametrize("halt_feed", ["unavailable", "clear", "halted", "failed"])
@pytest.mark.parametrize("ticker,broker_symbol", [("AAPL", "AAPL"), ("BRK-B", "BRK/B"), ("BRK.B", "BRK/B")])
def test_us_actual_response_parts_use_native_evidence_without_supplement(monkeypatch, bar_time, book_time, expected_asof, halt_feed, ticker, broker_symbol):
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from tradingagents.dataflows.intraday import microstructure as module
    fixed = datetime(2026, 10, 20, 10, 30, 30, tzinfo=ZoneInfo('America/New_York'))
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed.astimezone(tz)
    monkeypatch.setattr(module, 'datetime', Clock)
    class Client(FakeKisClient):
        def overseas_price(self, symbol, **kwargs):
            assert symbol == broker_symbol
            return {'output': {'last': '200', 'high': '205', 'low': '195', 'tvol': '10000', 'tamt': '1990000'}}
        def overseas_time_itemchartprice(self, symbol, **kwargs):
            assert symbol == broker_symbol
            return {'output2': [{'xymd': '20261020', 'xhms': bar_time, 'last': '200', 'evol': '5000'}]}, {}
        def overseas_asking_price(self, symbol, **kwargs):
            assert symbol == broker_symbol
            return {'output1': {'code': symbol, 'curr': 'USD', 'dymd': '20261020', 'dhms': book_time},
                    'output2': {'pbid1': '199', 'pask1': '201', 'vbid1': '700', 'vask1': '300'}}
        def overseas_quot_inquire_ccnl(self, symbol, **kwargs):
            assert symbol == broker_symbol
            return {'output1': {'nrec': '1'}, 'output2': [{'khms': '233023', 'vpow': '81.75', 'mtyp': '2'}]}, {}
        def fetch_overseas_daily_price_history(self, **kwargs):
            assert kwargs['symbol'] == broker_symbol
            assert kwargs['end_date'] < fixed.date()
            return [{'xymd': (fixed.date() - timedelta(days=i)).strftime('%Y%m%d'), 'tvol': '10000'} for i in range(1,21)]
    class NoFallback:
        def fetch(self, *args, **kwargs):
            pytest.fail('Native evidence must not trigger delayed external fallbacks')
    class Halts:
        def fetch(self, symbol, **kwargs):
            assert symbol == ('AAPL' if ticker == 'AAPL' else 'BRK-B')
            if halt_feed == "failed":
                raise ValueError("HALT_FEED_STALE_OR_FUTURE")
            return {"status": halt_feed, "is_clear": halt_feed == "clear",
                    "source": "nasdaq.current_trade_halts", "published_at": fixed.isoformat(),
                    "observed_at": fixed.isoformat(), "as_of": fixed.isoformat(),
                    "basis": "CURRENT_DAY_HALT_FEED_PLUS_DATED_TRADED_BAR", "symbol": symbol}
    snapshot = KISMicrostructureProvider(client=Client(), us_daily_volume_fallback=lambda _: None,
                                        us_supplement_provider=NoFallback(),
                                        us_halt_provider=None if halt_feed == "unavailable" else Halts()).fetch(ticker, interval='1m')
    assert snapshot.execution_strength == 81.75
    assert snapshot.spread_bps == 100
    assert snapshot.avg20_daily_volume == 10000
    assert snapshot.asof == expected_asof
    assert snapshot.bar_timestamp == ('2026-10-20T10:31:00-04:00' if bar_time == '103100' else '2026-10-20T10:30:00-04:00')
    assert (snapshot.execution_data_quality == DELAYED_ANALYSIS_ONLY) == (halt_feed != "clear")
    assert snapshot.halt_status['is_clear'] == (halt_feed == "clear")
    assert snapshot.reg_sho_status['status'] == 'not_applicable_long_only'
    assert snapshot.reg_sho_status['is_clear'] is None
    for field in ['luld_status', 'news_halt_status']:
        assert getattr(snapshot, field)['status'] == (halt_feed if halt_feed in {'clear', 'halted'} else 'not_available_by_provider')
    assert snapshot.luld_status['price_bands_available'] is False
    if halt_feed == "clear":
        assert "halt_status" not in snapshot.missing_reason
    else:
        assert "halt_status" in snapshot.missing_reason
