from __future__ import annotations

from datetime import date, timedelta

from tradingagents.dataflows.intraday.microstructure import KISMicrostructureProvider
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
    snapshot = KISMicrostructureProvider(client=IncompleteUsKisClient()).fetch(
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
