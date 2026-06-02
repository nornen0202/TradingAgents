from __future__ import annotations

import re
from dataclasses import dataclass


class InstrumentResolutionError(ValueError):
    """Raised when a user-provided instrument cannot be normalized."""


@dataclass(frozen=True)
class InstrumentProfile:
    input_symbol: str
    normalized_symbol: str
    country: str
    display_name: str
    exchange: str
    timezone: str
    currency: str
    display_name_kr: str | None = None
    display_name_en: str | None = None
    yahoo_symbol: str | None = None
    krx_code: str | None = None
    dart_corp_code: str | None = None
    aliases: tuple[str, ...] = tuple()

    @property
    def primary_symbol(self) -> str:
        return self.normalized_symbol

    def to_dict(self) -> dict[str, str | None | list[str]]:
        return {
            "input_symbol": self.input_symbol,
            "normalized_symbol": self.normalized_symbol,
            "primary_symbol": self.normalized_symbol,
            "display_name": self.display_name,
            "display_name_kr": self.display_name_kr,
            "display_name_en": self.display_name_en,
            "exchange": self.exchange,
            "country": self.country,
            "timezone": self.timezone,
            "currency": self.currency,
            "yahoo_symbol": self.yahoo_symbol or self.normalized_symbol,
            "krx_code": self.krx_code,
            "dart_corp_code": self.dart_corp_code,
            "aliases": list(self.aliases),
        }


