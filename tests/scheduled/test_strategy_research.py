import hashlib
import json
from datetime import date, datetime, timedelta

import pytest

from tradingagents.scheduled.strategy_research import _basis_compatible, _close_records, _price_checks
from tradingagents.scheduled.strategy_research_prices import KisResearchCloses, market_days, price_epoch, validated_quote
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


def test_kis_fetch_uses_only_exact_completed_kr_sessions_and_explicit_adjustment():
    now = dt("2026-11-25T02:47:48+09:00")
    days = market_days("KR", now)
    requests = []

    class Client:
        def domestic_daily_itemchartprice(self, ticker, **kwargs):
            requests.append((ticker, kwargs))
            return {"output2": [
                {"stck_bsop_date": day, "stck_oprc": "152000", "stck_clpr": "152700", "stck_hgpr": "153000",
                 "stck_lwpr": "150000", "acml_vol": "1000000"} for day in ("20261124", "20261125")]}

    records = KisResearchCloses(Client(), clock=lambda: now)("KR", "035420.KS", days, date(2026, 11, 24), now)
    assert set(records) == {date(2026, 11, 24)}
    assert [call[1]["adjusted_price"] for call in requests] == ["1", "0"]
    assert all(call[1]["end_date"] == date(2026, 11, 24) for call in requests)
    assert records[date(2026, 11, 24)]["price"] == 152700


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

