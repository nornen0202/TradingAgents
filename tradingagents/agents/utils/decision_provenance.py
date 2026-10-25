"""Bounded parser-input receipts; never retain model text or order authority."""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from threading import Lock

from tradingagents.schemas.decision import _extract_json_object, parse_structured_decision

SCHEMA = "tradingagents.decision-parser-input-provenance/v1"
MAX_EVENTS = 96
MAX_INPUT_CHARS = 500_000
_ACTIVE = ContextVar("decision_parser_input_provenance", default=None)
_STAGES = {
    "research manager investment plan": "RESEARCH_MANAGER",
    "trader execution plan": "TRADER",
    "portfolio manager final decision": "PORTFOLIO_MANAGER",
}
_ACTIONS = {"NONE", "STARTER", "ADD"}
_FIELDS = ("conditional_entry_action", "conditional_entry_valid_until")
_LOCALIZED_NARRATIVE = ("entry_logic", "exit_logic", "position_sizing", "risk_limits",
                        "catalysts", "invalidators", "watchlist_triggers")
_OUTCOMES = {"VALIDATED_INITIAL", "VALIDATED_REPAIR", "VALIDATION_REJECTED",
             "STRUCTURAL_FALLBACK", "PROVIDER_FALLBACK", "PROVIDER_EXCEPTION"}


def _sha(text):
    if not isinstance(text, str) or len(text) > MAX_INPUT_CHARS:
        raise ValueError("Unbounded parser input")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _machine_projection(text):
    decision = parse_structured_decision(text).to_dict()
    projection = {key: value for key, value in decision.items() if key not in _LOCALIZED_NARRATIVE}
    digest = hashlib.sha256(json.dumps(projection, sort_keys=True, separators=(",", ":"),
                                       allow_nan=False).encode()).hexdigest()
    return digest


def _shape(data, key):
    if key not in data:
        return {"presence": "ABSENT", "type": "MISSING", "valid_shape": None}
    value = data[key]
    kind = ("NULL" if value is None else "BOOLEAN" if isinstance(value, bool) else
            "STRING" if isinstance(value, str) else "NUMBER" if isinstance(value, (int, float)) else
            "OBJECT" if isinstance(value, dict) else "ARRAY" if isinstance(value, list) else "OTHER")
    if key == "conditional_entry_action":
        valid = isinstance(value, str) and value.upper() in _ACTIONS
    else:
        valid = value is None
        if isinstance(value, str):
            try:
                clock = datetime.fromisoformat(value)
                valid = clock.tzinfo is not None and clock.utcoffset() is not None
            except ValueError:
                valid = False
    return {"presence": "EXPLICIT_NULL" if value is None else "PRESENT",
            "type": kind, "valid_shape": valid}


class DecisionProvenanceRecorder:
    def __init__(self, ticker, *, max_events=MAX_EVENTS):
        self.ticker = ticker
        self.max_events = min(MAX_EVENTS, max_events) if type(max_events) is int and max_events > 0 else MAX_EVENTS
        self.events = []
        self.lock = Lock()
        self.failed = False
        self.overflow = 0

    def activate(self):
        return _ACTIVE.set(self)

    @staticmethod
    def reset(token):
        _ACTIVE.reset(token)

    def add(self, context, attempt, outcome, *, text=None, normalized=None):
        if outcome not in _OUTCOMES or type(attempt) is not int or attempt < 0:
            raise ValueError("Unverified trace origin")
        row = {"stage": _STAGES.get(context, "UNKNOWN"), "attempt": attempt,
               "outcome": outcome, "recorded_at": datetime.now(timezone.utc).isoformat(),
               "input_form": "LLM_MESSAGE_CONTENT_PARSER_INPUT_TEXT",
               "parser_input_text_sha256": None, "candidate_status": "NO_INPUT",
               "conditional_fields": None, "defaulted_fields": [],
               "normalized_text_sha256": None, "machine_projection_sha256": None}
        if text is not None:
            row["parser_input_text_sha256"] = _sha(text)
            try:
                data = _extract_json_object(text)  # Exactly the canonical parser's candidate selection.
            except Exception:
                row["candidate_status"] = "UNPARSEABLE"
            else:
                row["candidate_status"] = "MAPPING"
                row["conditional_fields"] = {key: _shape(data, key) for key in _FIELDS}
                # These are the existing parser's falsy-value defaults, not new validation rules.
                row["defaulted_fields"] = (["conditional_entry_action"] if not data.get("conditional_entry_action") else [])
                if ("conditional_entry_valid_until" not in data
                        or data["conditional_entry_valid_until"] is not None and not data["conditional_entry_valid_until"]):
                    row["defaulted_fields"].append("conditional_entry_valid_until")
        if normalized is not None:
            row["normalized_text_sha256"] = _sha(normalized)
            row["machine_projection_sha256"] = _machine_projection(normalized)
        with self.lock:
            if row["stage"] == "UNKNOWN":
                self.failed = True
            if len(self.events) >= self.max_events:
                self.failed = True
                self.overflow = min(self.overflow + 1, 1_000_000)
                return
            row["sequence"] = len(self.events)
            self.events.append(row)

    def snapshot(self):
        with self.lock:
            return deepcopy(self.events), self.failed, self.overflow


