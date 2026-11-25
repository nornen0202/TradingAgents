"""Read the latest completed KRX stock session in bulk for strategy research."""
from __future__ import annotations

import re

from tradingagents.dataflows.krx_open_api import call_krx_open_api


_BOARDS = {"KS": ("KOSPI", "stk_bydd_trd"), "KQ": ("KOSDAQ", "ksq_bydd_trd")}


class KrxResearchCloses:
    """Cache each board (including unavailable results) for one research build."""

    def __init__(self, clock):
        self.clock = clock
        self.boards = {}

    def _board(self, board, day):
        key = board, day
        if key not in self.boards:
            self.boards[key] = self._read(board, day)
        return self.boards[key]

    def _read(self, board, day):
        market, dataset = _BOARDS[board]
        token = day.strftime("%Y%m%d")
        try:
            payload = call_krx_open_api(f"/svc/apis/sto/{dataset}", {"basDd": token}, timeout=4.0)
        except (OSError, RuntimeError, ValueError):
            return {}
        observed = self.clock().isoformat()
        rows = payload.get("OutBlock_1") if isinstance(payload, dict) else None
        if not isinstance(rows, list):
            return {}
        result, seen, duplicates = {}, set(), set()
        for row in rows:
            if not isinstance(row, dict) or row.get("BAS_DD") != token or row.get("MKT_NM") != market:
                continue
            code = row.get("ISU_CD")
            if not isinstance(code, str) or not re.fullmatch(r"[0-9]{6}", code):
                continue
            if code in seen:
                duplicates.add(code)
            seen.add(code)
            value = str(row.get("TDD_CLSPRC"))
            if len(value) > 16 or not re.fullmatch(r"[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+", value):
                continue
            price = int(value.replace(",", ""))
            if price > 0:
                result[code] = {"source": "KRX_OPEN_API", "dataset": dataset, "board": market,
                                "ticker": code, "session": day.isoformat(), "price": price,
                                "currency": "KRW", "adjustment": "unadjusted", "observed_at": observed}
        return {code: close for code, close in result.items() if code not in duplicates}

    def __call__(self, ticker, day):
        code, _, board = ticker.partition(".")
        if board in _BOARDS:
            return self._board(board, day).get(code)
        matches = [close for market in _BOARDS if (close := self._board(market, day).get(code))]
        return matches[0] if len(matches) == 1 else None
