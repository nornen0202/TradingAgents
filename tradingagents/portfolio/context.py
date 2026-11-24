"""A standing analysis portfolio for the graph and independent backtest cells."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from tradingagents.dataflows.integrity import safe_symbol


class Position(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, extra="forbid")

    ticker: str
    quantity: float
    average_price: float | None = Field(default=None, ge=0)

    @field_validator("ticker")
    @classmethod
    def check_ticker(cls, value):
        return safe_symbol(value)


class PortfolioContext(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, extra="forbid")

    cash: float | None = None
    currency: str | None = Field(default=None, pattern=r"^[A-Z]{3}$")
    positions: list[Position] = Field(default_factory=list)

    def render(self, ticker):
        lines = [f"{row.ticker}: {row.quantity:g} units" +
                 (f", average {row.average_price:g}" if row.average_price is not None else "")
                 for row in self.positions]
        if self.cash is not None:
            lines.append(f"Available cash: {self.cash:g} {self.currency or '(currency unspecified)'}")
        if all(row.ticker != ticker for row in self.positions):
            lines.append(f"No position supplied for {ticker}.")
        return "User-supplied standing portfolio:\n" + "\n".join(lines)


def normalize_portfolio(portfolio):
    if portfolio is None:
        return None
    if hasattr(portfolio, "model_dump"):
        portfolio = portfolio.model_dump(mode="json")
    return PortfolioContext.model_validate(portfolio).model_dump(mode="json")


def render_portfolio(state):
    portfolio = state.get("standing_portfolio")
    if portfolio is None:
        return ""
    return PortfolioContext.model_validate(portfolio).render(state["company_of_interest"])
