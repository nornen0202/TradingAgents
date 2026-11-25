import hashlib
import json
from datetime import date, datetime, timedelta

import pytest

from tradingagents.scheduled.strategy_research import (
    _basis_compatible, _close_records, _compare, _price_checks, _retain_previous_close, _retain_previous_kr_close,
    previous_market_closes,
)
from tradingagents.portfolio.kis import KisClient
from tradingagents.scheduled.strategy_krx_close import KrxResearchCloses
from tradingagents.scheduled.strategy_research_prices import KR_DAILY, KisResearchCloses, market_days, price_epoch, validated_quote
from tradingagents.scheduled.strategy_research_sources import ResearchArchive, thesis_for


def dt(value):
    return datetime.fromisoformat(value)


@pytest.mark.parametrize(("age", "kind"), [(1, "REGULAR_QUOTE"), (71, "DELAYED_REGULAR_QUOTE"),
                                           (90, "DELAYED_REGULAR_QUOTE"), (120, "DELAYED_REGULAR_QUOTE"),
                                           (-1, None)])
def test_quote_delay_with_us_session_across_kst_midnight(age, kind):
    now = dt("2026-11-25T02:47:48+09:00")
    at = now - timedelta(minutes=age)
    quote = {"price": 351.64, "event_at": at.isoformat(), "observed_at": at.isoformat(), "source": "kis_microstructure",
             "category": "REALTIME_EXECUTION_READY", "exchange": "NAS", "market_session": "regular"}
    result = validated_quote(quote, "US", market_days("US", now), now)
    assert (result or {}).get("kind") == kind
    if kind:
        assert result["session"] == "2026-11-24"
        assert result["age_seconds"] == age * 60
    assert validated_quote(quote | {"currency": "KRW"}, "US", market_days("US", now), now) is None
    assert validated_quote(quote | {"adjustment": "split_adjusted"}, "US", market_days("US", now), now) is None


@pytest.mark.parametrize(("report_at", "kr", "us"), [
    ("2026-11-25T02:47:48+09:00", "2026-11-24", "2026-11-23"),
    ("2026-11-27T09:00:00+09:00", "2026-11-26", "2026-11-25"),  # Thanksgiving
    ("2026-11-29T12:00:00+09:00", "2026-11-27", "2026-11-27"),  # early close
    ("2026-07-18T12:00:00+09:00", "2026-07-16", "2026-07-17"),  # Constitution Day
])
def test_completed_session_epoch(report_at, kr, us):
    assert price_epoch(dt(report_at)) == (kr, us)


def test_dst_changes_us_market_clock():
    after = dt("2026-03-09T21:00:00+00:00")
    days = market_days("US", after)
    assert days[date(2026, 3, 6)][1] == dt("2026-03-06T21:00:00+00:00")
    assert days[date(2026, 3, 9)][1] == dt("2026-03-09T20:00:00+00:00")


def _bar(day, window, price, *, currency="USD", adjusted=None, observed=None):
    at = window[1]
    received = observed or at + timedelta(minutes=6)
    return {"kind": "REGULAR_CLOSE", "source": "KIS", "session": day.isoformat(), "currency": currency,
            "exchange": "NAS", "adjustment": "unadjusted", "event_at": at.isoformat(), "price": price,
            "observed_at": received.isoformat(), "adjustment_checked_at": received.isoformat(),
            "adjusted_close": price if adjusted is None else adjusted}


def test_basis_requires_anchor_currency_and_no_adjustment_change():
    now = dt("2026-11-26T22:00:00+00:00")
    days = market_days("US", now)
    ref, later = date(2026, 11, 23), date(2026, 11, 24)
    analysis = days[ref][1] + timedelta(hours=1)
    chart = {"ticker": "AAPL", "providers": ["yfinance"], "bars": [
        {"interval": "1d", "session_id": str(ref), "timestamp": days[ref][1].isoformat(),
         "observed_at": analysis.isoformat(), "close": 100}]}
    origin = "run", {"ticker": "AAPL"}, {}, {}, ref, analysis, chart
    anchor = _bar(ref, days[ref], 100)
    for later_bar, expected in (
        (_bar(later, days[later], 101), True),
        (_bar(later, days[later], 101, adjusted=50.5), False),
        (_bar(later, days[later], 101, currency="KRW"), False),
        (_bar(later, days[later], 101, observed=now + timedelta(seconds=1)), False),
        (_bar(later, days[later], 101, observed=days[later][1]), False),
    ):
        closes = _close_records({ref: anchor, later: later_bar}, "US", days, now)
        assert _basis_compatible(origin, closes, days, later, now) == expected