_KRX_COMPANIES = {
    "000150": {
        "display_name": "두산",
        "display_name_kr": "두산",
        "display_name_en": "Doosan Corporation",
        "symbol": "000150.KS",
        "aliases": ("두산", "Doosan", "Doosan Corporation", "000150", "000150.KS"),
    },
    "007660": {
        "display_name": "이수페타시스",
        "display_name_kr": "이수페타시스",
        "display_name_en": "ISU Petasys",
        "symbol": "007660.KS",
        "aliases": ("이수페타시스", "ISU Petasys", "Isu Petasys", "007660", "007660.KS"),
    },
    "007810": {
        "display_name": "코리아써키트",
        "display_name_kr": "코리아써키트",
        "display_name_en": "Korea Circuit",
        "symbol": "007810.KS",
        "aliases": ("코리아써키트", "Korea Circuit", "007810", "007810.KS"),
    },
    "020150": {
        "display_name": "롯데에너지머티리얼즈",
        "display_name_kr": "롯데에너지머티리얼즈",
        "display_name_en": "Lotte Energy Materials",
        "symbol": "020150.KS",
        "aliases": (
            "롯데에너지머티리얼즈",
            "Lotte Energy Materials",
            "020150",
            "020150.KS",
        ),
    },
    "036930": {
        "display_name": "주성엔지니어링",
        "display_name_kr": "주성엔지니어링",
        "display_name_en": "Jusung Engineering",
        "symbol": "036930.KQ",
        "aliases": ("주성엔지니어링", "Jusung Engineering", "036930", "036930.KQ"),
    },
    "090360": {
        "display_name": "로보스타",
        "display_name_kr": "로보스타",
        "display_name_en": "Robostar",
        "symbol": "090360.KQ",
        "aliases": ("로보스타", "Robostar", "090360", "090360.KQ"),
    },
    "222800": {
        "display_name": "심텍",
        "display_name_kr": "심텍",
        "display_name_en": "SIMMTECH",
        "symbol": "222800.KQ",
        "aliases": ("심텍", "SIMMTECH", "Simmtech", "222800", "222800.KQ"),
    },
    "277810": {
        "display_name": "레인보우로보틱스",
        "display_name_kr": "레인보우로보틱스",
        "display_name_en": "Rainbow Robotics",
        "symbol": "277810.KQ",
        "aliases": ("레인보우로보틱스", "Rainbow Robotics", "277810", "277810.KQ"),
    },
    "005930": {
        "display_name": "삼성전자",
        "display_name_kr": "삼성전자",
        "display_name_en": "Samsung Electronics",
        "symbol": "005930.KS",
        "aliases": ("삼성전자", "Samsung Electronics", "SAMSUNG", "005930", "005930.KS"),
    },
    "006400": {
        "display_name": "삼성SDI",
        "display_name_kr": "삼성SDI",
        "display_name_en": "Samsung SDI",
        "symbol": "006400.KS",
        "aliases": ("삼성SDI", "Samsung SDI", "006400", "006400.KS"),
    },
    "000660": {
        "display_name": "SK하이닉스",
        "display_name_kr": "SK하이닉스",
        "display_name_en": "SK hynix",
        "symbol": "000660.KS",
        "aliases": ("SK하이닉스", "SK hynix", "Hynix", "000660", "000660.KS"),
    },
    "012450": {
        "display_name": "한화에어로스페이스",
        "display_name_kr": "한화에어로스페이스",
        "display_name_en": "Hanwha Aerospace",
        "symbol": "012450.KS",
        "aliases": ("한화에어로스페이스", "Hanwha Aerospace", "012450", "012450.KS"),
    },
    "035420": {
        "display_name": "NAVER",
        "display_name_kr": "네이버",
        "display_name_en": "NAVER",
        "symbol": "035420.KS",
        "aliases": ("네이버", "NAVER", "035420", "035420.KS"),
    },
    "005380": {
        "display_name": "현대차",
        "display_name_kr": "현대차",
        "display_name_en": "Hyundai Motor",
        "symbol": "005380.KS",
        "aliases": ("현대차", "Hyundai Motor", "005380", "005380.KS"),
    },
    "009150": {
        "display_name": "삼성전기",
        "display_name_kr": "삼성전기",
        "display_name_en": "Samsung Electro-Mechanics",
        "symbol": "009150.KS",
        "aliases": ("삼성전기", "Samsung Electro-Mechanics", "009150", "009150.KS"),
    },
    "010120": {
        "display_name": "LS ELECTRIC",
        "display_name_kr": "LS ELECTRIC",
        "display_name_en": "LS ELECTRIC",
        "symbol": "010120.KS",
        "aliases": ("LS ELECTRIC", "엘에스일렉트릭", "LS일렉트릭", "010120", "010120.KS"),
    },
    "010140": {
        "display_name": "삼성중공업",
        "display_name_kr": "삼성중공업",
        "display_name_en": "Samsung Heavy Industries",
        "symbol": "010140.KS",
        "aliases": ("삼성중공업", "Samsung Heavy Industries", "010140", "010140.KS"),
    },
    "010950": {
        "display_name": "S-Oil",
        "display_name_kr": "에쓰오일",
        "display_name_en": "S-Oil",
        "symbol": "010950.KS",
        "aliases": ("S-Oil", "에쓰오일", "010950", "010950.KS"),
    },
    "011070": {
        "display_name": "LG이노텍",
        "display_name_kr": "LG이노텍",
        "display_name_en": "LG Innotek",
        "symbol": "011070.KS",
        "aliases": ("LG이노텍", "LG Innotek", "011070", "011070.KS"),
    },
    "012330": {
        "display_name": "현대모비스",
        "display_name_kr": "현대모비스",
        "display_name_en": "Hyundai Mobis",
        "symbol": "012330.KS",
        "aliases": ("현대모비스", "Hyundai Mobis", "012330", "012330.KS"),
    },
    "018260": {
        "display_name": "삼성SDS",
        "display_name_kr": "삼성SDS",
        "display_name_en": "Samsung SDS",
        "symbol": "018260.KS",
        "aliases": ("삼성SDS", "Samsung SDS", "018260", "018260.KS"),
    },
    "034020": {
        "display_name": "두산에너빌리티",
        "display_name_kr": "두산에너빌리티",
        "display_name_en": "Doosan Enerbility",
        "symbol": "034020.KS",
        "aliases": ("두산에너빌리티", "Doosan Enerbility", "034020", "034020.KS"),
    },
    "034220": {
        "display_name": "LG디스플레이",
        "display_name_kr": "LG디스플레이",
        "display_name_en": "LG Display",
        "symbol": "034220.KS",
        "aliases": ("LG디스플레이", "LG Display", "034220", "034220.KS"),
    },
    "042700": {
        "display_name": "한미반도체",
        "display_name_kr": "한미반도체",
        "display_name_en": "Hanmi Semiconductor",
        "symbol": "042700.KS",
        "aliases": ("한미반도체", "Hanmi Semiconductor", "042700", "042700.KS"),
    },
    "066570": {
        "display_name": "LG전자",
        "display_name_kr": "LG전자",
        "display_name_en": "LG Electronics",
        "symbol": "066570.KS",
        "aliases": ("LG전자", "LG Electronics", "066570", "066570.KS"),
    },
    "058470": {
        "display_name": "리노공업",
        "display_name_kr": "리노공업",
        "display_name_en": "LEENO Industrial",
        "symbol": "058470.KQ",
        "aliases": ("리노공업", "LEENO Industrial", "058470", "058470.KQ"),
    },
    "058610": {
        "display_name": "에스피지",
        "display_name_kr": "에스피지",
        "display_name_en": "SPG",
        "symbol": "058610.KQ",
        "aliases": ("에스피지", "SPG", "058610", "058610.KQ"),
    },
    "064400": {
        "display_name": "LG CNS",
        "display_name_kr": "LG CNS",
        "display_name_en": "LG CNS",
        "symbol": "064400.KS",
        "aliases": ("LG CNS", "064400", "064400.KS"),
    },
    "095340": {
        "display_name": "ISC",
        "display_name_kr": "ISC",
        "display_name_en": "ISC",
        "symbol": "095340.KS",
        "aliases": ("ISC", "095340", "095340.KS"),
    },
    "108490": {
        "display_name": "로보티즈",
        "display_name_kr": "로보티즈",
        "display_name_en": "Robotis",
        "symbol": "108490.KQ",
        "aliases": ("로보티즈", "Robotis", "108490", "108490.KQ"),
    },
    "131290": {
        "display_name": "티에스이",
        "display_name_kr": "티에스이",
        "display_name_en": "TSE",
        "symbol": "131290.KQ",
        "aliases": ("티에스이", "TSE", "131290", "131290.KQ"),
    },
    "396500": {
        "display_name": "TIGER Fn반도체TOP10",
        "display_name_kr": "TIGER Fn반도체TOP10",
        "display_name_en": "TIGER Fn Semiconductor TOP10",
        "symbol": "396500.KS",
        "aliases": ("TIGER Fn반도체TOP10", "396500", "396500.KS"),
    },
    "278470": {
        "display_name": "에이피알",
        "display_name_kr": "에이피알",
        "display_name_en": "APR",
        "symbol": "278470.KS",
        "aliases": ("에이피알", "APR", "278470", "278470.KS"),
    },
    "267260": {
        "display_name": "HD현대일렉트릭",
        "display_name_kr": "HD현대일렉트릭",
        "display_name_en": "HD Hyundai Electric",
        "symbol": "267260.KS",
        "aliases": ("HD현대일렉트릭", "HD Hyundai Electric", "267260", "267260.KS"),
    },
    "298040": {
        "display_name": "효성중공업",
        "display_name_kr": "효성중공업",
        "display_name_en": "Hyosung Heavy Industries",
        "symbol": "298040.KS",
        "aliases": ("효성중공업", "Hyosung Heavy Industries", "298040", "298040.KS"),
    },
    "353200": {
        "display_name": "대덕전자",
        "display_name_kr": "대덕전자",
        "display_name_en": "Daeduck Electronics",
        "symbol": "353200.KS",
        "aliases": ("대덕전자", "Daeduck Electronics", "353200", "353200.KS"),
    },
    "373220": {
        "display_name": "LG에너지솔루션",
        "display_name_kr": "LG에너지솔루션",
        "display_name_en": "LG Energy Solution",
        "symbol": "373220.KS",
        "aliases": ("LG에너지솔루션", "LG Energy Solution", "373220", "373220.KS"),
    },
    "403870": {
        "display_name": "HPSP",
        "display_name_kr": "HPSP",
        "display_name_en": "HPSP",
        "symbol": "403870.KQ",
        "aliases": ("HPSP", "403870", "403870.KQ"),
    },
    "454910": {
        "display_name": "두산로보틱스",
        "display_name_kr": "두산로보틱스",
        "display_name_en": "Doosan Robotics",
        "symbol": "454910.KS",
        "aliases": ("두산로보틱스", "Doosan Robotics", "454910", "454910.KS"),
    },
}

