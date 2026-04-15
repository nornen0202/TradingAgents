from tradingagents.scheduled.runner import _translate_legacy_rating


def test_no_trade_constructive_translates_to_watch_trigger():
    translated = _translate_legacy_rating(rating="NO_TRADE", stance="BULLISH", entry_action="WAIT")
    assert translated == "WATCH_TRIGGER"


def test_no_trade_bearish_translates_to_avoid():
    translated = _translate_legacy_rating(rating="NO_TRADE", stance="BEARISH", entry_action="EXIT")
    assert translated == "AVOID"