def test_close_sequence_preserves_group_and_waits_for_actual_next_session():
    first = date(2026, 11, 25)
    following = date(2026, 11, 27)
    now = dt("2026-11-26T22:00:00+00:00")
    days = market_days("US", now)
    threshold = {"level_type": "BREAKOUT", "price": 100, "confirmation": "close", "currency": "USD",
                 "confirmation_group": "reclaim", "source_text": "100달러 이상 정규장 종가"}
    retest = {"level_type": "PULLBACK", "low": 100, "high": 102, "confirmation": "next_day", "currency": "USD",
              "confirmation_group": "reclaim"}
    thesis = {"analysis_asof": "2026-11-25T17:00:00+00:00",
              "conditional_entry_valid_until": "2026-11-28T04:00:00+00:00",
              "execution_levels": {"levels": [threshold, retest]}}
    closes = {first: _bar(first, days[first], 100)}
    checks = _price_checks(thesis, closes, None, days, now, currency="USD", compatible=True, active=True)
    assert [(c["group"], c["status"]) for c in checks] == [("reclaim", "MET"), ("reclaim", "EVIDENCE_NEEDED")]
    assert checks[1]["needed_session"] == str(following)
    closes[following] = _bar(following, days[following], 103)
    after = dt("2026-11-27T19:00:00+00:00")
    result = _price_checks(thesis, closes, None, days, after, currency="USD", compatible=True, active=True)
    assert result[1]["status"] == "NOT_MET"
    assert _price_checks(thesis, closes, None, days, after, currency="USD", compatible=True, active=False)[1]["status"] == "EVIDENCE_NEEDED"


def test_failed_breakout_trim_requires_prior_breakout_and_tactical_position():
    now = dt("2026-11-25T23:00:00+00:00")
    day = date(2026, 11, 25)
    days = market_days("US", now)
    thesis = {"analysis_asof": "2026-11-25T17:00:00+00:00", "execution_levels": {"levels": [
        {"level_type": "TRIM", "price": 110, "confirmation": "close", "reason_code": "FAILED_BREAKOUT",
         "source_text": "돌파가 확인된 뒤 그 아래로 마감하면 전술분 감축"},
        {"level_type": "TRIM", "price": 100, "confirmation": "close", "source_text": "100달러 미만 종가에서 감축"},
    ]}}
    checks = _price_checks(thesis, {day: _bar(day, days[day], 95)}, None, days, now,
                           currency="USD", compatible=True, active=True)
    assert checks[0]["status"] == "EVIDENCE_NEEDED"
    assert checks[1]["status"] == "MET"


def test_kis_fetch_uses_only_exact_completed_kr_sessions_and_explicit_adjustment(monkeypatch):
    now = dt("2026-11-25T04:04:05+09:00")
    days = market_days("KR", now)
    day = date(2026, 11, 24)
    requests = []

    def request_json(self, **kwargs):
        requests.append(kwargs)
        return {"output1": {"stck_shrn_iscd": "035420"}, "output2": [
            {"stck_bsop_date": token, "stck_oprc": "156000", "stck_clpr": "152700", "stck_hgpr": "157000",
             "stck_lwpr": "152000", "acml_vol": "17079045"} for token in ("20261124", "20261125")
        ]}, {"Date": "Tue, 24 Nov 2026 19:04:03 GMT"}

    monkeypatch.setattr(KisClient, "request_json", request_json)
    load = KisResearchCloses(KisClient.__new__(KisClient), clock=lambda: now)
    records = load("KR", "035420.KS", days, day, now)
    assert set(records) == {day}
    assert [call["params"]["FID_ORG_ADJ_PRC"] for call in requests] == ["1", "0"]
    assert all(call["params"]["FID_INPUT_DATE_2"] == "20261124"
               and call["params"]["FID_COND_MRKT_DIV_CODE"] == "J"
               and call["params"]["FID_PERIOD_DIV_CODE"] == "D" for call in requests)
    bar = records[day]
    assert (bar["price"], bar["volume"], bar["kind"], bar["verification"]) == (152700, 17079045, KR_DAILY, "UNVERIFIED")
    assert bar["exchange"] is None and bar["requested_market"] == "J"
    assert bar["provider_response_at"] == "2026-11-24T19:04:03+00:00"
    assert bar["event_time_source"] == "exchange_calendar"


