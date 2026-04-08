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
    "005930": {
        "display_name": "삼성전자",
        "display_name_kr": "삼성전자",
        "display_name_en": "Samsung Electronics",
        "symbol": "005930.KS",
        "aliases": ("삼성전자", "Samsung Electronics", "SAMSUNG", "005930", "005930.KS"),
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
    "278470": {
        "display_name": "에이피알",
        "display_name_kr": "에이피알",
        "display_name_en": "APR",
        "symbol": "278470.KS",
        "aliases": ("에이피알", "APR", "278470", "278470.KS"),
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
