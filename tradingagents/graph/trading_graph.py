# TradingAgents/graph/trading_graph.py

import os
from copy import deepcopy
from pathlib import Path
import json
from datetime import date
import re
import hashlib
import sqlite3
from typing import Dict, Any, Tuple, List, Optional

from langgraph.prebuilt import ToolNode

from tradingagents.llm_clients import create_llm_client
from tradingagents.llm_clients.role_config import codex_client_kwargs

from tradingagents.agents import *
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)
from tradingagents.dataflows.config import set_config
from tradingagents.schemas import StructuredDecisionValidationError, parse_structured_decision

# Import the new abstract tool methods from agent_utils
from tradingagents.agents.utils.agent_utils import (
    get_stock_data,
    get_indicators,
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement,
    get_company_news,
    get_disclosures,
    get_macro_news,
    get_news,
    get_insider_transactions,
    get_global_news,
    get_social_sentiment,
    get_output_language,
    rewrite_in_output_language,
)

from .conditional_logic import ConditionalLogic
from .setup import GraphSetup
from .propagation import Propagator
from .reflection import Reflector
from .signal_processing import SignalProcessor
from tradingagents.agents.utils.macro_data_tools import get_macro_data


class TradingAgentsGraph:
    """Main class that orchestrates the trading agents framework."""

    def __init__(
        self,
        selected_analysts: Optional[List[str]] = None,
        debug=False,
        config: Dict[str, Any] = None,
        callbacks: Optional[List] = None,
    ):
        """Initialize the trading agents graph and components.

        Args:
            selected_analysts: List of analyst types to include
            debug: Whether to run in debug mode
            config: Configuration dictionary. If None, uses default config
            callbacks: Optional list of callback handlers (e.g., for tracking LLM/tool stats)
        """
        self.debug = debug
        self.config = deepcopy(config) if config is not None else deepcopy(DEFAULT_CONFIG)
        self.callbacks = callbacks or []

        # Update the interface's config
        set_config(self.config)

        # Create necessary directories
        os.makedirs(
            self.config["data_cache_dir"],
            exist_ok=True,
        )

        # Initialize LLMs with provider-specific thinking configuration
        deep_kwargs = self._get_provider_kwargs("deep")
        quick_kwargs = self._get_provider_kwargs("quick")
        output_kwargs = self._get_provider_kwargs("output")

        # Add callbacks to kwargs if provided (passed to LLM constructor)
        if self.callbacks:
            deep_kwargs["callbacks"] = self.callbacks
            quick_kwargs["callbacks"] = self.callbacks
            output_kwargs["callbacks"] = self.callbacks

        deep_client = create_llm_client(
            provider=self.config["llm_provider"],
            model=self.config["deep_think_llm"],
            base_url=self.config.get("backend_url"),
            **deep_kwargs,
        )
        output_model = (
            self.config.get("output_think_llm")
            or self.config.get("output_model")
            or self.config["quick_think_llm"]
        )
        quick_client = create_llm_client(
            provider=self.config["llm_provider"],
            model=self.config["quick_think_llm"],
            base_url=self.config.get("backend_url"),
            **quick_kwargs,
        )
        output_client = create_llm_client(
            provider=self.config["llm_provider"],
            model=output_model,
            base_url=self.config.get("backend_url"),
            **output_kwargs,
        )

        self.deep_thinking_llm = deep_client.get_llm()
        self.quick_thinking_llm = quick_client.get_llm()
        self.output_thinking_llm = output_client.get_llm()
        
        # Initialize memories
        self.bull_memory = FinancialSituationMemory("bull_memory", self.config)
        self.bear_memory = FinancialSituationMemory("bear_memory", self.config)
        self.trader_memory = FinancialSituationMemory("trader_memory", self.config)
        self.invest_judge_memory = FinancialSituationMemory("invest_judge_memory", self.config)
        self.portfolio_manager_memory = FinancialSituationMemory("portfolio_manager_memory", self.config)

        # Create tool nodes
        self.tool_nodes = self._create_tool_nodes()

        # Initialize components
        self.conditional_logic = ConditionalLogic(
            max_debate_rounds=self.config["max_debate_rounds"],
            max_risk_discuss_rounds=self.config["max_risk_discuss_rounds"],
        )
        self.graph_setup = GraphSetup(
            self.quick_thinking_llm,
            self.deep_thinking_llm,
            self.tool_nodes,
            self.bull_memory,
            self.bear_memory,
            self.trader_memory,
            self.invest_judge_memory,
            self.portfolio_manager_memory,
            self.conditional_logic,
        )

        self.propagator = Propagator(self.config["max_recur_limit"])
        self.reflector = Reflector(self.deep_thinking_llm)
        self.signal_processor = SignalProcessor()

        # State tracking
        self.curr_state = None
        self.ticker = None
        self.log_states_dict = {}  # date to full state dict

        # Set up the graph
        self.selected_analysts = selected_analysts or ["market", "social", "news", "fundamentals"]
        self._checkpoint_connection = None
        checkpointer = None
        if self.config.get("checkpoint_enabled"):
            from langgraph.checkpoint.sqlite import SqliteSaver
            directory = Path(self.config["checkpoint_dir"])
            directory.mkdir(parents=True, exist_ok=True)
            self._checkpoint_connection = sqlite3.connect(directory / "runs.sqlite3", check_same_thread=False)
            checkpointer = SqliteSaver(self._checkpoint_connection)
        self.graph = self.graph_setup.setup_graph(self.selected_analysts, checkpointer=checkpointer)

    def prepare_run(self, company_name, trade_date, analysis_date=None, callbacks=None):
        """Shared CLI/API lifecycle: resume with None to avoid duplicating messages."""
        state = self.propagator.create_initial_state(company_name, trade_date, analysis_date=analysis_date)
        from tradingagents.dataflows.integrity import safe_symbol
        safe_symbol(state["company_of_interest"])
        self.ticker = state["company_of_interest"]
        set_config({**self.config, "analysis_as_of": analysis_date or trade_date})
        for memory in (self.bull_memory, self.bear_memory, self.trader_memory, self.invest_judge_memory, self.portfolio_manager_memory):
            memory.as_of = analysis_date or trade_date
        args = self.propagator.get_graph_args(callbacks=callbacks)
        if self._checkpoint_connection is not None:
            identity = {
                "version": 1, "ticker": self.ticker, "trade_date": trade_date,
                "analysis_date": analysis_date or trade_date, "analysts": self.selected_analysts,
                "config": {key: value for key, value in self.config.items() if key not in {"api_keys_path", "results_dir", "project_dir", "data_cache_dir", "checkpoint_dir", "memory_dir"}},
            }
            thread_id = hashlib.sha256(json.dumps(identity, sort_keys=True, default=str).encode()).hexdigest()
            args["config"]["configurable"] = {"thread_id": thread_id}
            previous = self.graph.get_state(args["config"])
            if previous.values:
                state = None
        return state, args

    def close(self):
        for llm in (self.deep_thinking_llm, self.quick_thinking_llm, self.output_thinking_llm):
            close = getattr(llm, "close", None)
            if callable(close):
                close()
        if self._checkpoint_connection is not None:
            self._checkpoint_connection.close()
            self._checkpoint_connection = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def save_reports(self, final_state=None, *, save_path=None):
        from tradingagents.reporting import save_report_bundle
        state = final_state or self.curr_state
        if not state:
            raise ValueError("Run an analysis before saving reports")
        ticker = state["company_of_interest"]
        from tradingagents.dataflows.integrity import safe_symbol
        ticker = safe_symbol(ticker)
        path = save_path or Path(self.config["results_dir"]) / ticker / state["trade_date"] / "reports"
        return save_report_bundle(state, ticker, path, language=self.config.get("output_language", "English"))

    def _get_provider_kwargs(self, role: str) -> Dict[str, Any]:
        """Get provider-specific kwargs for LLM client creation."""
        kwargs = {}
        provider = self.config.get("llm_provider", "").lower()
        if provider != "codex":
            kwargs["max_retries"] = int(self.config.get("llm_max_retries", 2))
            if self.config.get("max_tokens") is not None:
                kwargs["max_tokens"] = int(self.config["max_tokens"])

        if provider == "google":
            thinking_level = self.config.get("google_thinking_level")
            if thinking_level:
                kwargs["thinking_level"] = thinking_level

        elif provider == "openai":
            reasoning_effort = self.config.get("openai_reasoning_effort")
            if reasoning_effort:
                kwargs["reasoning_effort"] = reasoning_effort

        elif provider == "anthropic":
            effort = self.config.get("anthropic_effort")
            if effort:
                kwargs["effort"] = effort
        elif provider == "codex":
            kwargs.update(codex_client_kwargs(self.config, role=role))

        return kwargs

    def _create_tool_nodes(self) -> Dict[str, ToolNode]:
        """Create tool nodes for different data sources using abstract methods."""
        return {
            "market": ToolNode(
                [
                    # Core stock data tools
                    get_stock_data,
                    # Technical indicators
                    get_indicators,
                ]
            ),
            "social": ToolNode(
                [
                    # Dedicated or news-derived sentiment tools
                    get_social_sentiment,
                    get_company_news,
                ]
            ),
            "news": ToolNode(
                [
                    get_macro_data,
                    # News, macro, and disclosure information
                    get_company_news,
                    get_macro_news,
                    get_disclosures,
                    get_insider_transactions,
                ]
            ),
            "fundamentals": ToolNode(
                [
                    # Fundamental analysis tools
                    get_fundamentals,
                    get_balance_sheet,
                    get_cashflow,
                    get_income_statement,
                    get_insider_transactions,
                ]
            ),
        }

    def propagate(self, company_name, trade_date, analysis_date=None):
        """Run the trading agents graph for a company on a specific date."""

        # Initialize state
        init_agent_state, args = self.prepare_run(
            company_name, trade_date, analysis_date=analysis_date
        )

        if self.debug:
            # Debug mode with tracing
            trace = []
            for chunk in self.graph.stream(init_agent_state, **args):
                if len(chunk["messages"]) == 0:
                    pass
                else:
                    chunk["messages"][-1].pretty_print()
                    trace.append(chunk)

            final_state = trace[-1] if trace else self.graph.get_state(args["config"]).values
        else:
            # Standard mode without tracing
            final_state = self.graph.invoke(init_agent_state, **args)

        signal = self.process_signal(final_state["final_trade_decision"])
        final_state = self._localize_final_state(final_state)

        # Store current state for reflection
        self.curr_state = final_state

        # Log state
        self._log_state(trade_date, final_state)

        # Return decision and processed signal
        return final_state, signal

    def _log_state(self, trade_date, final_state):
        """Log the final state to a JSON file."""
        self.log_states_dict[str(trade_date)] = {
            "input_instrument": final_state.get("input_instrument", final_state["company_of_interest"]),
            "company_of_interest": final_state["company_of_interest"],
            "instrument_profile": final_state.get("instrument_profile", {}),
            "trade_date": final_state["trade_date"],
            "analysis_date": final_state.get("analysis_date", final_state["trade_date"]),
            "market_report": final_state["market_report"],
            "sentiment_report": final_state["sentiment_report"],
            "news_report": final_state["news_report"],
            "fundamentals_report": final_state["fundamentals_report"],
            "investment_debate_state": {
                "bull_history": final_state["investment_debate_state"]["bull_history"],
                "bear_history": final_state["investment_debate_state"]["bear_history"],
                "history": final_state["investment_debate_state"]["history"],
                "current_response": final_state["investment_debate_state"][
                    "current_response"
                ],
                "judge_decision": final_state["investment_debate_state"][
                    "judge_decision"
                ],
            },
            "trader_investment_decision": final_state["trader_investment_plan"],
            "risk_debate_state": {
                "aggressive_history": final_state["risk_debate_state"]["aggressive_history"],
                "conservative_history": final_state["risk_debate_state"]["conservative_history"],
                "neutral_history": final_state["risk_debate_state"]["neutral_history"],
                "history": final_state["risk_debate_state"]["history"],
                "judge_decision": final_state["risk_debate_state"]["judge_decision"],
            },
            "investment_plan": final_state["investment_plan"],
            "final_trade_decision": final_state["final_trade_decision"],
        }

        # Save to file
        directory = Path(self.config["results_dir"]) / self.ticker / "TradingAgentsStrategy_logs"
        directory.mkdir(parents=True, exist_ok=True)

        log_path = directory / f"full_states_log_{trade_date}.json"
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(self.log_states_dict[str(trade_date)], f, indent=4)

    def reflect_and_remember(self, returns_losses, *, state=None, outcome_known_at=None):
        """Reflect on decisions and update memory based on returns."""
        current = dict(state or self.curr_state or {})
        if not current:
            raise ValueError("No completed decision to reflect on")
        if outcome_known_at:
            if date.fromisoformat(outcome_known_at) <= date.fromisoformat(current["trade_date"]):
                raise ValueError("Outcome must become known after the decision date")
            current["outcome_known_at"] = outcome_known_at
        self.reflector.reflect_bull_researcher(
            current, returns_losses, self.bull_memory
        )
        self.reflector.reflect_bear_researcher(
            current, returns_losses, self.bear_memory
        )
        self.reflector.reflect_trader(
            current, returns_losses, self.trader_memory
        )
        self.reflector.reflect_invest_judge(
            current, returns_losses, self.invest_judge_memory
        )
        self.reflector.reflect_portfolio_manager(
            current, returns_losses, self.portfolio_manager_memory
        )

    def process_signal(self, full_signal):
        """Process a signal to extract the core decision."""
        return self.signal_processor.process_signal(full_signal)

    def _localize_final_state(self, final_state: Dict[str, Any]) -> Dict[str, Any]:
        """Rewrite only the persisted report-facing outputs into the configured output language."""
        language = get_output_language()
        if language.lower() == "english":
            return final_state

        localized = dict(final_state)

        def maybe_localize(content: str, *, content_type: str, force_llm_backend: bool = False) -> str:
            if force_llm_backend:
                localization_llm = getattr(self, "quick_thinking_llm", None) or getattr(
                    self, "output_thinking_llm", None
                )
            else:
                localization_llm = getattr(self, "output_thinking_llm", None) or getattr(
                    self, "quick_thinking_llm", None
                )
            if localization_llm is None:
                return content

            def localize_text(text: str, *, text_content_type: str) -> str:
                localized_text: str
                try:
                    localized_text = rewrite_in_output_language(
                        localization_llm,
                        text,
                        content_type=text_content_type,
                        force_llm_backend=force_llm_backend,
                    )
                except TypeError as exc:
                    if "force_llm_backend" not in str(exc):
                        raise
                    localized_text = rewrite_in_output_language(
                        localization_llm,
                        text,
                        content_type=text_content_type,
                    )
                if _contains_unexpected_script_noise(localized_text, language):
                    return text
                return localized_text

            try:
                structured = parse_structured_decision(content)
            except StructuredDecisionValidationError:
                return localize_text(content, text_content_type=content_type)

            payload = structured.to_dict()
            for field_name in ("entry_logic", "exit_logic", "position_sizing", "risk_limits"):
                payload[field_name] = localize_text(
                    str(payload.get(field_name) or ""),
                    text_content_type=f"{content_type} {field_name.replace('_', ' ')}",
                )
            for field_name in ("catalysts", "invalidators", "watchlist_triggers"):
                payload[field_name] = [
                    localize_text(
                        str(item),
                        text_content_type=f"{content_type} {field_name.replace('_', ' ')} item",
                    )
                    for item in (payload.get(field_name) or [])
                    if str(item).strip()
                ]
            return json.dumps(payload, indent=2, ensure_ascii=False)

        for field_name, content_type in (
            ("market_report", "market analyst report"),
            ("sentiment_report", "social sentiment report"),
            ("news_report", "news analyst report"),
            ("fundamentals_report", "fundamentals analyst report"),
            ("trader_investment_plan", "trader plan"),
        ):
            localized[field_name] = maybe_localize(
                localized.get(field_name, ""),
                content_type=content_type,
            )

        investment_debate = dict(localized.get("investment_debate_state") or {})
        for field_name, content_type in (
            ("bull_history", "bull researcher debate history"),
            ("bear_history", "bear researcher debate history"),
            ("judge_decision", "research manager decision"),
        ):
            investment_debate[field_name] = maybe_localize(
                investment_debate.get(field_name, ""),
                content_type=content_type,
            )
        localized["investment_debate_state"] = investment_debate

        risk_debate = dict(localized.get("risk_debate_state") or {})
        for field_name, content_type in (
            ("aggressive_history", "aggressive risk analyst debate history"),
            ("conservative_history", "conservative risk analyst debate history"),
            ("neutral_history", "neutral risk analyst debate history"),
            ("judge_decision", "portfolio manager decision"),
        ):
            risk_debate[field_name] = maybe_localize(
                risk_debate.get(field_name, ""),
                content_type=content_type,
                force_llm_backend=(field_name == "judge_decision"),
            )
        localized["risk_debate_state"] = risk_debate

        return localized


def _contains_unexpected_script_noise(text: str, language: str) -> bool:
    if not text:
        return False
    normalized_language = str(language or "").strip().lower()
    if normalized_language != "korean":
        return False
    return bool(re.search(r"[\u0590-\u05FF\u0600-\u06FF\u0750-\u077F\u0400-\u04FF]", text))
