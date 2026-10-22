"""Financial situation memory using hybrid BM25 plus regime-tag retrieval."""

from __future__ import annotations

from rank_bm25 import BM25Okapi
from typing import Any, List, Tuple
import re
import json
import sqlite3
from pathlib import Path
from copy import deepcopy
from datetime import date, datetime, time, timedelta, timezone


def _clock(value: Any, *, allow_date: bool = False) -> datetime:
    if isinstance(value, datetime):
        stamp = value
    elif isinstance(value, date) and allow_date:
        return datetime.combine(value, time.min, timezone.utc)
    elif isinstance(value, str):
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            if not allow_date:
                raise ValueError("A timezone-aware memory clock is required")
            return datetime.combine(date.fromisoformat(value), time.min, timezone.utc)
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        raise ValueError("A verified memory clock is required")
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError("A timezone-aware memory clock is required")
    return stamp.astimezone(timezone.utc)


def _query_cutoff(value: Any) -> tuple[datetime | None, bool]:
    if value is None:
        return None, False
    date_only = ((isinstance(value, date) and not isinstance(value, datetime))
                 or (isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is not None))
    cutoff = _clock(value, allow_date=date_only)
    return (cutoff + timedelta(days=1), True) if date_only else (cutoff, False)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _eligible_clocks(metadata: dict, cutoff: datetime, *, date_only: bool,
                     knowledge_cutoff: datetime) -> bool:
    try:
        # Availability and local ingestion are always actual instants. A legacy
        # outcome date cannot manufacture either clock for an archived memory.
        available = _clock(metadata.get("available_at"))
        ingested = _clock(metadata.get("ingested_at"))
        known_value = metadata.get("outcome_known_at")
        if date_only and "outcome_known_at" not in metadata:
            known_value = metadata.get("settlement_date")
        known = _clock(known_value, allow_date=date_only)
        clocks = [known, available, ingested]
        for field in ("settlement_date", "settled_at"):
            if field in metadata:
                clocks.append(_clock(metadata[field], allow_date=date_only))
        if available < max([clocks[0], *clocks[3:]]) or ingested < available:
            return False
        # A current/future date query must not expose evidence that has not yet
        # become available in the real world. Keep the original date boundary
        # exclusive, while the actual-now knowledge boundary stays inclusive.
        if any(stamp > knowledge_cutoff or (stamp >= cutoff if date_only else stamp > cutoff)
               for stamp in clocks):
            return False
        if "trade_date" in metadata:
            # A trade-date label remains a calendar date, even for an instant
            # query. Its outcome/availability/ingestion must still be verified.
            trade = _clock(metadata["trade_date"], allow_date=True)
            if (trade >= cutoff if date_only else trade > cutoff) or trade > known:
                return False
    except (TypeError, ValueError, OverflowError):
        return False
    return True


