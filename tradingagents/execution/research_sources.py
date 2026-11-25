"""Save the bounded source receipts for the 2019 disclosed-constituent study."""
from datetime import date, datetime, timedelta, timezone
import io
import json
import math
from pathlib import Path
import re
import time
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile
from zoneinfo import ZoneInfo

import requests

from tradingagents.atomic_io import atomic_write_bytes, atomic_write_json
from tradingagents.dataflows.integrity import session_date
from tradingagents.dataflows.opendart import _get_opendart_key
from tradingagents.dataflows.sec_edgar import _get_json

SEC_HOLDINGS = "https://www.sec.gov/Archives/edgar/data/884394/000119312519302203/d818891dn30d.htm"
KR_HOLDINGS = "https://m.samsungfund.com/sheet/20191007/2ETF01_20190930.pdf"
FB_RENAME = "https://www.sec.gov/Archives/edgar/data/1326801/000132680122000070/may312022-exhibit991.htm"
# Top five individual security lines of each published 2019-09-30 holdings
# table, ranked by value/weight before inspecting the subsequent prices.
UNIVERSE = {
    "US": {"benchmark": "SPY",
           "satellites": {"MSFT": "0000789019", "AAPL": "0000320193", "AMZN": "0001018724",
                          "META": "0001326801", "BRK-B": "0001067983"}},
    "KR": {"benchmark": "069500.KS",
           "satellites": {"005930.KS": "00126380", "000660.KS": "00164779", "035420.KS": "00266961",
                          "005380.KS": "00164742", "055550.KS": "00382199"}},
}
PRICE_WARMUP = "2018-12-01"
FILING_WARMUP = "2017-01-01"
PRICE_COLUMNS = ("Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits", "Capital Gains")
_SEC_FORMS = {"10-K", "10-K/A"}
_XBRL = "{http://www.xbrl.org/2003/instance}"


def _day(value):
    try:
        day = date.fromisoformat(value)
        return day if day.isoformat() == value else None
    except (TypeError, ValueError):
        return None


def _number(value):
    if isinstance(value, bool):
        return None
    try:
        n = float(value)
        return n if math.isfinite(n) else None
    except (ValueError, TypeError, OverflowError):
        return None


def _retain(root, name, load, *, binary=False):
    path = root / name
    if not path.exists():
        value = load()
        if binary:
            atomic_write_bytes(path, value)
        else:
            atomic_write_json(path, value)
    return path.read_bytes() if binary else json.loads(path.read_bytes())


def _sec_rows(block):
    columns = ("accessionNumber", "acceptanceDateTime", "filingDate", "form", "reportDate")
    arrays = [block.get(column) for column in columns]
    if any(not isinstance(array, list) for array in arrays) or len(set(map(len, arrays))) != 1:
        raise ValueError("SEC submission metadata is incomplete.")
    return (dict(zip(columns, values)) for values in zip(*arrays))


def _sec_filings(cik, root, final_day):
    source = "https://data.sec.gov/submissions/"
    base = _retain(root, f"sec-{cik}-submissions.json", lambda: _get_json(f"{source}CIK{cik}.json"))
    filings = base["filings"]
    blocks = [filings["recent"]]
    for part in filings.get("files", []):
        name = part.get("name", "")
        if (re.fullmatch(rf"CIK{cik}-submissions-\d+\.json", name)
                and FILING_WARMUP <= part.get("filingTo", "")):
            blocks.append(_retain(root, f"sec-{name}", lambda: _get_json(source + name)))
    return [row for block in blocks for row in _sec_rows(block)
            if row["form"] in _SEC_FORMS and FILING_WARMUP <= row["filingDate"] <= final_day]


