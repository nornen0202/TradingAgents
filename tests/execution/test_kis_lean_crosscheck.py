import pandas as pd
import pytest

from tradingagents.execution.kis_lean_crosscheck import compare_fixture


class FixtureConverter:
    @staticmethod
    def export(data, output_dir, *, market_type):
        from pathlib import Path
        assert market_type == "krx"
        symbol, frame = next(iter(data.items()))
        target = Path(output_dir) / f"{symbol}.csv"
        frame = frame.assign(date=frame.date.dt.strftime("%Y%m%d"))
        frame.to_csv(target, index=False, header=False)
        return {symbol: target}


def test_fixture_compares_independent_after_cost_ledger_and_keeps_scope(tmp_path):
    receipt = compare_fixture(FixtureConverter, tmp_path)
    assert receipt["input"]["sessions"] == 10
    assert (receipt["input"]["start"], receipt["input"]["end"]) == ("2026-06-08", "2026-06-19")
    assert receipt["lean_input_conversion_executed"] is True
    assert receipt["lean_backtest_executed"] is receipt["market_performance_verified"] is False
    gross, costs, taxed = [row["decimal_reference"] for row in receipt["cases"]]
    assert gross["quantity"] == 30 and costs["quantity"] == taxed["quantity"] == 29
    assert gross["final_krw"] > costs["final_krw"] > taxed["final_krw"]
    assert taxed["tax_reserve_krw"] > 0


def test_converter_cannot_change_price_or_date(tmp_path):
    class ChangedPrice(FixtureConverter):
        @staticmethod
        def export(data, output_dir, *, market_type):
            target = FixtureConverter.export(data, output_dir, market_type=market_type)
            path, = target.values()
            frame = pd.read_csv(path, header=None)
            frame.iloc[0, 1] -= 1
            frame.to_csv(path, header=False, index=False)
            return target

    with pytest.raises(ValueError, match="changed the fixture prices"):
        compare_fixture(ChangedPrice, tmp_path)


def test_converter_cannot_rewrite_its_input_in_place(tmp_path):
    class ChangedInput(FixtureConverter):
        @staticmethod
        def export(data, output_dir, *, market_type):
            for frame in data.values():
                columns = ["open", "high", "low", "close"]
                frame[columns] = frame[columns] * 2
            return FixtureConverter.export(data, output_dir, market_type=market_type)

    with pytest.raises(ValueError, match="changed the fixture prices"):
        compare_fixture(ChangedInput, tmp_path)
