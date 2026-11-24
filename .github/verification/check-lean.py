import json
from pathlib import Path

root = Path("engine-evidence")
reference = json.loads((root / "reference/crosscheck.json").read_bytes())
receipt = {"scope": "ISOLATED_SYNTHETIC", "source": reference["input"], "cases": []}
for case in reference["cases"]:
    row = json.loads((root / case["scenario"] / "reconciliation.json").read_bytes())
    expected = case["decimal_reference"]
    assert len(row["fills"]) == 2, row
    assert [f["q"] for f in row["fills"]] == [expected["quantity"], -expected["quantity"]], row
    for key in ("tax_reserve_krw", "dividend_receivable_krw", "final_krw"):
        assert abs(row[key] - expected[key]) < 1e-5, (case["scenario"], key, row, expected)
    receipt["cases"].append({"scenario": case["scenario"], "engine": row, "reference": expected})
(root / "actual-engine-comparison.json").write_text(json.dumps(receipt, indent=2))