def sec_vintages(facts, filings, final_day):
    """Match duration and instant facts from the same accepted annual accession."""
    good = {}
    for row in filings:
        filed = _day(row.get("filingDate"))
        end = _day(row.get("reportDate"))
        accession = row.get("accessionNumber", "")
        try:
            accepted = datetime.fromisoformat(row["acceptanceDateTime"].replace("Z", "+00:00"))
        except (KeyError, TypeError, ValueError, AttributeError):
            continue
        if (not filed or not end or not end <= filed <= final_day or accepted.utcoffset() is None
                or not re.fullmatch(r"\d{10}-\d{2}-\d{6}", accession) or row.get("form") not in _SEC_FORMS):
            continue
        if not end <= accepted.astimezone(ZoneInfo("America/New_York")).date() <= final_day:
            continue
        if accession in good and good[accession][0] != row:
            raise ValueError("Conflicting SEC accession metadata.")
        good[accession] = row, filed, accepted, end
    values = {}
    for tag in ("NetIncomeLoss", "ProfitLoss", "Assets"):
        for fact in facts.get(tag, {}).get("units", {}).get("USD", []):
            accession = fact.get("accn")
            if accession not in good:
                continue
            row, filed, _, limit = good[accession]
            end = _day(fact.get("end"))
            start = _day(fact.get("start"))
            value = _number(fact.get("val"))
            if (not end or end > limit or value is None or fact.get("filed") != filed.isoformat()
                    or fact.get("form") != row["form"]):
                continue
            if tag == "Assets":
                if fact.get("start") is not None or value <= 0:
                    continue
            elif not start or not 300 <= (end - start).days <= 400:
                continue
            values.setdefault((accession, end), {}).setdefault(tag, set()).add(value)
    output = []
    for (accession, end), tags in values.items():
        assets = tags.get("Assets", ())
        profit = tags.get("NetIncomeLoss") or tags.get("ProfitLoss", ())
        if len(assets) != 1 or len(profit) != 1:
            continue
        row, filed, accepted, _ = good[accession]
        output.append({"id": accession, "period_end": end.isoformat(), "filed": filed.isoformat(),
                       "accepted_at": accepted.isoformat(), "form": row["form"], "source": "SEC",
                       "roa": next(iter(profit)) / next(iter(assets))})
    return sorted(output, key=lambda row: (row["filed"], row["id"], row["period_end"]))


