from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _clean_float(value: Any, *, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class SourceRef:
    provider: str
    title: str
    document_type: str = "analysis"
    date: str | None = None
    url: str | None = None
    section: str | None = None
    confidence: float = 0.5

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "SourceRef":
        return cls(
            provider=_clean_text(payload.get("provider")) or "unknown",
            title=_clean_text(payload.get("title")) or _clean_text(payload.get("document")) or "Untitled source",
            document_type=_clean_text(payload.get("document_type")) or _clean_text(payload.get("type")) or "analysis",
            date=_clean_text(payload.get("date")) or None,
            url=_clean_text(payload.get("url")) or None,
            section=_clean_text(payload.get("section")) or None,
            confidence=max(0.0, min(_clean_float(payload.get("confidence"), default=0.5), 1.0)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "title": self.title,
            "document_type": self.document_type,
            "date": self.date,
            "url": self.url,
            "section": self.section,
            "confidence": round(self.confidence, 4),
        }


@dataclass(frozen=True)
class EvidenceItem:
    claim: str
    ticker: str
    source_refs: tuple[SourceRef, ...]
    direction: str = "context"
    metric: str | None = None
    value: str | None = None
    period: str | None = None
    magnitude: str | None = None
    quality: float = 0.5

    @classmethod
    def from_mapping(cls, payload: dict[str, Any], *, ticker: str) -> "EvidenceItem":
        raw_sources = payload.get("source_refs") or payload.get("sources") or []
        source_refs = tuple(
            SourceRef.from_mapping(item)
            for item in raw_sources
            if isinstance(item, dict)
        )
        return cls(
            claim=_clean_text(payload.get("claim")) or _clean_text(payload.get("summary")) or "Imported evidence",
            ticker=_clean_text(payload.get("ticker")) or ticker,
            source_refs=source_refs,
            direction=_clean_text(payload.get("direction")) or "context",
            metric=_clean_text(payload.get("metric")) or None,
            value=_clean_text(payload.get("value")) or None,
            period=_clean_text(payload.get("period")) or None,
            magnitude=_clean_text(payload.get("magnitude")) or None,
            quality=max(0.0, min(_clean_float(payload.get("quality"), default=0.5), 1.0)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim": self.claim,
            "ticker": self.ticker,
            "direction": self.direction,
            "metric": self.metric,
            "value": self.value,
            "period": self.period,
            "magnitude": self.magnitude,
            "quality": round(self.quality, 4),
            "source_refs": [source.to_dict() for source in self.source_refs],
        }


@dataclass(frozen=True)
class ProviderDefinition:
    id: str
    display_name: str
    capabilities: tuple[str, ...]
    access: str
    credential_envs: tuple[str, ...] = tuple()
    priority: int = 100
    notes: str = ""

    def to_dict(self, *, configured: bool = False, imported: bool = False) -> dict[str, Any]:
        if self.access == "free":
            status = "available_public"
        elif imported:
            status = "available_imported"
        elif configured:
            status = "configured_optional"
        else:
            status = "unconfigured_optional"
        return {
            "id": self.id,
            "display_name": self.display_name,
            "capabilities": list(self.capabilities),
            "access": self.access,
            "credential_envs": list(self.credential_envs),
            "priority": self.priority,
            "status": status,
            "configured": configured,
            "imported": imported,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class EarningsEventPack:
    ticker: str
    asof: str
    status: str = "unavailable"
    actuals: dict[str, Any] = field(default_factory=dict)
    guidance: dict[str, Any] = field(default_factory=dict)
    consensus_delta: dict[str, Any] = field(default_factory=dict)
    transcript_available: bool = False
    transcript_highlights: tuple[str, ...] = tuple()
    next_catalysts: tuple[str, ...] = tuple()
    source_refs: tuple[SourceRef, ...] = tuple()
    warnings: tuple[str, ...] = tuple()

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker,
            "asof": self.asof,
            "status": self.status,
            "actuals": self.actuals,
            "guidance": self.guidance,
            "consensus_delta": self.consensus_delta,
            "transcript_available": self.transcript_available,
            "transcript_highlights": list(self.transcript_highlights),
            "next_catalysts": list(self.next_catalysts),
            "source_refs": [source.to_dict() for source in self.source_refs],
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class ThesisTracker:
    ticker: str
    asof: str
    status: str = "insufficient_evidence"
    security_readiness: str = "watch_only"
    pillars: tuple[str, ...] = tuple()
    falsifiers: tuple[str, ...] = tuple()
    strengthened_by: tuple[str, ...] = tuple()
    weakened_by: tuple[str, ...] = tuple()
    evidence_count: int = 0
    source_quality_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker,
            "asof": self.asof,
            "status": self.status,
            "security_readiness": self.security_readiness,
            "pillars": list(self.pillars),
            "falsifiers": list(self.falsifiers),
            "strengthened_by": list(self.strengthened_by),
            "weakened_by": list(self.weakened_by),
            "evidence_count": self.evidence_count,
            "source_quality_score": round(self.source_quality_score, 4),
        }