def record_decision_input(context, attempt, outcome, *, text=None, normalized=None):
    """Trace failures cannot change a model call, tuple, retry or investment decision."""
    recorder = _ACTIVE.get()
    if recorder is None:
        return
    try:
        recorder.add(context, attempt, outcome, text=text, normalized=normalized)
    except Exception:
        mark_trace_unverified()


def mark_trace_unverified():
    try:
        recorder = _ACTIVE.get()
        if recorder is not None:
            recorder.failed = True
    except Exception:
        pass


class DecisionProvenanceSession:
    """One new ticker's optional trace, isolated even if capture initialization fails."""
    def __init__(self, ticker):
        self.ticker = ticker
        self.failed = False
        self.binding = None
        try:
            self.recorder = DecisionProvenanceRecorder(ticker)
        except Exception:
            self.recorder = None
            self.failed = True

    @contextmanager
    def capture(self):
        neutral = _ACTIVE.set(None)
        token = None
        try:
            if self.recorder is not None:
                try:
                    token = self.recorder.activate()
                except Exception:
                    self.failed = True
            yield
        finally:
            if token is not None:
                try:
                    self.recorder.reset(token)
                except Exception:
                    self.failed = True
            try:
                _ACTIVE.reset(neutral)
            except Exception:
                self.failed = True
                _ACTIVE.set(None)

    def bind_selected(self, text, final_state):
        try:
            stage = "UNKNOWN"
            candidates = [("PORTFOLIO_MANAGER", final_state.get("final_trade_decision")),
                          ("PORTFOLIO_MANAGER", (final_state.get("risk_debate_state") or {}).get("judge_decision")),
                          ("RESEARCH_MANAGER", (final_state.get("investment_debate_state") or {}).get("judge_decision"))]
            for name, candidate in candidates:
                if isinstance(candidate, str) and candidate.strip() == text:
                    stage = name
                    break
            self.binding = {"selected_stage": stage, "selected_post_localization_text_sha256": _sha(text),
                            "selected_machine_projection_sha256": _machine_projection(text)}
        except Exception:
            self.failed = True

    def receipt(self):
        try:
            events, failed, overflow = self.recorder.snapshot() if self.recorder is not None else ([], True, 0)
            binding = deepcopy(self.binding)
            if binding is not None:
                matches = [e for e in events if e["stage"] == binding["selected_stage"]
                           and e["normalized_text_sha256"] is not None]
                exact = [e for e in matches if e["normalized_text_sha256"] == binding["selected_post_localization_text_sha256"]]
                semantic = [e for e in matches if e["machine_projection_sha256"] == binding["selected_machine_projection_sha256"]]
                candidates = exact or semantic
                chosen = candidates[0] if len(candidates) == 1 and binding["selected_stage"] != "UNKNOWN" else None
                binding["binding_basis"] = ("EXACT_NORMALIZED_TEXT" if exact else "MACHINE_PROJECTION_ONLY_POST_LOCALIZATION") if chosen else "AMBIGUOUS" if len(candidates) > 1 else "MISSING_OR_DIVERGED"
                binding["normalized_pre_localization_text_sha256"] = chosen["normalized_text_sha256"] if chosen else None
                binding["selected_origin"] = chosen["outcome"] if chosen else None
                binding["full_decision_text_equal"] = bool(chosen and exact)
                binding["selected_machine_projection_matches"] = bool(chosen and chosen["machine_projection_sha256"] == binding["selected_machine_projection_sha256"])
                if not binding["selected_machine_projection_matches"]:
                    failed = True
            status = "UNVERIFIED" if self.failed or failed else "RECORDED" if events else "NOT_COLLECTED"
            return {"schema": SCHEMA, "ticker": self.ticker, "status": status,
                    "events": events, "overflow_count": overflow, "selected_binding": binding,
                    "projection_scope": "CANONICAL_FIELDS_EXCEPT_LOCALIZED_NARRATIVE",
                    "projection_excluded_fields": list(_LOCALIZED_NARRATIVE),
                    "full_translation_faithfulness_verified": False,
                    "raw_response_retained": False, "execution_authorized": False}
        except Exception:
            return {"schema": SCHEMA, "ticker": self.ticker, "status": "UNVERIFIED", "events": [],
                    "overflow_count": 0, "selected_binding": None,
                    "projection_scope": "CANONICAL_FIELDS_EXCEPT_LOCALIZED_NARRATIVE",
                    "projection_excluded_fields": list(_LOCALIZED_NARRATIVE),
                    "full_translation_faithfulness_verified": False,
                    "raw_response_retained": False, "execution_authorized": False}
