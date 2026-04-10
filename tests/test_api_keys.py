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

    def test_reads_utf8_bom_json_fallback(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = f"{temp_dir}/api_keys.json"
            with open(path, "w", encoding="utf-8-sig") as handle:
                json.dump({"KIS_Developers_APP_KEY": "kis-key"}, handle)

            with patch.dict("os.environ", {"TRADINGAGENTS_API_KEYS_PATH": path}, clear=True):
                self.assertEqual(api_keys.get_api_key("KIS_APP_KEY"), "kis-key")

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

    def test_reads_kis_developers_aliases_from_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = f"{temp_dir}/api_keys.json"
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(
                    {
                        "KIS_Developers_APP_KEY": "kis-app-key",
                        "KIS_Developers_APP_SECRET": "kis-app-secret",
                        "KIS_Developers_ACCOUNT_NO": "12345678",
                        "KIS_Developers_PRODUCT_CODE": "01",
                    },
                    handle,
                )

            with patch.dict("os.environ", {"TRADINGAGENTS_API_KEYS_PATH": path}, clear=True):
                self.assertEqual(api_keys.get_api_key("KIS_APP_KEY"), "kis-app-key")
                self.assertEqual(api_keys.get_api_key("KIS_APP_SECRET"), "kis-app-secret")
                self.assertEqual(api_keys.get_api_key("KIS_ACCOUNT_NO"), "12345678")
                self.assertEqual(api_keys.get_api_key("KIS_PRODUCT_CODE"), "01")


if __name__ == "__main__":
    unittest.main()
