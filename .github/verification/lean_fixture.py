"""The KIS-converted fixture has integer won and explicit open/close events."""
import json
import os
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from NodaTime import DateTimeZoneProviders
from AlgorithmImports import (PythonData, QCAlgorithm, Resolution, SubscriptionDataSource,
    SubscriptionTransportMedium, FileFormat, FeeModel, OrderFee, CashAmount, ConstantSlippageModel,
    ImmediateFillModel, OrderStatus)

D = Decimal

class NativePrice(PythonData):
    def get_source(self, config, date, is_live):
        return SubscriptionDataSource("/Fixture/events.csv", SubscriptionTransportMedium.LOCAL_FILE, FileFormat.CSV)

    def reader(self, config, line, date, is_live):
        at, price = line.split(",")
        row = NativePrice()
        row.symbol = config.symbol
        row.time = row.end_time = datetime.strptime(at, "%Y%m%d%H%M")
        row.value = float(price)
        return row

class CommissionAndLevy(FeeModel):
    def get_order_fee(self, security, order):
        mark = D(str(security.price))
        execution = mark * (D("1.001") if order.quantity > 0 else D(".999"))
        fee = execution * D(str(abs(order.quantity))) * (D(".001") if order.quantity > 0 else D(".003"))
        return OrderFee(CashAmount(float(fee), "KRW"))

class Algorithm(QCAlgorithm):
    def initialize(self):
        self.set_start_date(2026, 6, 8)
        self.set_end_date(2026, 6, 19)
        self.set_time_zone("Asia/Seoul")
        self.set_account_currency("KRW", 3000000)
        self.scenario = os.environ["SCENARIO"]
        self.costs = self.scenario != "gross_fixture"
        self.tax = self.scenario == "transaction_costs_and_tax_reserve"
        security = self.add_data(NativePrice, "FIXTURE", Resolution.MINUTE, DateTimeZoneProviders.Tzdb["Asia/Seoul"], False)
        self.fixture = security.symbol
        self.set_benchmark(lambda _: 1.)
        security.set_fill_model(ImmediateFillModel())
        if self.costs:
            security.set_slippage_model(ConstantSlippageModel(.001))
            security.set_fee_model(CommissionAndLevy())
        else:
            security.set_slippage_model(ConstantSlippageModel(0))
            security.set_fee_model(FeeModel())
        self.fills = []
        self.dividend = D(0)

    def on_data(self, data):
        row = data.get(self.fixture)
        if row is None:
            return
        at = row.end_time
        if (at.month, at.day, at.hour) == (6, 9, 9):
            cost = D(str(row.value)) * (D("1.002001") if self.costs else D(1))
            self.market_order(self.fixture, int(D(3000000) // cost), tag="fixture buy at official opening input")
        elif (at.month, at.day, at.hour) == (6, 11, 15):
            self.dividend = D(str(self.portfolio[self.fixture].quantity)) * 500
            if self.costs:
                self.dividend *= D(".9")
        elif (at.month, at.day, at.hour) == (6, 19, 15):
            self.market_order(self.fixture, -self.portfolio[self.fixture].quantity, tag="fixture terminal close")

    def on_order_event(self, event):
        if event.status == OrderStatus.FILLED:
            self.fills.append(dict(q=float(event.fill_quantity), px=float(event.fill_price),
                                   fee=float(event.order_fee.value.amount), time=str(event.utc_time)))

    def on_end_of_algorithm(self):
        reserve = D(0)
        if len(self.fills) == 2 and self.tax:
            a, b = self.fills
            reservation = D(str(-b["q"])) * D(str(b["px"])) - D(str(b["fee"]))
            basis = D(str(a["q"])) * D(str(a["px"])) + D(str(a["fee"]))
            reserve = max(D(0), reservation - basis - 75000) * D(".15")
        cash = D(str(self.portfolio.cash))
        Path("/Results/reconciliation.json").write_text(json.dumps(dict(
            fills=self.fills, final_engine_cash=float(cash), dividend_receivable_krw=float(self.dividend),
            tax_reserve_krw=float(reserve), final_krw=float(cash + self.dividend - reserve))))
