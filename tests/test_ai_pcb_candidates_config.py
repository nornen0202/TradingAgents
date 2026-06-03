from tradingagents.portfolio.profiles import load_portfolio_profile
from tradingagents.scheduled.config import load_scheduled_config


def test_ai_pcb_candidates_are_in_kr_daily_analysis_universe_and_watchlist():
    config = load_scheduled_config("config/scheduled_analysis_korea.toml")
    profile = load_portfolio_profile("config/portfolio_profiles.toml", "kr_kis_default")
    candidates = {
        "000150.KS": "두산",
        "007660.KS": "이수페타시스",
        "007810.KS": "코리아써키트",
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
        "277810.KQ": "레인보우로보틱스",
    }

    assert config.run.market == "KR"
    assert candidates.keys() <= set(config.run.tickers)
    assert candidates.keys() <= set(profile.watch_tickers)
    assert {ticker: config.run.ticker_name_overrides[ticker] for ticker in candidates} == candidates


def test_ai_infrastructure_candidates_are_in_kr_daily_analysis_universe_and_watchlist():
    config = load_scheduled_config("config/scheduled_analysis_korea.toml")
    profile = load_portfolio_profile("config/portfolio_profiles.toml", "kr_kis_default")
    candidates = {
        "006400.KS": "삼성SDI",
        "010120.KS": "LS ELECTRIC",
        "018260.KS": "삼성SDS",
        "058610.KQ": "에스피지",
        "066570.KS": "LG전자",
        "108490.KQ": "로보티즈",
        "131290.KQ": "티에스이",
        "267260.KS": "HD현대일렉트릭",
        "298040.KS": "효성중공업",
        "373220.KS": "LG에너지솔루션",
        "454910.KS": "두산로보틱스",
    }

    assert config.run.market == "KR"
    assert candidates.keys() <= set(config.run.tickers)
    assert candidates.keys() <= set(profile.watch_tickers)
    assert {ticker: config.run.ticker_name_overrides[ticker] for ticker in candidates} == candidates
    assert len(config.run.tickers) == 32
    assert {"010950.KS", "020150.KS", "090360.KQ"}.isdisjoint(config.run.tickers)


def test_ai_pcb_and_power_candidates_are_in_us_daily_analysis_universe_and_watchlist():
    config = load_scheduled_config("config/scheduled_analysis.toml")
    profile = load_portfolio_profile("config/portfolio_profiles.toml", "us_kis_default")
    candidates = {
        "CRM": "Salesforce",
        "SMCI": "Super Micro Computer",
        "TXN": "Texas Instruments",
        "URI": "United Rentals",
    }
    already_present = {"ETN", "VRT"}

    assert config.run.market == "US"
    assert candidates.keys() <= set(config.run.tickers)
    assert already_present <= set(config.run.tickers)
    assert candidates.keys() <= set(profile.watch_tickers)
    assert already_present <= set(profile.watch_tickers)
    assert {ticker: config.run.ticker_name_overrides[ticker] for ticker in candidates} == candidates


def test_global_ai_infrastructure_candidates_are_in_us_daily_analysis_universe_and_watchlist():
    config = load_scheduled_config("config/scheduled_analysis.toml")
    profile = load_portfolio_profile("config/portfolio_profiles.toml", "us_kis_default")
    candidates = {
        "AMZN": "Amazon",
        "ANET": "Arista Networks",
        "COHR": "Coherent",
        "DDOG": "Datadog",
        "DELL": "Dell Technologies",
        "META": "Meta Platforms",
        "MPWR": "Monolithic Power Systems",
        "MSFT": "Microsoft",
        "QCOM": "Qualcomm",
        "SNOW": "Snowflake",
    }

    assert config.run.market == "US"
    assert candidates.keys() <= set(config.run.tickers)
    assert candidates.keys() <= set(profile.watch_tickers)
    assert {ticker: config.run.ticker_name_overrides[ticker] for ticker in candidates} == candidates
    assert len(config.run.tickers) == 34
    assert {
        "BA",
        "BE",
        "CGNX",
        "CSCO",
        "FANG",
        "FLNC",
        "FN",
        "FORM",
        "GRID",
        "HPE",
        "IBM",
        "INTC",
        "LITE",
        "NTAP",
        "OKTA",
        "ON",
        "PAVE",
        "SMMT",
        "SONY",
        "SOXX",
        "STM",
        "TER",
        "TTMI",
    }.isdisjoint(config.run.tickers)
