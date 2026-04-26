import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tradingagents.summary_image.openai_image import render_openai_summary_image


class OpenAiSummaryImageTests(unittest.TestCase):
    def test_missing_api_key_skips_without_png_or_exception(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False):
                metadata = render_openai_summary_image(
                    spec={
                        "title": "TradingAgents US 계좌 운용 리포트 요약",
                        "run": {"run_id": "run", "date": "2026-04-26", "status": "success"},
                        "account": {"account_value": "비공개", "available_cash": "비공개", "min_cash_buffer": "비공개", "mode": "계좌 기준"},
                        "counts": {"add_now": 0, "pilot_ready": 0, "close_confirm": 1, "trim_to_fund": 1, "reduce_risk": 0, "stop_loss": 0, "exit": 0},
                        "top_priority": [{"ticker": "TSM"}],
                        "next_checkpoints": [],
                        "risks": [],
                        "footer": "report-only",
                    },
                    output_path=root / "summary_card_ai.png",
                    prompt_path=root / "summary_image_prompt.txt",
                    metadata_path=root / "summary_image_metadata.json",
                    settings=SimpleNamespace(
                        image_model="gpt-image-2",
                        image_size="1024x1536",
                        image_quality="medium",
                        request_timeout=1.0,
                    ),
                )

            saved = json.loads((root / "summary_image_metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["status"], "skipped")
            self.assertEqual(saved["reason"], "missing_openai_api_key")
            self.assertTrue((root / "summary_image_prompt.txt").exists())
            self.assertFalse((root / "summary_card_ai.png").exists())


if __name__ == "__main__":
    unittest.main()