def _dart_request(endpoint, params, *, binary=False):
    try:
        response = requests.get(f"https://opendart.fss.or.kr/api/{endpoint}",
                                params={"crtfc_key": _get_opendart_key(), **params}, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ValueError(f"OpenDART request failed ({type(exc).__name__}).") from None
    if binary:
        return response.content
    return response.json()


def _dart_filings(corp, root, final_day):
    output = []
    for page in range(1, 21):
        params = {"corp_code": corp, "bgn_de": FILING_WARMUP.replace("-", ""),
                  "end_de": final_day.replace("-", ""), "pblntf_detail_ty": "A001",
                  "last_reprt_at": "N", "page_count": 100, "page_no": page}
        payload = _retain(root, f"dart-{corp}-list-{page}.json", lambda: _dart_request("list.json", params))
        if payload.get("status") == "013":
            return output
        if payload.get("status") != "000" or not isinstance(payload.get("list"), list):
            raise ValueError(f'OpenDART list status {payload.get("status")}.')
        output.extend(payload["list"])
        if page >= int(payload.get("total_page", 0)):
            return output
    raise ValueError("OpenDART annual filing pagination is incomplete.")


def _local_tag(tag):
    return tag.rsplit("}", 1)[-1]


def dart_vintages(raw, corp, filing, final_day):
    accession = filing.get("rcept_no", "")
    receipt = str(filing.get("rcept_dt", ""))
    period = re.search(r"사업보고서\s*\((\d{4})\.(\d{2})\)", filing.get("report_nm", ""))
    if (filing.get("corp_code") != corp or not re.fullmatch(r"\d{14}", accession)
            or not re.fullmatch(r"\d{8}", receipt) or not period):
        return []
    filed = _day(f"{receipt[:4]}-{receipt[4:6]}-{receipt[6:8]}")
    if not filed or not FILING_WARMUP <= filed.isoformat() <= final_day:
        return []
    with ZipFile(io.BytesIO(raw)) as zipped:
        member, = [item for item in zipped.infolist() if item.filename.lower().endswith(".xbrl")]
        if member.file_size > 30_000_000:
            raise ValueError("OpenDART XBRL exceeds the input limit.")
        doc = ElementTree.fromstring(zipped.read(member))
    contexts = {}
    for item in doc.findall(f"{_XBRL}context"):
        if item.findtext(f"{_XBRL}entity/{_XBRL}identifier") != corp:
            continue
        dimensions = [node.text for node in item.iter() if _local_tag(node.tag) in {"explicitMember", "typedMember"}]
        if len(dimensions) != 1 or not str(dimensions[0]).endswith(":ConsolidatedMember"):
            continue
        start = _day(item.findtext(f"{_XBRL}period/{_XBRL}startDate"))
        instant = _day(item.findtext(f"{_XBRL}period/{_XBRL}instant"))
        end = _day(item.findtext(f"{_XBRL}period/{_XBRL}endDate"))
        if instant and instant <= filed:
            contexts[item.get("id")] = "Assets", instant
        elif start and end and end <= filed and 300 <= (end - start).days <= 400:
            contexts[item.get("id")] = "ProfitLoss", end
    values = {}
    for item in doc:
        matched = contexts.get(item.get("contextRef"))
        if not matched or _local_tag(item.tag) != matched[0] or item.get("unitRef") != "KRW":
            continue
        value = _number(item.text)
        if value is not None and (matched[0] != "Assets" or value > 0):
            values.setdefault(matched[1], {}).setdefault(matched[0], set()).add(value)
    latest = max(values, default=date.min)
    if latest.strftime("%Y.%m") != ".".join(period.groups()):
        return []  # The document must identify the requested report period.
    return [{"id": accession, "period_end": end.isoformat(), "filed": filed.isoformat(),
             "form": filing["report_nm"], "source": "OpenDART",
             "roa": next(iter(tags["ProfitLoss"])) / next(iter(tags["Assets"]))}
            for end, tags in sorted(values.items())
            if len(tags.get("Assets", ())) == len(tags.get("ProfitLoss", ())) == 1]


def _yahoo_panel(ticker, final_day):
    import yfinance as yf
    from yfinance.exceptions import YFException

    end = (date.fromisoformat(final_day) + timedelta(days=1)).isoformat()
    try:
        frame = yf.Ticker(ticker).history(start=PRICE_WARMUP, end=end, auto_adjust=False, actions=True, raise_errors=True)
    except YFException as exc:
        raise RuntimeError(type(exc).__name__) from None
    rows = {}
    for stamp, row in frame.iterrows():
        session = session_date(stamp).date().isoformat()
        if not PRICE_WARMUP <= session <= final_day:
            continue
        if session in rows:
            raise ValueError("Duplicate Yahoo daily session.")
        rows[session] = {field: _number(row.get(field, 0 if field == "Capital Gains" else None)) for field in PRICE_COLUMNS}
    return rows


def _kis_kospi200(final_day):
    from tradingagents.portfolio.kis import KisClient

    client = KisClient.from_api_keys(environment="real")
    first, cursor = date.fromisoformat(PRICE_WARMUP), date.fromisoformat(final_day)
    fields = {"Open": "stck_oprc", "High": "stck_hgpr", "Low": "stck_lwpr",
              "Close": "stck_clpr", "Volume": "acml_vol"}
    rows = {}
    for page in range(30):
        if page:
            time.sleep(.25)
        data = client.domestic_daily_itemchartprice("069500", start_date=first, end_date=cursor,
                                                   market_division="J", period_division="D", adjusted_price="1")
        days = []
        for row in data.get("output2", []):
            stamp = row.get("stck_bsop_date", "")
            if not re.fullmatch(r"\d{8}", stamp):
                continue
            day = _day(f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:]}")
            if day is None or not first <= day <= cursor:
                continue
            values = {key: _number(row.get(name)) for key, name in fields.items()}
            if any(value is None for value in values.values()):
                continue
            label = day.isoformat()
            if label in rows and values != rows[label]:
                raise ValueError("KIS contains conflicting daily bars.")
            rows[label] = values
            days.append(day)
        if not days:
            break
        oldest = min(days)
        if oldest <= first:
            break
        cursor = oldest - timedelta(days=1)
    else:
        raise ValueError("KIS price history exceeds the research page limit.")
    if len(rows) < 1500:
        raise ValueError("KIS KOSPI200 history is incomplete.")
    return rows


