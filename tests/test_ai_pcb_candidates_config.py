from tradingagents.portfolio.profiles import load_portfolio_profile
from tradingagents.scheduled.config import load_scheduled_config


def test_ai_pcb_candidates_are_in_kr_daily_analysis_universe_and_watchlist():
    config = load_scheduled_config("config/scheduled_analysis_korea.toml")
    profile = load_portfolio_profile("config/portfolio_profiles.toml", "kr_kis_default")
    candidates = {
        "000150.KS": "두산",
        "007660.KS": "이수페타시스",
        "007810.KS": "코리아써키트",
        "020150.KS": "롯데에너지머티리얼즈",
        "222800.KQ": "심텍",
    }

    assert config.run.market == "KR"
    assert candidates.keys() <= set(config.run.tickers)
    assert candidates.keys() <= set(profile.watch_tickers)
    assert {ticker: config.run.ticker_name_overrides[ticker] for ticker in candidates} == candidates


def test_domestic_watchlist_additions_are_in_kr_daily_analysis_universe_and_watchlist():
    config = load_scheduled_config("config/scheduled_analysis_korea.toml")
    profile = load_portfolio_profile("config/portfolio_profiles.toml", "kr_kis_default")
    candidates = {
        "012330.KS": "현대모비스",
        "035420.KS": "NAVER",
        "036930.KQ": "주성엔지니어링",
        "090360.KQ": "로보스타",
        "277810.KQ": "레인보우로보틱스",
    }

    assert config.run.market == "KR"
    assert candidates.keys() <= set(config.run.tickers)
    assert candidates.keys() <= set(profile.watch_tickers)
    assert {ticker: config.run.ticker_name_overrides[ticker] for ticker in candidates} == candidates


def test_ai_pcb_and_power_candidates_are_in_us_daily_analysis_universe_and_watchlist():
    config = load_scheduled_config("config/scheduled_analysis.toml")
    profile = load_portfolio_profile("config/portfolio_profiles.toml", "us_kis_default")
    candidates = {
        "STM": "STMicroelectronics",
        "TTMI": "TTM Technologies",
        "TXN": "Texas Instruments",
    }
    already_present = {"ETN", "VRT"}

    assert config.run.market == "US"
    assert candidates.keys() <= set(config.run.tickers)
    assert already_present <= set(config.run.tickers)
    assert candidates.keys() <= set(profile.watch_tickers)
    assert already_present <= set(profile.watch_tickers)
    assert {ticker: config.run.ticker_name_overrides[ticker] for ticker in candidates} == candidates
