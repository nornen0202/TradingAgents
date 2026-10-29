from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock
import pandas as pd
import pytest
from tradingagents.dataflows import alpaca_daily_history as sip, us_daily_history as us
from tradingagents.dataflows.vendor_exceptions import VendorMalformedResponseError
from tradingagents.dataflows.daily_history_selection import activate_daily_history_selection, reset_daily_history_selection, get_selected_daily_history

DATES=['2021-10-28','2026-10-27','2026-10-28']
def row(day, **extra):
    return {'t':day+'T04:00:00Z','o':100,'h':110,'l':90,'c':105,'v':1000,**extra}

@pytest.fixture
def provider(monkeypatch):
    monkeypatch.setenv(sip.ENABLED,'1')
    monkeypatch.setenv('TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED','1')
    monkeypatch.setattr(sip,'get_api_key',lambda _: 'offline')
    monkeypatch.setattr(us,'_sessions',lambda start,end: [date.fromisoformat(x) for x in DATES])
    request=Mock(return_value=SimpleNamespace(status_code=200,json=lambda: {'bars':{'CVX':[row(x) for x in DATES]}}))
    monkeypatch.setattr(sip.requests,'get',request)
    return request


def test_complete_sip_series_uses_completed_close_and_asof(provider):
    result=sip.load_us_daily_bars('CVX','2026-09-28','2026-10-28')
    assert len(result)==3 and result.attrs['complete'] is True
    params=provider.call_args.kwargs['params']
    assert params['end']=='2026-10-28T20:00:00+00:00' and params['asof']=='2026-10-28'
    assert params['feed']=='sip' and params['adjustment']=='all'
    assert provider.call_args.kwargs['allow_redirects'] is False


@pytest.mark.parametrize('rows', [[],[row(DATES[0]),row(DATES[-1])],
    [row(x) for x in DATES]+[row(DATES[-1],c=106)],
    [row(DATES[0]),row(DATES[1]),row(DATES[-1],h=99)],
    [row(DATES[0]),row(DATES[1]),row(DATES[-1],t=None)],
    [row(DATES[0]),row(DATES[1]),row(DATES[-1],t='bad-date')],
    [row(DATES[0]),row(DATES[1]),row(DATES[-1],t='2026-10-28')],
    [row(DATES[0]),row(DATES[1]),row(DATES[-1],c=float('nan'))],
    [row(DATES[0]),row(DATES[1]),row(DATES[-1],v=-1)]])
def test_sip_rejects_empty_missing_invalid_and_conflicting_rows(provider,rows):
    provider.return_value.json=lambda: {'bars':{'CVX':rows}}
    with pytest.raises(VendorMalformedResponseError): sip.load_us_daily_bars('CVX','2026-09-28','2026-10-28')


def test_future_rows_are_excluded_before_values(provider):
    provider.return_value.json=lambda: {'bars':{'CVX':[row(x) for x in DATES]+[{'t':'2026-10-29T04:00:00Z'}]}}
    assert len(sip.load_us_daily_bars('CVX','2026-09-28','2026-10-28'))==3


def test_repeated_pages_fail_bounded(provider):
    provider.return_value.json=lambda: {'bars':{'CVX':[row(DATES[0])]},'next_page_token':'repeat'}
    with pytest.raises(VendorMalformedResponseError,match='progress'): sip.load_us_daily_bars('CVX','2026-09-28','2026-10-28')
    assert provider.call_count==2


@pytest.mark.parametrize('status',[401,403,429,500])
def test_sip_does_not_retry_denied_requests(provider,status):
    provider.return_value.status_code=status
    with pytest.raises(VendorMalformedResponseError,match=str(status)): sip.load_us_daily_bars('CVX','2026-09-28','2026-10-28')
    assert provider.call_count==1


def test_invalid_kis_selects_whole_sip_series_and_pins_indicators(provider,monkeypatch):
    monkeypatch.setattr(us,'load_us_daily_bars',Mock(side_effect=VendorMalformedResponseError('bad KIS OHLCV')))
    token=activate_daily_history_selection()
    try:
        original=pd.DataFrame({'Date':['2026-10-28'],'Close':[float('nan')]})
        result=us.validate_with_us_fallback(original,'CVX','2026-09-28','2026-10-28')
        selected=get_selected_daily_history('CVX','2026-10-28')
        assert selected['source']==sip.SOURCE and len(selected['frame'])==3
        assert len(result)==2 and sip.SOURCE in us.source_note(result)
        pinned=us.selected_history('CVX','2026-09-28','2026-10-28')
        assert list(pinned.Close)==[105,105] and provider.call_count==1
    finally: reset_daily_history_selection(token)

def test_sip_evidence_is_verified_only_with_matching_cutoff(provider):
    from tradingagents.dataflows.daily_history_evidence import _snapshot
    frame=sip.load_us_daily_bars('CVX','2026-09-28','2026-10-28')
    receipt=_snapshot('CVX','2026-10-28',sip.SOURCE,frame)
    assert receipt['status']=='VERIFIED_RETRIEVED_SERIES'
    assert receipt['provider']=='alpaca' and receipt['historical_vintage_verified'] is False
    frame.attrs['request_end']='2026-10-29T00:00:00+00:00'
    assert _snapshot('CVX','2026-10-28',sip.SOURCE,frame)['status']=='UNVERIFIED'


def test_sip_routes_remain_pinned_to_wrapper(provider):
    from tradingagents.dataflows.interface import _assert_history_vendor
    from tradingagents.dataflows.daily_history_selection import select_daily_history
    from tradingagents.dataflows.vendor_exceptions import VendorInputError
    token=activate_daily_history_selection()
    try:
        frame=sip.load_us_daily_bars('CVX','2026-09-28','2026-10-28')
        select_daily_history('CVX','2026-10-28',sip.SOURCE,frame)
        _assert_history_vendor(('CVX','2026-10-28'),'yfinance')
        with pytest.raises(VendorInputError): _assert_history_vendor(('CVX','2026-10-28'),'alpha_vantage')
    finally: reset_daily_history_selection(token)
