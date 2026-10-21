from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from types import SimpleNamespace

import pytest

from tradingagents.dataflows.intraday.us_halts import NasdaqHaltProvider, parse_feed, status_for

NOW = datetime(2026, 10, 20, 15, 0, tzinfo=timezone.utc)


def feed(items="", count=0, published=NOW):
    return (f'<rss xmlns:ndaq="http://www.nasdaqtrader.com/"><channel>'
            f'<description>NASDAQ Trade Halts</description><pubDate>{format_datetime(published)}</pubDate>'
            f'<ndaq:numItems>{count}</ndaq:numItems>{items}</channel></rss>').encode()


def item(symbol="AAPL", halted="10:30:00.000", resumed="", resume_day=""):
    values = {"IssueSymbol": symbol, "ReasonCode": "T1", "HaltDate": "10/20/2026",
              "HaltTime": halted, "ResumptionDate": resume_day, "ResumptionTradeTime": resumed}
    return '<item>' + ''.join(f'<ndaq:{k}>{v}</ndaq:{k}>' for k, v in values.items()) + '</item>'


def bars():
    return [{"timestamp": (NOW-timedelta(minutes=1)).isoformat(), "available_at": NOW.isoformat(),
             "observed_at": NOW.isoformat(), "volume": 10}]


def status(content, symbol="AAPL"):
    return status_for(parse_feed(content, observed_at=NOW), symbol, analysis_as_of=NOW, traded_bars=bars())


def test_absence_requires_current_dated_trade_to_rule_out_multiday_halt():
    assert status_for(parse_feed(feed(), observed_at=NOW), "AAPL", analysis_as_of=NOW)["status"] == "unknown"
    assert status(feed())["is_clear"] is True
    assert status(feed(item(), 1), "MSFT")["is_clear"] is True
    assert status(feed(item(), 1))["is_clear"] is False


def test_trade_resumption_and_latest_rehalt():
    resumed = item(resumed="10:40:00", resume_day="10/20/2026")
    assert status(feed(resumed, 1))["is_clear"] is True
    assert status(feed(resumed + item(halted="10:50:00"), 2))["is_clear"] is False
    assert status(feed(item(resumed="11:05:00", resume_day="10/20/2026"), 1))["is_clear"] is False


@pytest.mark.parametrize('alias', ['BRK.B', 'BRK/B', 'BRK B', 'BRK-B'])
def test_class_share_halt_alias_is_matched_without_confusing_other_class(alias):
    assert status(feed(item(symbol=alias), 1), 'BRK-B')['status'] == 'halted'
    assert status(feed(item(symbol='BRK.A'), 1), 'BRK-B')['status'] == 'clear'


@pytest.mark.parametrize("content", [b'', b'<rss/>', feed(count=1), feed(item(), 0),
    feed(item(halted="bad"), 1), feed(item(halted="11:00:01"), 1),
    feed(item(symbol=""), 1), feed(item(resumed="10:20:00", resume_day="10/20/2026"), 1),
    feed(item(resumed="10:40:00"), 1), feed(published=NOW+timedelta(seconds=1)),
    feed(item() + item(resumed="10:40:00", resume_day="10/20/2026"), 2),
    feed(published=NOW-timedelta(seconds=120)),
    feed().replace(b'<pubDate>', b'<badDate>').replace(b'</pubDate>', b'</badDate>'),
    feed(item().replace('10/20/2026', '02/30/2026'), 1)])
def test_bad_incomplete_missing_future_stale_dates_fail_closed(content):
    with pytest.raises(Exception):
        status(content)


def test_future_ingestion_and_cached_age_never_rewrite_publication():
    parsed = parse_feed(feed(), observed_at=NOW)
    for cutoff in [NOW-timedelta(seconds=1), NOW+timedelta(seconds=120)]:
        with pytest.raises(ValueError):
            status_for(parsed, "AAPL", analysis_as_of=cutoff)


@pytest.mark.parametrize("change", [
    {"volume": 0}, {"volume": float("nan")}, {"volume": True},
    {"timestamp": (NOW-timedelta(days=1)).isoformat()},
    {"available_at": (NOW+timedelta(seconds=1)).isoformat()},
    {"observed_at": (NOW+timedelta(seconds=1)).isoformat()},
    {"timestamp": None}, {"available_at": "bad"}])
def test_empty_or_unverifiable_traded_bar_cannot_clear_unlisted_multiday_halt(change):
    traded = [{**bars()[0], **change}]
    result = status_for(parse_feed(feed(), observed_at=NOW), "AAPL", analysis_as_of=NOW, traded_bars=traded)
    assert result["status"] == "unknown" and result["is_clear"] is False


def test_provider_paces_across_symbols_and_does_not_reuse_success_after_failure():
    clock = [NOW]; elapsed = [0]; calls = []
    def get(url, **kwargs):
        calls.append((url, kwargs))
        return SimpleNamespace(status_code=200 if len(calls) == 1 else 500, content=feed())
    provider = NasdaqHaltProvider(get=get, clock=lambda: clock[0], monotonic=lambda: elapsed[0])
    assert provider.fetch("AAPL", traded_bars=bars())["is_clear"]
    assert provider.fetch("MSFT", traded_bars=bars())["is_clear"]
    assert len(calls) == 1 and calls[0][1]["allow_redirects"] is False
    elapsed[0] = 60
    with pytest.raises(ValueError):
        provider.fetch("AAPL")
    with pytest.raises(ValueError):
        provider.fetch("MSFT")
    assert len(calls) == 2


@pytest.mark.parametrize("reason", ["T1", "T2", "LUDP", "T5", "M", "UNKNOWN_CODE"])
def test_all_reported_halts_block_long_only_pause_and_news_checks(reason):
    from tradingagents.dataflows.intraday.us_halts import long_only_market_statuses
    halt = status(feed(item().replace('<ndaq:ReasonCode>T1', '<ndaq:ReasonCode>' + reason), 1))
    luld, reg_sho, news = long_only_market_statuses(halt, analysis_as_of=NOW)
    assert luld['is_clear'] is news['is_clear'] is False
    assert luld['price_bands_available'] is False
    assert reg_sho['status'] == 'not_applicable_long_only'
    assert reg_sho['is_clear'] is None and reg_sho['short_sale_status'] == 'unknown'


@pytest.mark.parametrize("change", [{}, {'published_at': None}, {'observed_at': 'bad'},
    {'as_of': (NOW + timedelta(seconds=1)).isoformat()}, {'basis': None}, {'is_clear': False}])
def test_scoped_status_retains_strict_dates_and_never_claims_price_bands(change):
    from tradingagents.dataflows.intraday.us_halts import long_only_market_statuses
    halt = {**status(feed()), **change}
    luld, _, news = long_only_market_statuses(halt, analysis_as_of=NOW)
    assert (luld['is_clear'] is True) == (not change)
    assert (news['is_clear'] is True) == (not change)
    assert luld['price_bands_available'] is False
    expired, _, _ = long_only_market_statuses(halt, analysis_as_of=NOW+timedelta(seconds=120))
    assert expired['is_clear'] is None
