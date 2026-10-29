import sqlite3

from tradingagents.performance.action_outcomes import initialize_action_tracker
from tradingagents.performance.price_history import _recommendations_due_for_refresh


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
