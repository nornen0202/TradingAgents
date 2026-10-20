from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from tradingagents.dataflows.intraday.us_kis_evidence import dated_book, dated_strength, prior_daily_volume


NOW = datetime(2026, 10, 21, 0, 5, 30, tzinfo=ZoneInfo("Asia/Seoul"))


def book(**changes):
    result = {"output1": {"code": "AAPL", "curr": "USD", "dymd": "20261021", "dhms": "000520"},
              "output2": {"pbid1": "200", "pask1": "201", "vbid1": "1000", "vask1": "500"}}
    result["output1"].update(changes)
    return result


def test_original_korea_clock_split_response_and_direct_broker_strength():
    row, at = dated_book(book(), "AAPL", NOW)
    assert row["pbid1"] == "200" and at == NOW - timedelta(seconds=10)
    strength, event_at, receipt = dated_strength(
        {"output1": {"nrec": "2"}, "output2": [
            {"khms": "000519", "vpow": "85.2", "mtyp": "1"},
            {"khms": "000518", "vpow": "95", "mtyp": "2"}]},
        book_at=at, observed_at=NOW)
    assert strength == 85.2  # mtyp does not infer buy/sell direction
    assert event_at == NOW - timedelta(seconds=11)
    assert receipt["date_basis"] == "TDAY_1_DATED_CURRENT_ORDERBOOK"


@pytest.mark.parametrize("changes", [
    {"dymd": ""}, {"dymd": "20261020"}, {"dymd": "bad"},
    {"dymd": "20260230"}, {"dhms": ""}, {"dhms": "000531"},
    {"dhms": "000330"}, {"code": "MSFT"}, {"curr": "KRW"},
])
def test_book_rejects_missing_invalid_future_stale_wrong_identity(changes):
    with pytest.raises(ValueError):
        dated_book(book(**changes), "AAPL", NOW)


def test_volumes_are_never_prices_and_parts_cannot_conflict():
    payload = book()
    payload["output2"] = {"vbid1": "1000", "vask1": "2000"}
    with pytest.raises(ValueError):
        dated_book(payload, "AAPL", NOW)
    payload = book()
    payload["output2"]["code"] = "MSFT"
    with pytest.raises(ValueError):
        dated_book(payload, "AAPL", NOW)


@pytest.mark.parametrize("rows", [
    [], None, [{"khms": "000531", "vpow": 100}],
    [{"khms": "000330", "vpow": 100}], [{"vpow": 100}],
    [{"khms": "235959", "vpow": 100}],  # no midnight rollover guessed
    [{"khms": "000520", "mtyp": "2", "evol": 200}],
    [{"khms": "000520", "vpow": "nan"}],
])
def test_tape_never_uses_summary_side_or_unverified_time(rows):
    with pytest.raises(ValueError):
        dated_strength({"output2": rows}, book_at=NOW - timedelta(seconds=10), observed_at=NOW)


def test_daily_denominator_locally_filters_dates_and_requires_twenty():
    day = NOW.date()
    rows = [{"xymd": (day - timedelta(days=i)).strftime("%Y%m%d"), "tvol": "1000"}
            for i in range(1, 21)]
    bad = [{"xymd": day.strftime("%Y%m%d"), "tvol": "900000"},
           {"xymd": (day + timedelta(days=1)).strftime("%Y%m%d"), "tvol": "900000"},
           {"xymd": "20260230", "tvol": "900000"}, {"tvol": "900000"}]
    assert prior_daily_volume(rows + bad, as_of=day) == 1000
    assert prior_daily_volume(rows[:-1] + bad, as_of=day) is None
    assert prior_daily_volume(rows + [{**rows[0], "tvol": "2000"}], as_of=day) is None