class FinancialSituationMemory:
    """Memory system for storing and retrieving financial situations."""

    def __init__(self, name: str, config: dict | None = None):
        self.name = name
        self.config = config or {}
        self.documents: List[str] = []
        self.recommendations: List[str] = []
        self.metadata: List[dict[str, Any]] = []
        self.bm25 = None
        self.default_n_matches = int(self.config.get("memory_n_matches", 2))
        self.max_entries = max(1, int(self.config.get("memory_max_entries", 500)))
        self.as_of: str | date | datetime | None = None
        self.store_path = None
        if self.config.get("memory_dir"):
            if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
                raise ValueError("Invalid memory name")
            self.store_path = Path(self.config["memory_dir"]) / f"{name}.sqlite3"
            if self.store_path.exists():
                with sqlite3.connect(self.store_path) as connection:
                    rows = connection.execute("SELECT situation, advice, metadata FROM memories ORDER BY id").fetchall()
                for situation, advice, metadata in rows:
                    self.documents.append(situation)
                    self.recommendations.append(advice)
                    try:
                        decoded = json.loads(metadata)
                    except (TypeError, ValueError):
                        decoded = {}
                    self.metadata.append(decoded if isinstance(decoded, dict) else {})

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b\w+\b", text.lower())

    def _extract_regime_tags(self, text: str) -> set[str]:
        lowered = text.lower()
        tags: set[str] = set()
        keyword_groups = {
            "volatility": ("volatility", "atr", "drawdown", "swing", "high-volatility"),
            "trend_up": ("uptrend", "trending up", "breakout", "bullish", "momentum"),
            "trend_down": ("downtrend", "trending down", "selloff", "bearish", "breakdown"),
            "range_bound": ("range-bound", "sideways", "consolidation", "choppy"),
            "rates": ("interest rate", "fed", "fomc", "yield", "monetary"),
            "earnings": ("earnings", "guidance", "quarter", "revenue", "eps"),
            "insider": ("insider", "buyback", "share issuance"),
            "kr": ("krx", ".ks", ".kq", "korea", "한국", "원", "krw"),
            "us": ("nasdaq", "nyse", "usd", "federal reserve", "u.s.", "us/eastern"),
            "sentiment": ("sentiment", "narrative", "social", "headline"),
            "macro": ("inflation", "cpi", "gdp", "macro", "employment"),
        }
        for tag, keywords in keyword_groups.items():
            if any(keyword in lowered for keyword in keywords):
                tags.add(tag)
        return tags

    def add_situations(self, situations_and_advice: List[Tuple]):
        """Append originals; max_entries limits a query, never stored history."""
        for item in situations_and_advice:
            if len(item) == 2:
                situation, recommendation = item
                metadata = {}
            elif len(item) == 3:
                situation, recommendation, metadata = item
            else:
                raise ValueError("Each memory entry must be (situation, recommendation) or (situation, recommendation, metadata).")

            combined_metadata = deepcopy(dict(metadata or {}))
            combined_metadata.setdefault("regime_tags", sorted(self._extract_regime_tags(str(situation))))
            self.documents.append(str(situation))
            self.recommendations.append(str(recommendation))
            self.metadata.append(combined_metadata)
            if self.store_path:
                self.store_path.parent.mkdir(parents=True, exist_ok=True)
                with sqlite3.connect(self.store_path) as connection:
                    connection.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, situation TEXT, advice TEXT, metadata TEXT)")
                    connection.execute("INSERT INTO memories (situation, advice, metadata) VALUES (?, ?, ?)",
                                       (str(situation), str(recommendation), json.dumps(combined_metadata, ensure_ascii=False)))
        self.bm25 = None

    def get_memories(
        self,
        current_situation: str,
        n_matches: int | None = None,
        metadata_filters: dict[str, Any] | None = None,
        as_of: str | date | datetime | None = None,
    ) -> List[dict]:
        """Retrieve only evidence eligible before ranking and retention.

        An aware timestamp is an exact, inclusive cutoff: outcome, availability,
        ingestion and any settlement clock must be timezone-aware. A YYYY-MM-DD
        cutoff means the entire UTC calendar day (exclusive next midnight), and
        permits legacy outcome/settlement dates. Both paths require actual aware
        availability and ingestion; missing or invalid clocks are excluded.
        Both cutoff modes are additionally bounded by actual UTC now, inclusive,
        so today's or a future as_of cannot admit future knowledge. Historical
        date boundaries remain exclusive at the following UTC midnight.
        Without as_of or self.as_of this remains an unbounded-time diagnostic
        search, not point-in-time investment evidence.
        """
        cutoff, date_only = _query_cutoff(self.as_of if as_of is None else as_of)
        knowledge_cutoff = _utc_now() if cutoff is not None else None
        if not self.documents:
            return []

        limit = n_matches if n_matches is not None else self.default_n_matches
        if limit <= 0:
            return []
        eligible = []
        for idx in range(len(self.documents)):
            metadata = self.metadata[idx] if idx < len(self.metadata) else {}
            if cutoff is not None and not _eligible_clocks(
                    metadata, cutoff, date_only=date_only, knowledge_cutoff=knowledge_cutoff):
                continue
            if metadata_filters and any(metadata.get(key) != value for key, value in metadata_filters.items()):
                continue
            eligible.append((idx, metadata))
        eligible = eligible[-self.max_entries:]
        if not eligible:
            return []

        query_tokens = self._tokenize(current_situation)
        query_tags = self._extract_regime_tags(current_situation)
        # Filtering only the returned rows still lets future entries change IDF,
        # average document length and ranking. Build the index from eligible
        # evidence so adding future memories cannot alter a historical query.
        index = BM25Okapi(
            [self._tokenize(self.documents[idx]) or ["_empty_"] for idx, _ in eligible]
        )
        self.bm25 = index
        scores = index.get_scores(query_tokens)
        max_score = max(scores) if max(scores) > 0 else 1

        ranked_results = []
        for (idx, metadata), score in zip(eligible, scores):
            normalized_bm25 = score / max_score if max_score > 0 else 0
            doc_tags = set(metadata.get("regime_tags", []))
            tag_score = len(query_tags & doc_tags) / len(query_tags | doc_tags) if (query_tags or doc_tags) else 0
            hybrid_score = 0.75 * normalized_bm25 + 0.25 * tag_score
            ranked_results.append((hybrid_score, normalized_bm25, tag_score, idx, metadata))

        ranked_results.sort(key=lambda item: item[0], reverse=True)

        results = []
        for hybrid_score, normalized_bm25, tag_score, idx, metadata in ranked_results[:limit]:
            results.append(
                {
                    "matched_situation": self.documents[idx],
                    "recommendation": self.recommendations[idx],
                    "similarity_score": hybrid_score,
                    "bm25_score": normalized_bm25,
                    "tag_overlap_score": tag_score,
                    "metadata": deepcopy(metadata),
                }
            )

        return results

    def clear(self):
        if self.store_path and self.store_path.exists():
            with sqlite3.connect(self.store_path) as connection:
                connection.execute("DELETE FROM memories")
        self.documents = []
        self.recommendations = []
        self.metadata = []
        self.bm25 = None