def collect_sources(root: Path, cutoff, final_days):
    """Retain original files and normalized data. Credentials stay in the downloader."""
    root.mkdir(parents=True, exist_ok=True)
    identity = {"as_of": cutoff.isoformat(), "final_days": final_days, "universe": UNIVERSE}
    if _retain(root, "collect-identity.json", lambda: identity) != identity:
        raise ValueError("The collection directory belongs to another cutoff or universe.")
    prices, vintages, receipts, gaps = {}, {}, {}, {}
    for market, cohort in UNIVERSE.items():
        final = final_days[market]
        for symbol in [cohort["benchmark"], *cohort["satellites"]]:
            try:
                prices[symbol] = _retain(root, f"yahoo-{symbol}.json", lambda: _yahoo_panel(symbol, final))
            except (ValueError, RuntimeError, OSError) as exc:
                gaps[symbol] = type(exc).__name__
                prices[symbol] = {}
        for symbol, issuer in cohort["satellites"].items():
            vintages[symbol], receipts[symbol] = [], []
            try:
                if market == "US":
                    receipts[symbol] = _sec_filings(issuer, root, final)
                    endpoint = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{issuer}.json"
                    facts = _retain(root, f"sec-{issuer}-facts.json", lambda: _get_json(endpoint))
                    vintages[symbol] = sec_vintages(facts["facts"]["us-gaap"], receipts[symbol], date.fromisoformat(final))
                    continue
                receipts[symbol] = _dart_filings(issuer, root, final)
                for filing in receipts[symbol]:
                    number = filing.get("rcept_no", "")
                    receipt = filing.get("rcept_dt", "")
                    if (not re.fullmatch(r"\d{14}", number) or not re.fullmatch(r"\d{8}", receipt)
                            or not FILING_WARMUP.replace("-", "") <= receipt <= final.replace("-", "")
                            or filing.get("corp_code") != issuer or "사업보고서" not in filing.get("report_nm", "")):
                        continue
                    try:
                        params = {"rcept_no": number, "reprt_code": "11011"}
                        raw = _retain(root, f"dart-{number}.zip",
                                      lambda: _dart_request("fnlttXbrl.xml", params, binary=True), binary=True)
                        statements = dart_vintages(raw, issuer, filing, final)
                        if not statements:
                            gaps[f"{symbol}:{number}"] = "No matched consolidated annual facts"
                        vintages[symbol].extend(statements)
                    except (OSError, ValueError, ElementTree.ParseError, BadZipFile):
                        gaps[f"{symbol}:{number}"] = "Original XBRL unavailable or ambiguous"
            except (OSError, ValueError, RuntimeError, KeyError) as exc:
                gaps[f"{symbol}:filings"] = type(exc).__name__
    fx = _retain(root, "yahoo-KRW-X.json", lambda: _yahoo_panel("KRW=X", max(final_days.values())))
    benchmark = UNIVERSE["KR"]["benchmark"]
    benchmark_source = {"ohlcv": "Yahoo", "actions": "Yahoo"}
    try:
        kis = _retain(root, "kis-069500-raw.json", lambda: _kis_kospi200(final_days["KR"]))
        yahoo = prices[benchmark]
        if not yahoo or any(row.get("Stock Splits") for row in yahoo.values()):
            raise ValueError("KODEX 200 requires matching independent split coverage.")
        overlap = kis.keys() & yahoo.keys()
        differences = [day for day in overlap if yahoo[day]["Close"] and
                       abs(kis[day]["Close"] / yahoo[day]["Close"] - 1) > .002]
        prices[benchmark] = {day: row | {field: yahoo.get(day, {}).get(field) or 0
                                       for field in ("Dividends", "Stock Splits", "Capital Gains")}
                             for day, row in kis.items()}
        benchmark_source = {"ohlcv": "KIS unadjusted", "actions": "Yahoo", "overlap": len(overlap),
                            "missing_yahoo_action_dates": sorted(kis.keys() - yahoo.keys()),
                            "close_difference_over_20bps": sorted(differences)}
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        gaps[f"{benchmark}:kis"] = type(exc).__name__
    result = {"identity": identity, "prices": prices, "fx": fx, "vintages": vintages, "receipts": receipts,
              "gaps": gaps, "kr_benchmark_source": benchmark_source}
    atomic_write_json(root / "market-inputs.json", result)
    return result
