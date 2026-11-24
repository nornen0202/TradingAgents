from datetime import date, datetime, timezone
import io
from zipfile import ZipFile

import pytest

from tradingagents.execution.research_ledger import Ledger, actual_shares
from tradingagents.execution.research_lean import _final_market_timezone
from tradingagents.execution.research_sources import dart_vintages, sec_vintages
from tradingagents.execution.research_study import _filing_events, _profit_at, _without_unverified_revisions


def test_sec_requires_exact_accession_date_period_and_clock():
    accession = "0000320193-20-000001"
    filing = {"filingDate": "2020-10-30", "reportDate": "2020-09-26", "form": "10-K",
              "acceptanceDateTime": "2020-10-30T20:15:21Z", "accessionNumber": accession}
    fact = {"accn": accession, "end": "2020-09-26", "filed": "2020-10-30", "form": "10-K"}
    rows = {"Assets": {"units": {"USD": [{**fact, "val": 200},
                                         {**fact, "val": 999, "filed": "garbled"}]}},
            "NetIncomeLoss": {"units": {"USD": [{**fact, "val": 20, "start": "2019-09-29"},
                                               {**fact, "val": 99, "accn": "unmapped"}]}}}
    assert sec_vintages(rows, [filing], date(2020, 10, 29)) == []
    assert sec_vintages(rows, [{**filing, "acceptanceDateTime": "invalid"}], date(2020, 12, 1)) == []
    assert sec_vintages(rows, [], date(2020, 12, 1)) == []
    actual = sec_vintages(rows, [filing], date(2020, 12, 1))
    assert [row["roa"] for row in actual] == [.1]
    events = _filing_events(actual, "US", ["2020-10-30", "2020-11-02"])
    assert _profit_at(events, "2020-10-30") is None
    assert _profit_at(events, "2020-11-02")[1]["id"] == accession


def test_dart_original_consolidated_and_date_only_amendment():
    raw = io.BytesIO()
    xml = """<x:xbrl xmlns:x="http://www.xbrl.org/2003/instance" xmlns:i="urn:test" xmlns:d="urn:dim">
      <x:context id="instant"><x:entity><x:identifier>00126380</x:identifier></x:entity>
        <x:period><x:instant>2019-12-31</x:instant></x:period><d:explicitMember>d:ConsolidatedMember</d:explicitMember></x:context>
      <x:context id="span"><x:entity><x:identifier>00126380</x:identifier></x:entity>
        <x:period><x:startDate>2019-01-01</x:startDate><x:endDate>2019-12-31</x:endDate></x:period>
        <d:explicitMember>d:ConsolidatedMember</d:explicitMember></x:context>
      <i:Assets unitRef="KRW" contextRef="instant">500</i:Assets>
      <i:ProfitLoss unitRef="KRW" contextRef="span">50</i:ProfitLoss>
    </x:xbrl>"""
    with ZipFile(raw, "w") as zipped:
        zipped.writestr("original.xbrl", xml)
    filing = {"rcept_dt": "20200330", "report_nm": "사업보고서 (2019.12)",
              "rcept_no": "20200330003851", "corp_code": "00126380"}
    data = raw.getvalue()
    assert dart_vintages(data, filing["corp_code"], filing, "2020-03-29") == []
    assert dart_vintages(data, filing["corp_code"], {**filing, "rcept_dt": "invalid"}, "2020-04-01") == []
    original, = dart_vintages(data, filing["corp_code"], filing, "2020-04-01")
    amended = {**original, "id": "20200401000001", "filed": "2020-04-01", "roa": .08}
    events = _filing_events([original, amended], "KR", ["2020-03-30", "2020-03-31", "2020-04-01", "2020-04-02"])
    assert _profit_at(events, "2020-03-30") is None
    assert _profit_at(events, "2020-04-01")[1]["roa"] == .1
    assert _profit_at(events, "2020-04-02")[1]["roa"] == .08
    revisions = _without_unverified_revisions([original], [
        {**filing, "rcept_no": "20200401000001", "rcept_dt": "20200401", "report_nm": "[기재정정]사업보고서 (2019.12)"}
    ], "KR")
    events = _filing_events(revisions, "KR", ["2020-03-30", "2020-03-31", "2020-04-01", "2020-04-02"])
    assert _profit_at(events, "2020-04-01")[1]["roa"] == .1
    assert _profit_at(events, "2020-04-02") is None


def test_share_reconstruction_and_costed_new_entry():
    bar = {"Open": 25, "High": 27, "Low": 24, "Close": 26, "Volume": 1000,
           "Dividends": 0, "Stock Splits": 0, "Capital Gains": 0}
    actual = actual_shares({"2020-08-28": bar, "2020-08-31": {**bar, "Stock Splits": 4}})
    assert actual["2020-08-28"]["open"] == 100
    assert actual["2020-08-31"]["open"] == 25
    ledger = Ledger({"AAPL": "US"})
    first = datetime(2020, 8, 28, 13, 30, tzinfo=timezone.utc)
    ledger.positions["AAPL"].close = 100
    ledger.rebalance("US", {"AAPL": 100}, {"AAPL": .5}, first, first.date(), 1000)
    assert ledger.positions["AAPL"].units == 500
    assert ledger.cash == pytest.approx(100_000_000 - 500 * 100 * 1000 * 1.001 ** 3)
    cash_before = ledger.cash
    ledger.corporate_action("AAPL", {"split": 4, "dividend": .25}, first, 1000)
    assert ledger.positions["AAPL"].units == 2000
    assert ledger.receivables["US"] == 425
    assert ledger.cash == cash_before


@pytest.mark.parametrize(("market", "zone"), [("KR", "Asia/Seoul"), ("US", "America/New_York")])
def test_lean_closing_cutoff_uses_last_mark_market(tmp_path, market, zone):
    tape = tmp_path / "202611.csv"
    tape.write_text(
        '20261124 063000,{"market":"%s","day":"2026-11-24","mark":true}\n' % market,
        encoding="utf-8",
    )
    assert _final_market_timezone(tape, "2026-11-24") == zone
    with pytest.raises(ValueError, match="final tape event"):
        _final_market_timezone(tape, "2026-11-23")
