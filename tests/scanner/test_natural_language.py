import json

import pytest

from tradingagents.scanner.conditions import evaluate_condition
from tradingagents.scanner.natural_language import compile_condition_text, main


def compiled(text, market=None):
    draft = compile_condition_text(text, market=market)
    assert draft["status"] == "compiled", draft["issues"]
    assert draft["assumptions"] == []
    return draft["condition"]


def test_korean_request_units_and_missing_data_remain_fail_closed():
    draft = compile_condition_text("거래대금 100억원 이상 그리고 전일 대비 거래량 1.5배 이상 그리고 거래정지 제외")
    assert draft["scope_market"] == "KR"
    tree = draft["condition"]
    row = {"market": "KR", "trading_value": 10_000_000_000, "volume_ratio": 1.5, "halted": False}
    assert evaluate_condition(tree, row)
    assert not evaluate_condition(tree, {**row, "market": "US"})
    assert not evaluate_condition(tree, {**row, "volume_ratio": 1.49})
    assert not evaluate_condition(tree, {**row, "halted": True})
    assert not evaluate_condition(tree, {**row, "halted": None})
    assert "전일 거래량" in draft["normalized_rules"][0]
    assert "KRW" in draft["normalized_rules"][1]


def test_boolean_grouping_precedence_and_unknown_not():
    grouped = compiled("(daily change >= 3% or gap >= 2%) and not halted")
    assert evaluate_condition(grouped, {"daily_change_pct": 3, "gap_pct": 0, "halted": False})
    assert evaluate_condition(grouped, {"daily_change_pct": 0, "gap_pct": 2, "halted": False})
    assert not evaluate_condition(grouped, {"daily_change_pct": 3, "gap_pct": 2})
    assert not evaluate_condition(grouped, {"daily_change_pct": 3, "gap_pct": 2, "halted": True})
    conventional = compiled("daily change >= 3% or gap >= 2% and not halted")
    assert evaluate_condition(conventional, {"daily_change_pct": 3, "halted": True})
    double_not = compiled("not not halted")
    assert evaluate_condition(double_not, {"halted": True})
    assert not evaluate_condition(double_not, {})


@pytest.mark.parametrize("text,market,field,value", [
    ("trading value at least 10 million USD", None, "trading_value", 10_000_000),
    ("시가총액이 1.2조원 이상", None, "market_cap", 1_200_000_000_000),
    ("거래대금 >= 10,000,000,000", "KR", "trading_value", 10_000_000_000),
    ("거래량 10만주 초과", None, "volume", 100_000),
    ("종가 강도 75% 이상", None, "close_strength", 0.75),
    ("close strength >= 0.75", None, "close_strength", 0.75),
    ("daily change > -3%", None, "daily_change_pct", -3),
    ("volume ratio >= 1.5x", None, "volume_ratio", 1.5),
    ("halted = FALSE", None, "halted", False),
])
def test_explicit_numbers_and_units(text, market, field, value):
    tree = compiled(text, market)
    if "all" in tree:
        tree = tree["all"][-1]
    assert tree["field"] == field
    assert tree["value"] == value


def test_text_values_are_exact_literals_never_executable():
    tree = compiled('sector = "Energy and Infrastructure" and ticker != AAPL')
    assert evaluate_condition(tree, {"sector": "Energy and Infrastructure", "ticker": "MSFT"})
    assert not evaluate_condition(tree, {"sector": "Energy", "ticker": "MSFT"})
    assert compiled("sector not equal to Technology")["op"] == "ne"
    assert compiled("시장 = 미국")["value"] == "US"


@pytest.mark.parametrize("text,market", [
    ("", None), ("거래량이 충분한 종목", "KR"), ("volume ratio >=", None),
    ("거래량 1.5배 이상", None), ("volume ratio >= 150%", None),
    ("trading value >= 100", None), ("거래대금 >= 100억원", "US"),
    ("close > 10 USD and trading value > 1억원", None),
    ("RSI 30 이하", "KR"), ("20 day average volume >= 100000", None),
    ("volume ratio >= 1.5 over the last 20 days", None),
    ("daily change >= 3% buy immediately", None),
    ("volume > __import__('os').system('touch failed')", None),
    ("volume >= NaN", None), ("volume >= inf", None), ("volume >= -10", None),
    ("close strength >= 75", None), ("close strength >= 101%", None),
    ("sector > Tech", None), ("sector = \"Tech", None),
    ("market = EU", None), ("volume >= 10 and", None),
    ("(volume >= 10", None), ("volume >= 10)", None),
    ("not " * 30 + "halted", None), (" or ".join(["halted"] * 101), None),
    ("daily change > 1억%", None), ("volume >= 10 USD", None),
    ("volume >= 100,00", None),
])
def test_unsupported_or_ambiguous_input_never_returns_partial_dsl(text, market):
    draft = compile_condition_text(text, market=market)
    assert draft["status"] == "needs_clarification"
    assert draft["condition"] is None
    assert draft["normalized_rules"] == []
    assert draft["issues"]


def test_cli_outputs_compatible_dsl_and_never_overwrites_on_uncertainty(tmp_path, capsys):
    output = tmp_path / "condition.json"
    assert main(["--text", "volume ratio >= 1.5", "--output", str(output)]) == 0
    assert json.loads(output.read_text("utf-8")) == compiled("volume ratio >= 1.5")
    old = output.read_bytes()
    assert main(["--text", "volume is high", "--output", str(output)]) == 2
    assert output.read_bytes() == old
    assert "needs_clarification" in capsys.readouterr().out


@pytest.mark.parametrize("text,market", [(None, None), ("x" * 4001, None), ("volume > 1", "EU")])
def test_gross_invalid_input_is_rejected(text, market):
    with pytest.raises(ValueError):
        compile_condition_text(text, market=market)


def test_bounded_long_whitespace_draft_keeps_whole_request_validation():
    # Exercise the maximum-size user-facing path that previously repartitioned
    # the same whitespace run in both tokenizer and numeric suffix matching.
    padding = " " * 3800
    draft = compile_condition_text("volume >= 10" + padding + "unsupported")
    assert draft["status"] == "needs_clarification"
    assert draft["condition"] is None
    assert draft["normalized_rules"] == []
    # Long whitespace is still valid between explicit numeric components and
    # around the Korean connector; the fix does not trim unsupported content.
    tree = compiled("volume >= 10" + padding + "주")
    assert tree == {"field": "volume", "op": "gte", "value": 10}
    tree = compiled("volume >= 10" + " " * 1800 + "및" + " " * 1800 + "not halted")
    assert evaluate_condition(tree, {"volume": 10, "halted": False})