def test_krx_verifies_by_session_board_and_symbol_with_bulk_requests(monkeypatch):
    now = dt("2026-11-25T08:38:31+09:00")
    day = date(2026, 11, 24)
    requests = []

    def get(path, params, *, timeout):
        requests.append((path, params, timeout))
        if "ksq_" in path:
            raise RuntimeError("unavailable")
        def row(ticker, price, session="20261124", board="KOSPI"):
            return {"BAS_DD": session, "MKT_NM": board, "ISU_CD": ticker, "TDD_CLSPRC": price}
        return {"OutBlock_1": [
            row("005930", "189,400"), row("035420", "156,100"),
            row("000660", "1158000", session="20261123"), row("111111", "100", board="KOSDAQ"),
            row("222222", "100"), row("222222", "101"),
        ]}

    monkeypatch.setattr("tradingagents.scheduled.strategy_krx_close.call_krx_open_api", get)
    official = KrxResearchCloses(lambda: now)
    anch = official("005930.KS", day)
    assert (anch["price"], anch["observed_at"], anch["adjustment"]) == (189400, now.isoformat(), "unadjusted")
    assert official("035420.KS", day)["price"] == 156100
    assert all(official(ticker, day) is None for ticker in ("000660.KS", "111111.KS", "222222.KS", "123456.KQ", "654321.KQ"))
    assert requests == [(f"/svc/apis/sto/{dataset}", {"basDd": "20261124"}, 4.0)
                        for dataset in ("stk_bydd_trd", "ksq_bydd_trd")]


@pytest.mark.parametrize("date_fields", [None, {}, {"BAS_DD": "20261125"}, {"BAS_DD": "20261131"},
                                         {"BAS_DD": "2026-11-24"}, {"BAS_DD": None}])
def test_krx_rejects_missing_invalid_and_future_trade_dates(monkeypatch, date_fields):
    now = dt("2026-11-25T08:38:31+09:00")
    day = date(2026, 11, 24)
    days = market_days("KR", now)
    rows = [] if date_fields is None else [
        {"MKT_NM": "KOSPI", "ISU_CD": "005930", "TDD_CLSPRC": "182900"} | date_fields,
    ]
    monkeypatch.setattr("tradingagents.scheduled.strategy_krx_close.call_krx_open_api",
                        lambda *args, **kwargs: {"OutBlock_1": rows})
    official = KrxResearchCloses(lambda: now)("005930.KS", day)
    assert official is None
    bar = _bar(day, days[day], 189400, currency="KRW", observed=now) | {
        "ticker": "005930.KS", "exchange": "KRX", "official_close": official,
    }
    assessed = _close_records({day: bar}, "KR", days, now)[day]
    assert assessed["verification"] == "UNVERIFIED"
    assert assessed["price_range"] == [189400, 189400]


@pytest.mark.parametrize("timestamp", [None, "bogus", "2026-11-25T08:38:31", "2026-11-25T08:38:32+09:00",
                                       "2026-11-24T15:34:59+09:00"])
def test_krx_rejects_invalid_evidence_receive_times(timestamp):
    now = dt("2026-11-25T08:38:31+09:00")
    day = date(2026, 11, 24)
    days = market_days("KR", now)
    official = {"source": "KRX_OPEN_API", "session": str(day), "price": 182900, "currency": "KRW",
                "adjustment": "unadjusted", "ticker": "005930", "board": "KOSPI", "dataset": "stk_bydd_trd"}
    if timestamp is not None:
        official["observed_at"] = timestamp
    bar = _bar(day, days[day], 189400, currency="KRW", observed=now) | {
        "ticker": "005930.KS", "exchange": "KRX", "official_close": official,
    }
    assessed = _close_records({day: bar}, "KR", days, now)[day]
    assert assessed["verification"] == "UNVERIFIED" and assessed["official_close"] is None
    level = {"level_type": "PULLBACK", "confirmation": "close", "low": 189300, "high": 190100}
    assert _compare(level, assessed, currency="KRW", compatible=True, conflict=False)["status"] == "MET"