_ALIAS_TO_KRX_CODE: dict[str, str] = {}
for code, profile in _KRX_COMPANIES.items():
    _ALIAS_TO_KRX_CODE[code] = code
    _ALIAS_TO_KRX_CODE[profile["symbol"].upper()] = code
    for alias in profile["aliases"]:
        _ALIAS_TO_KRX_CODE[str(alias).upper()] = code


def is_krx_symbol(symbol: str) -> bool:
    return bool(re.fullmatch(r"\d{6}\.(KS|KQ)", symbol.upper()))


def resolve_instrument(user_input: str) -> InstrumentProfile:
    raw_value = (user_input or "").strip()
    if not raw_value:
        raise InstrumentResolutionError("Instrument input is empty.")

    upper = raw_value.upper()
    code = _ALIAS_TO_KRX_CODE.get(upper)
    if code:
        return _build_krx_profile(raw_value, code)

    if is_krx_symbol(upper):
        code = upper.split(".", 1)[0]
        if code in _KRX_COMPANIES:
            return _build_krx_profile(raw_value, code)
        return _build_generic_krx_profile(raw_value, upper, code)

    if re.fullmatch(r"\d{6}", raw_value):
        if raw_value in _KRX_COMPANIES:
            return _build_krx_profile(raw_value, raw_value)
        return _build_generic_krx_profile(raw_value, f"{raw_value}.KS", raw_value)

    if re.fullmatch(r"[A-Za-z][A-Za-z0-9.\-]{0,14}", raw_value):
        return InstrumentProfile(
            input_symbol=raw_value,
            normalized_symbol=upper,
            display_name=upper,
            country="US",
            exchange="US",
            timezone="US/Eastern",
            currency="USD",
            display_name_en=upper,
            yahoo_symbol=upper,
            aliases=(upper,),
        )

    raise InstrumentResolutionError(
        f"Could not resolve instrument '{user_input}'. Pass an exchange-qualified ticker or a known company name/code."
    )


def _build_krx_profile(input_symbol: str, code: str) -> InstrumentProfile:
    data = _KRX_COMPANIES[code]
    symbol = data["symbol"]
    exchange = "KOSDAQ" if symbol.endswith(".KQ") else "KRX"
    return InstrumentProfile(
        input_symbol=input_symbol,
        normalized_symbol=symbol,
        display_name=data["display_name"],
        display_name_kr=data.get("display_name_kr"),
        display_name_en=data.get("display_name_en"),
        exchange=exchange,
        country="KR",
        timezone="Asia/Seoul",
        currency="KRW",
        yahoo_symbol=symbol,
        krx_code=code,
        aliases=tuple(dict.fromkeys([*data.get("aliases", ()), symbol, code])),
    )


def _build_generic_krx_profile(input_symbol: str, symbol: str, code: str) -> InstrumentProfile:
    return InstrumentProfile(
        input_symbol=input_symbol,
        normalized_symbol=symbol,
        display_name=code,
        display_name_kr=code,
        display_name_en=code,
        exchange="KRX",
        country="KR",
        timezone="Asia/Seoul",
        currency="KRW",
        yahoo_symbol=symbol,
        krx_code=code,
        aliases=(code, symbol),
    )
