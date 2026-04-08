import unittest
from unittest.mock import patch

from tradingagents.dataflows.api_keys import get_api_key


class ApiKeysTests(unittest.TestCase):
    def test_supports_opendart_alias_env_name(self):
        with patch.dict("os.environ", {"OPEN_DART_API_KEY": "alias-key"}, clear=True):
            self.assertEqual(get_api_key("OPENDART_API_KEY"), "alias-key")

    def test_strips_wrapping_quotes_and_whitespace(self):
        with patch.dict("os.environ", {"NAVER_CLIENT_ID": "  'quoted-id'  "}, clear=True):
            self.assertEqual(get_api_key("NAVER_CLIENT_ID"), "quoted-id")


if __name__ == "__main__":
    unittest.main()