@pytest.mark.parametrize(("use_exchange", "early_price", "expected"), [
    (False, None, "UNVERIFIED"), (True, None, "MATCHED"), (True, 182900, "CONFLICT"),
    (False, 182900, "CONFLICT"),
])
def test_kr_close_assessment_uses_actual_candidate_prices(use_exchange, early_price, expected):
    now = dt("2026-11-25T08:38:31+09:00")
    days = market_days("KR", now)
    day = date(2026, 11, 24)
    receipt = {"source": "KRX_OPEN_API", "session": str(day), "price": 189400, "currency": "KRW",
               "adjustment": "unadjusted", "observed_at": now.isoformat(), "ticker": "005930",
               "board": "KOSPI", "dataset": "stk_bydd_trd"}
    fresh = _bar(day, days[day], 189400, currency="KRW", observed=now) | {
        "kind": KR_DAILY, "requested_market": "J", "ticker": "005930.KS",
        "official_close": receipt if use_exchange else None,
    }
    closes = _close_records({day: fresh}, "KR", days, now)
    if early_price:
        old = _bar(day, days[day], early_price, currency="KRW") | {"exchange": "KRX"}
        _retain_previous_kr_close(closes, old, days, now)
    assert closes[day]["verification"] == expected
    assert closes[day]["kind"] == ("REGULAR_CLOSE" if expected == "MATCHED" else KR_DAILY)
    assert closes[day]["price_range"] == [early_price or 189400, 189400]
    level = {"level_type": "PULLBACK", "confirmation": "close"}
    for low, high, stable in [(189300, 190100, "MET"), (180000, 190100, "MET"),
                              (184000, 185000, "NOT_MET"), (190000, 191000, "NOT_MET")]:
        check = _compare(level | {"low": low, "high": high}, closes[day], currency="KRW", compatible=True, conflict=False)
        assert check["status"] == ("EVIDENCE_NEEDED" if early_price and low == 189300 else stable)


def test_malformed_us_response_does_not_block_another_symbol():
    now = dt("2026-11-25T02:47:48+09:00")
    days = market_days("US", now)
    close_day = date(2026, 11, 23)

    class Client:
        def request_json(self, *, params, **kwargs):
            if params["SYMB"] == "COST":
                return {"output1": ["ambiguous"], "output2": []}, {}
            return {"output1": {"rsym": "DNASAAPL"}, "output2": [
                {"xymd": "20261123", "open": "348", "clos": "349.08", "high": "351",
                 "low": "345", "tvol": "58000000"},
            ]}, {}

    load = KisResearchCloses(Client(), clock=lambda: now)
    assert load("US", "COST", days, close_day, now, "NAS") == {}
    assert load("US", "AAPL", days, close_day, now, "NAS")[close_day]["price"] == 349.08


@pytest.mark.parametrize("at", ["2026-11-24T16:15:03-05:00", "2026-11-25T07:00:03-05:00"])
@pytest.mark.parametrize("repeat_close", ["110.0275", "110.0001", None])
def test_us_daily_price_rechecks_the_same_completed_session_with_separate_receipts(at, repeat_close, monkeypatch):
    now = dt(at)
    day = date(2026, 11, 24)
    days = market_days("US", now)
    received = iter([now + timedelta(seconds=i) for i in range(3)])
    requests = []
    monkeypatch.setattr("tradingagents.scheduled.strategy_research_prices.sleep", lambda _: None)

    class Client:
        def request_json(self, **kwargs):
            requests.append(kwargs)
            close = repeat_close if len(requests) == 3 else "110.0001"
            rows = [{"xymd": token, "open": "108", "clos": close, "high": "112", "low": "107", "tvol": "1000"}
                    for token in (None, "2026114", "20261131", "20261125", "20261124")]
            return {"output1": {"rsym": "DNASAAPL"}, "output2": rows if close else []}, {
                "Date": "Tue, 24 Nov 2026 21:15:00 GMT" if len(requests) == 1 else "invalid",
            }

    load = KisResearchCloses(Client(), clock=lambda: next(received))
    records = load("US", "AAPL", days, date(2026, 11, 4), now, "NAS")
    assert set(records) == {day}
    assert [request["params"]["MODP"] for request in requests] == ["0", "1", "0"]
    assert all(request["method"] == "GET" and request["params"]["BYMD"] == "20261124" for request in requests)
    observation = records[day]
    assert observation["kind"] == "KIS_DAILY_CLOSE"
    assert observation["event_at"] == "2026-11-24T21:00:00+00:00"
    assert observation["provider_response_at"] == "2026-11-24T21:15:00+00:00"
    assert observation["observed_at"] == now.isoformat()
    assert observation["price"] == observation["adjusted_close"] == 110.0001
    if repeat_close:
        assert observation["recheck"] == {"price": float(repeat_close), "observed_at": (now + timedelta(seconds=2)).isoformat(),
                                          "provider_response_at": None}
        assert "recheck" not in _close_records(records, "US", days, now)[day]
    else:
        assert "recheck" not in observation


