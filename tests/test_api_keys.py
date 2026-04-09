import json
import tempfile
import unittest
from unittest.mock import patch

from tradingagents.dataflows import api_keys


class ApiKeysTests(unittest.TestCase):
    def setUp(self):
        api_keys._load_documented_keys.cache_clear()

    def tearDown(self):
        api_keys._load_documented_keys.cache_clear()

    def test_supports_opendart_alias_env_name(self):
        with patch.dict("os.environ", {"OPEN_DART_API_KEY": "alias-key"}, clear=True):
            self.assertEqual(api_keys.get_api_key("OPENDART_API_KEY"), "alias-key")

    def test_strips_wrapping_quotes_and_whitespace(self):
        with patch.dict("os.environ", {"NAVER_CLIENT_ID": "  'quoted-id'  "}, clear=True):
            self.assertEqual(api_keys.get_api_key("NAVER_CLIENT_ID"), "quoted-id")

    def test_reads_json_fallback_from_config_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = f"{temp_dir}/api_keys.json"
            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"OPENDART_API_KEY": "json-key"}, handle)

            with patch.dict("os.environ", {"TRADINGAGENTS_API_KEYS_PATH": path}, clear=True):
                self.assertEqual(api_keys.get_api_key("OPENDART_API_KEY"), "json-key")

    def test_legacy_markdown_fallback_still_works(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = f"{temp_dir}/list_api_keys.md"
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(
                    "Alpha Vantage: alpha-key\n\n"
                    "Naver:\n"
                    "- Client ID: naver-id\n"
                    "- Client Secret: naver-secret\n\n"
                    "OpenDart: opendart-key\n"
                )

            with patch.dict("os.environ", {"TRADINGAGENTS_API_KEYS_PATH": path}, clear=True):
                self.assertEqual(api_keys.get_api_key("NAVER_CLIENT_SECRET"), "naver-secret")


if __name__ == "__main__":
    unittest.main()
