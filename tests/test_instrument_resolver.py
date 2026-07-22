import unittest

from tradingagents.agents.utils.instrument_resolver import resolve_instrument
from tradingagents.graph.propagation import Propagator


class InstrumentResolverTests(unittest.TestCase):
    def test_resolves_us_symbol(self):
        profile = resolve_instrument("AAPL")
        self.assertEqual(profile.primary_symbol, "AAPL")
        self.assertEqual(profile.display_name, "Apple")
        self.assertEqual(profile.country, "US")
        self.assertIn("AAPL", profile.aliases)

    def test_resolves_exchange_qualified_krx_symbol(self):
        profile = resolve_instrument("005930.KS")
        self.assertEqual(profile.primary_symbol, "005930.KS")
        self.assertEqual(profile.country, "KR")

    def test_resolves_numeric_krx_code(self):
        profile = resolve_instrument("005930")
        self.assertEqual(profile.primary_symbol, "005930.KS")

    def test_resolves_korean_company_name(self):
        profile = resolve_instrument("삼성전자")
        self.assertEqual(profile.primary_symbol, "005930.KS")

    def test_resolves_known_krx_english_name(self):
        profile = resolve_instrument("NAVER")
        self.assertEqual(profile.primary_symbol, "035420.KS")

    def test_resolves_known_krx_numeric_code(self):
        profile = resolve_instrument("035420")
        self.assertEqual(profile.primary_symbol, "035420.KS")

    def test_resolves_sjg_sejong_without_repeating_ticker_as_name(self):
        profile = resolve_instrument("033530.KS")
        self.assertEqual(profile.primary_symbol, "033530.KS")
        self.assertEqual(profile.display_name, "SJG세종")
        self.assertEqual(profile.display_name_en, "SJG Sejong")

    def test_resolves_ai_pcb_krx_candidates(self):
        expected = {
            "두산": "000150.KS",
            "이수페타시스": "007660.KS",
            "코리아써키트": "007810.KS",
            "롯데에너지머티리얼즈": "020150.KS",
            "심텍": "222800.KQ",
        }
        for name, ticker in expected.items():
            with self.subTest(name=name):
                profile = resolve_instrument(name)
                self.assertEqual(profile.primary_symbol, ticker)

    def test_resolves_domestic_watchlist_additions(self):
        expected = {
            "삼성SDI": "006400.KS",
            "LS ELECTRIC": "010120.KS",
            "삼성SDS": "018260.KS",
            "현대모비스": "012330.KS",
            "주성엔지니어링": "036930.KQ",
            "에스피지": "058610.KQ",
            "LG전자": "066570.KS",
            "로보스타": "090360.KQ",
            "로보티즈": "108490.KQ",
            "티에스이": "131290.KQ",
            "HD현대일렉트릭": "267260.KS",
            "레인보우로보틱스": "277810.KQ",
            "효성중공업": "298040.KS",
            "LG에너지솔루션": "373220.KS",
            "두산로보틱스": "454910.KS",
        }
        for name, ticker in expected.items():
            with self.subTest(name=name):
                profile = resolve_instrument(name)
                self.assertEqual(profile.primary_symbol, ticker)

    def test_resolves_kr_alias_set_for_hynix(self):
        profile = resolve_instrument("SK hynix")
        self.assertEqual(profile.primary_symbol, "000660.KS")
        self.assertIn("000660", profile.aliases)

    def test_propagator_normalizes_instrument_into_state(self):
        state = Propagator().create_initial_state("삼성전자", "2026-01-15")
        self.assertEqual(state["company_of_interest"], "005930.KS")
        self.assertEqual(state["input_instrument"], "삼성전자")
        self.assertEqual(state["instrument_profile"]["country"], "KR")


if __name__ == "__main__":
    unittest.main()