@pytest.mark.parametrize(("level", "expected"), [
    ({"level_type": "BREAKOUT", "price": 110, "source_text": "110 이상"}, "MET"),
    ({"level_type": "BREAKOUT", "price": 110.005, "source_text": "110.005 이상"}, "EVIDENCE_NEEDED"),
    ({"level_type": "BREAKOUT", "price": 110.0001}, "EVIDENCE_NEEDED"),
    ({"level_type": "STOP_LOSS", "price": 110.0275, "source_text": "110.0275 미만"}, "EVIDENCE_NEEDED"),
    ({"level_type": "PULLBACK", "low": 110.005, "high": 110.015}, "EVIDENCE_NEEDED"),
    ({"level_type": "PULLBACK", "low": 110.0001, "high": 110.0275}, "MET"),
    ({"level_type": "SUPPORT", "low": 108, "high": 109}, "NOT_MET"),
])
def test_divergent_us_closes_hold_only_unstable_price_comparisons(level, expected):
    observation = {"price": 110.0001, "recheck": {"price": 110.0275}}
    result = _compare(level | {"confirmation": "close"}, observation, currency="USD", compatible=True, conflict=False)
    assert result["status"] == expected
    assert result["observation"] == observation
    if expected == "EVIDENCE_NEEDED":
        assert "거래소 공식 종가" in result["needed"]


def test_single_us_observation_keeps_a_research_comparison_available():
    level = {"level_type": "BREAKOUT", "price": 110, "source_text": "110 이상", "confirmation": "close"}
    observation = {"price": 111, "kind": "KIS_DAILY_CLOSE"}
    assert _compare(level, observation, currency="USD", compatible=True, conflict=False)["status"] == "MET"
    assert _compare(level, observation, currency="USD", compatible=False, conflict=False)["status"] == "EVIDENCE_NEEDED"


def test_next_day_requery_retains_the_us_range_from_the_previous_build(tmp_path):
    now = dt("2026-11-25T14:00:00+00:00")
    day = date(2026, 11, 24)
    days = market_days("US", now)
    early = _bar(day, days[day], 108, observed=now - timedelta(hours=15))
    latest = _bar(day, days[day], 111, observed=now) | {"kind": "KIS_DAILY_CLOSE"}
    previous_path = tmp_path / "strategy.json"
    previous_path.write_text(json.dumps({"markets": {"us": {"rows": [
        {"ticker": "AAPL", "research_plan": {"completed_close": early}},
        {"ticker": "MSFT", "research_plan": None}, None,
    ]}}}), encoding="utf-8")
    old = previous_market_closes(previous_path)["US"]
    assert old == {"AAPL": early}
    closes = {day: latest}
    _retain_previous_close(closes, old["AAPL"], days, now)
    assert closes[day]["previous_range"] == [{"price": 108, "observed_at": early["observed_at"]}]
    level = {"level_type": "BREAKOUT", "price": 110, "source_text": "110 이상", "confirmation": "close"}
    assert _compare(level, closes[day], currency="USD", compatible=True, conflict=False)["status"] == "EVIDENCE_NEEDED"

    newer = {day: latest | {"observed_at": (now + timedelta(minutes=1)).isoformat()}}
    _retain_previous_close(newer, closes[day], days, now + timedelta(minutes=1))
    assert newer[day]["previous_range"] == closes[day]["previous_range"]

    for wrong in ({"exchange": "NYS"}, {"session": "2026-11-23"},
                  {"observed_at": (now + timedelta(seconds=1)).isoformat()}, {"currency": "KRW"}):
        fresh = {day: latest}
        _retain_previous_close(fresh, early | wrong, days, now)
        assert fresh[day] == latest
    previous_path.write_text("invalid", encoding="utf-8")
    assert previous_market_closes(previous_path) == {}


