from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


ACTION_TRACKER_SCHEMA: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS action_recommendations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      run_id TEXT NOT NULL,
      ticker TEXT NOT NULL,
      action TEXT NOT NULL,
      risk_action TEXT,
      recommended_price REAL,
      confidence REAL,
      trigger_type TEXT,
      source TEXT,
      prism_agreement TEXT,
      was_executed INTEGER DEFAULT 0,
      skip_reason TEXT,
      created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS action_outcomes (
      recommendation_id INTEGER,
      return_1d REAL,
      return_3d REAL,
      return_5d REAL,
      return_10d REAL,
      return_20d REAL,
      return_60d REAL,
      benchmark_return_5d REAL,
      max_drawdown_20d REAL,
      max_favorable_excursion_20d REAL,
      outcome_label TEXT,
      updated_at TEXT,
      FOREIGN KEY(recommendation_id) REFERENCES action_recommendations(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS trade_journal (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      ticker TEXT NOT NULL,
      buy_run_id TEXT,
      sell_run_id TEXT,
      buy_context_json TEXT,
      sell_context_json TEXT,
      profit_rate REAL,
      holding_days INTEGER,
      missed_signals_json TEXT,
      overreacted_signals_json TEXT,
      lessons_json TEXT,
      pattern_tags_json TEXT,
      one_line_summary TEXT,
      confidence_score REAL,
      created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS learned_intuitions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      category TEXT NOT NULL,
      condition TEXT NOT NULL,
      insight TEXT NOT NULL,
      confidence REAL,
      supporting_trades INTEGER,
      success_rate REAL,
      source_journal_ids_json TEXT,
      is_active INTEGER DEFAULT 1,
      created_at TEXT NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_action_recommendations_run ON action_recommendations(run_id)",
    "CREATE INDEX IF NOT EXISTS idx_action_recommendations_ticker ON action_recommendations(ticker)",
    "CREATE INDEX IF NOT EXISTS idx_trade_journal_ticker ON trade_journal(ticker)",
)


@dataclass(frozen=True)
class ActionPerformanceSummary:
    recommendations: int = 0
    outcomes: int = 0
    closed_trades: int = 0
    learned_intuitions: int = 0
    by_action: dict[str, dict[str, Any]] = field(default_factory=dict)
    prism_agreement: dict[str, dict[str, Any]] = field(default_factory=dict)
    action_buckets: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "recommendations": self.recommendations,
            "outcomes": self.outcomes,
            "closed_trades": self.closed_trades,
            "learned_intuitions": self.learned_intuitions,
            "by_action": self.by_action,
            "prism_agreement": self.prism_agreement,
            "action_buckets": self.action_buckets,
        }


def action_tracker_schema_sql() -> str:
    return ";\n".join(statement.strip().rstrip(";") for statement in ACTION_TRACKER_SCHEMA) + ";"
