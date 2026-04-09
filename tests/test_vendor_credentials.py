import unittest
from unittest.mock import Mock, patch

from tradingagents.dataflows.api_keys import _normalize_key_value
from tradingagents.dataflows.naver_news import validate_naver_credentials
from tradingagents.dataflows.opendart import validate_opendart_credentials
from tradingagents.dataflows.vendor_exceptions import VendorConfigurationError


class VendorCredentialTests(unittest.TestCase):
    def test_normalize_key_value_rejects_redacted_placeholder(self):
        self.assertIsNone(_normalize_key_value("[REDACTED]"))
        self.assertIsNone(_normalize_key_value("  <REDACTED>  "))
        self.assertEqual(_normalize_key_value(" real-key "), "real-key")

    @patch("tradingagents.dataflows.naver_news.get_api_key", side_effect=lambda name: "configured")
    @patch("tradingagents.dataflows.naver_news.requests.get")
    def test_validate_naver_credentials_raises_configuration_error_on_401(self, mock_get, _mock_key):
        response = Mock(status_code=401, reason="Unauthorized")
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        with self.assertRaises(VendorConfigurationError):
            validate_naver_credentials()

    @patch("tradingagents.dataflows.opendart.get_api_key", return_value="configured")
    @patch("tradingagents.dataflows.opendart.requests.get")
    def test_validate_opendart_credentials_raises_configuration_error_on_invalid_zip(self, mock_get, _mock_key):
        response = Mock()
        response.raise_for_status.return_value = None
        response.content = b"not-a-zip"
        mock_get.return_value = response

        with self.assertRaises(VendorConfigurationError):
            validate_opendart_credentials()


if __name__ == "__main__":
    unittest.main()