def test_disagreement_does_not_shift_first_breakout_to_a_later_session():
    now = dt("2026-11-27T19:00:00+00:00")
    days = market_days("US", now)
    first, following = date(2026, 11, 25), date(2026, 11, 27)
    breakout = {"level_type": "BREAKOUT", "price": 110, "source_text": "110 이상", "confirmation": "close",
                "confirmation_group": "reclaim"}
    follow = {"level_type": "PULLBACK", "low": 110, "high": 113, "confirmation": "next_day", "confirmation_group": "reclaim"}
    thesis = {"analysis_asof": "2026-11-25T17:00:00+00:00", "execution_levels": {"levels": [breakout, follow]}}
    closes = {first: _bar(first, days[first], 109) | {"recheck": {"price": 111}}, following: _bar(following, days[following], 112)}
    result = _price_checks(thesis, closes, None, days, now, currency="USD", compatible=True, active=True)
    assert [check["status"] for check in result] == ["MET", "EVIDENCE_NEEDED"]
    assert result[1]["needed"] == "2026-11-25 선행 종가의 가격 경계 확인"
    assert "preceding_price_session" not in result[1]


def test_latest_partial_research_reuses_true_origin_and_keeps_old_failed_ticker(tmp_path):
    def manifest(run_id, rows, *, finish, receipt=None, copies=None):
        directory = tmp_path / "runs" / "2026" / run_id
        directory.mkdir(parents=True)
        for row in rows:
            if row["status"] == "failed":
                continue
            (directory / row["artifacts"]["analysis_json"]).write_bytes((copies or {}).get(row["ticker"], json.dumps(row).encode()))
        payload = {"run_id": run_id, "settings": {"market": "KR", "run_mode": "full"},
                   "status": "partial_failure", "started_at": finish - 1, "tickers": rows, "finished_at": finish}
        payload.update(started_at=f"2026-11-{finish-1:02}T05:00:00+09:00", finished_at=f"2026-11-{finish:02}T06:00:00+09:00")
        if receipt:
            payload["research_recovery"] = receipt
        f = directory / "run.json"
        f.write_text(json.dumps(payload), encoding="utf-8")
        return f, directory

    def row(ticker, day):
        return {"ticker": ticker, "status": "success", "started_at": f"2026-11-{day}T05:30:00+09:00",
                "finished_at": f"2026-11-{day}T05:45:00+09:00", "trade_date": f"2026-11-{day-1}",
                "analysis_date": f"2026-11-{day}", "artifacts": {"analysis_json": ticker + ".json"},
                "decision": {"rating": "HOLD", "conditional_entry_action": "STARTER"}}

    older = "20261120T050000_local-scheduler-kr-full"
    original = "20261124T050000_local-scheduler-kr-full"
    retry = "20261124T100000_local-scheduler-kr-full"
    a, b = "035420.KS", "005930.KS"
    manifest(older, [row(a, 20), row(b, 20)], finish=20)
    source = row(a, 24)
    original_file, original_dir = manifest(original, [source, {"ticker": b, "status": "failed"}], finish=24)
    raw = (original_dir / (a + ".json")).read_bytes()
    proof = {"source_run_id": original, "analysis_started_at": source["started_at"],
             "analysis_finished_at": source["finished_at"], "artifact_sha256": {"analysis_json": hashlib.sha256(raw).hexdigest()}}
    receipt = {"source_run_id": original, "source_manifest_sha256": hashlib.sha256(original_file.read_bytes()).hexdigest(),
               "reused_research": {a: proof}}
    manifest(retry, [source | {"research_reuse": proof}, {"ticker": b, "status": "failed"}],
             finish=24, receipt=receipt, copies={a: raw})
    now = dt("2026-11-25T02:47:48+09:00")
    plans = ResearchArchive(tmp_path, "KR", now).latest([a, b])
    assert plans[a][0] == retry and plans[a][1][0] == original
    assert plans[b][1][0] == older
    thesis = thesis_for(plans[a][1])
    assert thesis["rating"] == thesis["stance"] == "HOLD"
    assert thesis["conditional_entry_action"] == "STARTER"
