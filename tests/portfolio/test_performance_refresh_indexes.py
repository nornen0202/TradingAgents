import sqlite3

from tradingagents.performance.action_outcomes import initialize_action_tracker
from tradingagents.performance.price_history import _recommendations_due_for_refresh
from tradingagents.performance import action_outcomes


def test_eligibility_uses_covering_indexes_and_preserves_existing_records(tmp_path, monkeypatch):
    db = tmp_path / 'performance.sqlite'
    initialize_action_tracker(db)
    with sqlite3.connect(db) as conn:
        conn.executemany(
            'INSERT INTO action_recommendations (run_id,ticker,market,action,created_at,profit_plan_json) '
            'VALUES (?,?,?,?,?,?)',
            [('run', ticker, market, 'WATCH', '2026-10-20', 'x' * 4096)
             for ticker, market in [('MSFT', 'US'), ('AAPL', 'US'), ('005930.KS', 'KR')]],
        )
        conn.execute('INSERT INTO action_outcomes (recommendation_id,calculation_version,return_60d,updated_at) '
                     'VALUES (1,3,NULL,?)', ('2026-10-28',))
        before = [conn.execute('SELECT * FROM ' + table).fetchall()
                  for table in ('action_recommendations', 'action_outcomes')]
    initialize_action_tracker(db)
    queries = []
    original_connect = sqlite3.connect

    def traced(*args, **kwargs):
        connection = original_connect(*args, **kwargs)
        connection.set_trace_callback(queries.append)
        return connection

    monkeypatch.setattr(sqlite3, 'connect', traced)
    tickers, ids, warnings = _recommendations_due_for_refresh(db, market='US', asof_date='2026-10-29')
    assert tickers == ['AAPL', 'MSFT'] and ids == (2, 1)
    assert warnings == ['performance_price_history_market_filter:US:skipped=1']
    eligibility = next(query for query in queries if 'SELECT r.id' in query)
    with original_connect(db) as conn:
        plan = ' '.join(row[3] for row in conn.execute('EXPLAIN QUERY PLAN ' + eligibility))
        assert 'COVERING INDEX idx_action_refresh_recommendations' in plan
        assert 'COVERING INDEX idx_action_refresh_outcomes' in plan
        assert before == [conn.execute('SELECT * FROM ' + table).fetchall()
                          for table in ('action_recommendations', 'action_outcomes')]


def test_summary_joins_are_covering_and_preserve_null_and_duplicate_outcomes(tmp_path):
    db = tmp_path / 'summary.sqlite'
    initialize_action_tracker(db)
    with sqlite3.connect(db) as conn:
        conn.executemany(
            'INSERT INTO action_recommendations '
            '(run_id,ticker,market,action,source,source_cohort,prism_agreement,'
            'sell_intent,risk_action,lift_status,created_at,profit_plan_json) '
            'VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
            [('run', ticker, market, action, source, cohort, prism, sell, risk, lift,
              '2026-10-20', 'x' * 4096)
             for ticker, market, action, source, cohort, prism, sell, risk, lift in [
                 ('MSFT', 'US', 'BUY', 'TradingAgents', 'main', 'conflict_sell', None, None, 'BUDGET_BLOCKED'),
                 ('AAPL', 'US', 'TAKE_PROFIT', 'TradingAgents', 'main', None, 'TAKE_PROFIT', None, 'READY'),
                 ('NVDA', None, 'WATCH', 'scanner', None, None, None, None, None),
                 ('005930.KS', 'KR', 'HOLD', 'PRISM', 'advisory', 'agree', None, None, None),
             ]],
        )
        conn.executemany(
            'INSERT INTO action_outcomes (recommendation_id,return_5d,return_20d,'
            'benchmark_excess_20d,avoided_drawdown_20d,missed_upside_20d,return_60d) VALUES (?,?,?,?,?,?,?)',
            [(1, 2.0, 4.0, 1.0, 0.0, 3.0, None), (1, 4.0, None, None, None, None, None),
             (2, -2.0, -4.0, -1.0, 2.0, 0.0, 8.0), (4, None, None, None, None, None, None)],
        )
        conn.execute('DROP INDEX idx_action_summary_recommendations')
        conn.execute('DROP INDEX idx_action_summary_outcomes')
    queries = []

    def summaries():
        with sqlite3.connect(db) as conn:
            conn.row_factory = sqlite3.Row
            conn.set_trace_callback(queries.append)
            return [action_outcomes._aggregate(conn, field) for field in ('action', 'prism_agreement', 'source_cohort')] + [
                action_outcomes._aggregate_action_buckets(conn),
                action_outcomes._aggregate_profit_taking(conn),
                action_outcomes._aggregate_calibration(conn),
                action_outcomes._performance_data_quality(conn, closed_trades=0, known_events={}, active_reviews=[]),
            ]

    before = summaries()
    initialize_action_tracker(db)
    queries.clear()
    assert summaries() == before
    with sqlite3.connect(db) as conn:
        joins = [query for query in queries if 'LEFT JOIN action_outcomes' in query]
        assert len(joins) == 7
        for query in joins:
            plan = ' '.join(row[3] for row in conn.execute('EXPLAIN QUERY PLAN ' + query))
            assert 'COVERING INDEX idx_action_summary_recommendations' in plan
            assert 'COVERING INDEX idx_action_summary_outcomes' in plan
