"""Offline calendar construction concurrency, forwarding and failure contracts."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event, Lock, Thread
from unittest.mock import Mock

import exchange_calendars
import pytest

from tradingagents.calendar_access import get_exchange_calendar


def test_parallel_construction_does_not_overlap_shared_factory(monkeypatch):
    gate = Barrier(5)
    attempted = [Event() for _ in range(4)]
    entered, overlap, release = Event(), Event(), Event()
    count_lock = Lock()
    active, maximum = 0, 0
    expected = object()

    def factory(name, **kwargs):
        nonlocal active, maximum
        with count_lock:
            active += 1
            maximum = max(maximum, active)
            if active > 1:
                overlap.set()
        entered.set()
        assert release.wait(5)
        with count_lock:
            active -= 1
        return expected

    monkeypatch.setattr(exchange_calendars, 'get_calendar', factory)

    def worker(index):
        gate.wait(timeout=5)
        attempted[index].set()
        return get_exchange_calendar('XKRX', start='2021-10-23', end='2026-10-23')

    with ThreadPoolExecutor(4) as pool:
        futures = [pool.submit(worker, index) for index in range(4)]
        try:
            gate.wait(timeout=5)
            assert entered.wait(5)
            assert all(event.wait(5) for event in attempted)
            assert not overlap.wait(0.2)
        finally:
            release.set()
        assert all(future.result(timeout=5) is expected for future in futures)
    assert maximum == 1


@pytest.mark.parametrize('name,kwargs', [
    ('XKRX', {}), ('XNYS', {}),
    ('XKRX', {'start': '2021-10-23', 'end': '2026-10-23', 'side': 'left'}),
])
def test_original_calendar_arguments_and_object_are_preserved(monkeypatch, name, kwargs):
    expected = object()
    factory = Mock(return_value=expected)
    monkeypatch.setattr(exchange_calendars, 'get_calendar', factory)
    assert get_exchange_calendar(name, **kwargs) is expected
    factory.assert_called_once_with(name, **kwargs)


def test_factory_failure_is_unchanged_and_releases_other_threads(monkeypatch):
    error, expected = ValueError('calendar unavailable'), object()
    factory = Mock(side_effect=[error, expected])
    monkeypatch.setattr(exchange_calendars, 'get_calendar', factory)
    with pytest.raises(ValueError) as caught:
        get_exchange_calendar('XKRX')
    assert caught.value is error
    finished = Event()
    results = []

    def retry():
        results.append(get_exchange_calendar('XNYS'))
        finished.set()

    thread = Thread(target=retry, daemon=True)
    thread.start()
    assert finished.wait(5)
    thread.join(timeout=5)
    assert results == [expected]
