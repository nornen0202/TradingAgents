import pytest

from tradingagents.external.prism_telegram_common import (
    PrismTelegramDocument,
    PrismTelegramMessage,
    _ticker_mentions_from_line,
    message_to_signals,
)


@pytest.mark.parametrize("text", [
    "20일 이동평균(SMA20)",
    "50일 이동평균(SMA50)",
    "📊 지표: 20일 단순 이동평균선 (SMA20)",
    "20-day simple moving average (SMA20)",
    "50 period moving average (SMA50)",
    "기준시각(UTC)",
    "기준 시간 (UTC)",
    "협정 세계시 (UTC)",
    "Coordinated Universal Time (UTC)",
    "timestamp (UTC)",
    "낸드(NAND)",
    "산업 설명: 낸드 플래시 메모리 (NAND)",
    "NAND flash memory (NAND)",
    "not-and (NAND)",
])
def test_explicit_descriptive_abbreviations_are_not_ticker_mentions(text):
    assert _ticker_mentions_from_line(text) == []
    assert message_to_signals(PrismTelegramMessage(message_id="synthetic", text=text), default_market="US") == []


@pytest.mark.parametrize("text,expected", [
    ("NAND Technologies (NAND)", ["NAND"]),
    ("UTC Corporation (UTC)", ["UTC"]),
    ("SMA20 Holdings (SMA20)", ["SMA20"]),
    ("SMA50 Ltd. (SMA50)", ["SMA50"]),
    ("Tickers: (SMA20), (SMA50), (UTC), (NAND)", ["SMA20", "SMA50", "UTC", "NAND"]),
    ("티커: 낸드(NAND)", ["NAND"]),
    ("종목 코드: 기준시각(UTC)", ["UTC"]),
    ("종목 목록: 20일 이동평균(SMA20)", ["SMA20"]),
    ("ticker: 50-day simple moving average (SMA50)", ["SMA50"]),
    ("종목 목록: 20일 이동평균(SMA20) / 기준시각(UTC) / 낸드(NAND)", ["SMA20", "UTC", "NAND"]),
    ("Alpha(AAA) / Beta(BBB)", ["AAA", "BBB"]),
    ("Berkshire Hathaway (BRK.B) / Berkshire Hathaway (BRK-B)", ["BRK.B", "BRK-B"]),
    ("삼성전자(005930) / SK하이닉스(000660)", ["005930", "000660"]),
    ("A company (AI) / Another company (ATR) / Third company (RSI)", ["AI", "ATR", "RSI"]),
    # Ambiguous/mismatched contexts remain candidates, not a global blacklist.
    ("20일 이동평균(SMA50)", ["SMA50"]),
    ("지표(SMA20)", ["SMA20"]),
    ("낸드 회사(NAND)", ["NAND"]),
    ("NAND (NAND)", ["NAND"]),
])
def test_symbols_are_preserved_outside_the_narrow_description_context(text, expected):
    assert [mention.ticker for mention in _ticker_mentions_from_line(text)] == expected


def test_ignored_inline_abbreviation_does_not_contaminate_next_company_name():
    mentions = _ticker_mentions_from_line("Alpha Corp(AAA) / 20일 이동평균(SMA20) / Beta Corp(BBB)")
    assert [(mention.ticker, mention.display_name) for mention in mentions] == [
        ("AAA", "Alpha Corp"), ("BBB", "Beta Corp"),
    ]


def test_scoping_uses_accepted_mentions_for_boundaries_inline_counts_and_start():
    message = PrismTelegramMessage(
        message_id="synthetic",
        text="""기준시각(UTC)
Current: $999
Alpha Corp(AAA) / 20일 이동평균(SMA20)
50일 이동평균(SMA50)
기준시각(UTC)
낸드(NAND)
Current: $10
Target: $12
Stop: $9
Score: 8/10
UTC Corporation (UTC)
Current: $20
Target: $24
Stop: $18
Score: 6/10""",
    )
    signals = {signal.canonical_ticker: signal for signal in message_to_signals(message, default_market="US")}
    assert set(signals) == {"AAA", "UTC"}
    assert (signals["AAA"].current_price, signals["AAA"].target_price, signals["AAA"].stop_loss_price, signals["AAA"].confidence) == (10, 12, 9, 0.8)
    assert (signals["UTC"].current_price, signals["UTC"].target_price, signals["UTC"].stop_loss_price, signals["UTC"].confidence) == (20, 24, 18, 0.6)


def test_real_multiple_inline_companies_still_do_not_share_prices():
    message = PrismTelegramMessage(message_id="synthetic", text="Alpha(AAA) / Beta(BBB) / 20일 이동평균(SMA20)\nCurrent: $10\nStop: $9")
    signals = message_to_signals(message, default_market="US")
    assert [signal.canonical_ticker for signal in signals] == ["AAA", "BBB"]
    assert all(signal.current_price is None and signal.stop_loss_price is None for signal in signals)


def test_single_remaining_company_does_not_inherit_ignored_preamble_prices():
    message = PrismTelegramMessage(
        message_id="synthetic",
        text="기준시각(UTC)\nCurrent: $999\nStop: $998\nScore: 1/10\nAlpha(AAA)\nCurrent: $10\nStop: $9\nScore: 8/10",
    )
    signals = message_to_signals(message, default_market="US")
    assert len(signals) == 1
    assert signals[0].canonical_ticker == "AAA"
    assert (signals[0].current_price, signals[0].stop_loss_price, signals[0].confidence) == (10, 9, 0.8)


@pytest.mark.parametrize("text,ticker", [
    ("기준시각(UTC) Current: $999 / Alpha(AAA) Current: $10", "AAA"),
    ("기준시각(UTC) Current: $999 / UTC Corporation(UTC) Current: $10", "UTC"),
])
def test_inline_ignored_header_does_not_supply_company_prices(text, ticker):
    signals = message_to_signals(PrismTelegramMessage(message_id="synthetic", text=text), default_market="US")
    assert len(signals) == 1
    assert signals[0].canonical_ticker == ticker
    assert signals[0].current_price is None


def test_single_document_filename_only_fallback_is_preserved():
    message = PrismTelegramMessage(
        message_id="synthetic", text="Current: $10\nStop: $9",
        documents=(PrismTelegramDocument(filename="AAA_Alpha_20261002.pdf"),),
    )
    signals = message_to_signals(message, default_market="US")
    assert len(signals) == 1
    assert signals[0].canonical_ticker == "AAA"
    assert (signals[0].current_price, signals[0].stop_loss_price) == (10, 9)


def test_filename_only_company_does_not_inherit_ignored_abbreviation_prices():
    message = PrismTelegramMessage(
        message_id="synthetic", text="기준시각(UTC)\nCurrent: $999\nStop: $998",
        documents=(PrismTelegramDocument(filename="AAA_Alpha_20261002.pdf"),),
    )
    signals = message_to_signals(message, default_market="US")
    assert len(signals) == 1
    assert signals[0].canonical_ticker == "AAA"
    assert signals[0].current_price is None
    assert signals[0].stop_loss_price is None


def test_document_excerpt_uses_same_filter_without_changing_filename_identity():
    message = PrismTelegramMessage(
        message_id="synthetic", text="",
        documents=(PrismTelegramDocument(
            filename="NAND_NAND_Technologies_20261002.pdf",
            text_summary={"excerpt": "NAND Technologies(NAND)\n낸드(NAND)\n기준시각(UTC)\n20일 이동평균(SMA20)"},
        ),),
    )
    signals = message_to_signals(message, default_market="US")
    assert [signal.canonical_ticker for signal in signals] == ["NAND"]
