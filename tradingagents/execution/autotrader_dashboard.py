"""Export PRISM-compatible live trading dashboard JSON and interactive HTML."""
from __future__ import annotations

from datetime import datetime
import html
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import atomic_write_bytes, atomic_write_json
from .prism_autotrader import (
    AutotraderPolicy,
    compute_performance_metrics,
    evaluate_live_promotion_gate,
    initialize_autotrader_db,
)


def build_market_dashboard_payload(db_path: Path, market: str, policy: AutotraderPolicy) -> dict[str, Any]:
    initialize_autotrader_db(db_path, policy)
    metrics = compute_performance_metrics(db_path, market, policy.mode)
    promotion = evaluate_live_promotion_gate(db_path, market, min_vts_trades=policy.min_vts_trades_for_live)
    return {
        "schema": "tradingagents.autotrader-dashboard/v1",
        "updated_at": datetime.now(ZoneInfo("Asia/Seoul")).isoformat(),
        "market": market.upper(),
        "mode": policy.mode,
        "account_summary": {
            "currency": metrics["currency"],
            "initial_capital": metrics["initial_capital"],
            "total_assets": metrics["nav"],
            "cash": metrics["cash"],
            "cash_ratio_pct": metrics["cash_ratio_pct"],
            "positions_value": metrics["positions_value"],
            "season_return_pct": metrics["season_return_pct"],
            "slot_realized_return_pct": metrics["slot_realized_return_pct"],
            "max_drawdown_pct": metrics["max_drawdown_pct"],
            "open_slots": metrics["open_slots"],
            "max_slots": policy.max_slots,
        },
        "performance": {
            "closed_trades": metrics["closed_trades"],
            "win_count": metrics["win_count"],
            "loss_count": metrics["loss_count"],
            "win_rate_pct": metrics["win_rate_pct"],
            "avg_win_pct": metrics["avg_win_pct"],
            "avg_loss_pct": metrics["avg_loss_pct"],
            "payoff_ratio": metrics["payoff_ratio"],
        },
        "promotion_gate": promotion,
        "holdings": metrics["positions"],
        "pending_entries": metrics["pending_entries"],
        "trading_history": metrics["recent_trades"],
        "equity_curve": metrics["equity_curve"],
    }


def render_autotrader_dashboard_html(kr: dict[str, Any], us: dict[str, Any]) -> str:
    def _fmt_money(val: float, market: str) -> str:
        return f"{val:,.0f}원" if market == "KR" else f"${val:,.2f}"

    def _market_card(data: dict[str, Any], title: str) -> str:
        m = data["market"]
        acct = data["account_summary"]
        perf = data["performance"]
        promo = data["promotion_gate"]
        ret_cls = "pos" if acct["season_return_pct"] >= 0 else "neg"
        rows = []
        for h in data["holdings"]:
            ret = (float(h["current_price"]) - float(h["buy_price"])) / max(float(h["buy_price"]), 1e-9) * 100.0
            cls = "pos" if ret >= 0 else "neg"
            rows.append(
                f"<tr><td><strong>{html.escape(str(h.get('display_name') or h['ticker']))}</strong> "
                f"<span class='muted'>({html.escape(str(h['ticker']))})</span></td>"
                f"<td>{int(h['quantity'])}</td>"
                f"<td>{_fmt_money(float(h['buy_price']), m)}</td>"
                f"<td>{_fmt_money(float(h['current_price']), m)}</td>"
                f"<td class='{cls}'>{ret:+.2f}%</td>"
                f"<td>{_fmt_money(float(h['target_price']), m)}</td>"
                f"<td>{_fmt_money(float(h['stop_loss']), m)}</td>"
                f"<td>{'🚀 주도주' if int(h.get('runner_active') or 0) else '일반'}</td></tr>"
            )
        holdings_html = "".join(rows) or "<tr><td colspan='8' class='muted'>현재 보유 슬롯 없음 (대기 큐 감시 중)</td></tr>"

        queued_rows = []
        for q in data["pending_entries"][:10]:
            queued_rows.append(
                f"<tr><td>{html.escape(str(q.get('display_name') or q['ticker']))} ({html.escape(str(q['ticker']))})</td>"
                f"<td>{float(q['buy_score']):.1f}</td>"
                f"<td>{_fmt_money(float(q['reference_price']), m)}</td>"
                f"<td>{_fmt_money(float(q['max_entry_price']), m)}</td>"
                f"<td>{_fmt_money(float(q['stop_loss']), m)}</td>"
                f"<td>{_fmt_money(float(q['target_price']), m)}</td></tr>"
            )
        queued_html = "".join(queued_rows) or "<tr><td colspan='6' class='muted'>예약 대기 주문 없음</td></tr>"

        hist_rows = []
        for t in data["trading_history"][:15]:
            cls = "pos" if float(t["return_pct"]) >= 0 else "neg"
            hist_rows.append(
                f"<tr><td>{html.escape(str(t.get('display_name') or t['ticker']))} ({html.escape(str(t['ticker']))})</td>"
                f"<td>{_fmt_money(float(t['buy_price']), m)}</td>"
                f"<td>{_fmt_money(float(t['sell_price']), m)}</td>"
                f"<td class='{cls}'>{float(t['return_pct']):+.2f}%</td>"
                f"<td>{int(t['holding_days'])}일</td>"
                f"<td>{html.escape(str(t['exit_reason']))}</td></tr>"
            )
        hist_html = "".join(hist_rows) or "<tr><td colspan='6' class='muted'>청산 완료 거래 대기 중</td></tr>"

        promo_text = "✅ 실전 승격 가능" if promo["eligible"] else f"🧪 검증 중 ({promo['closed_burn_in_trades']}/{promo['required_trades']}건)"
        return f"""
        <section class="market-panel">
          <h2>{html.escape(title)} <span class="badge">{html.escape(data['mode'].upper())}</span> <span class="badge">{html.escape(promo_text)}</span></h2>
          <div class="kpi-grid">
            <div class="kpi"><div class="label">총 평가자산</div><div class="val">{_fmt_money(acct['total_assets'], m)}</div></div>
            <div class="kpi"><div class="label">시즌 수익률</div><div class="val {ret_cls}">{acct['season_return_pct']:+.2f}%</div></div>
            <div class="kpi"><div class="label">10슬롯 실현수익률</div><div class="val">{acct['slot_realized_return_pct']:+.2f}%</div></div>
            <div class="kpi"><div class="label">최대 낙폭 (MDD)</div><div class="val neg">{acct['max_drawdown_pct']:.2f}%</div></div>
            <div class="kpi"><div class="label">승률 ({perf['closed_trades']}건)</div><div class="val">{perf['win_rate_pct']:.1f}%</div></div>
            <div class="kpi"><div class="label">평균수익 / 평균손실 / 손익비</div><div class="val">{perf['avg_win_pct']:+.1f}% / {perf['avg_loss_pct']:+.1f}% / {perf['payoff_ratio']:.2f}</div></div>
            <div class="kpi"><div class="label">슬롯 가동 / 현금비중</div><div class="val">{acct['open_slots']}/{acct['max_slots']} · {acct['cash_ratio_pct']:.1f}%</div></div>
          </div>
          <h3>보유 포지션 (10슬롯 관리)</h3>
          <table><thead><tr><th>종목</th><th>수량</th><th>매수가</th><th>현재가</th><th>수익률</th><th>목표가</th><th>손절가</th><th>상태</th></tr></thead>
          <tbody>{holdings_html}</tbody></table>
          <h3>차기 정규장 대기 큐 (장외 분석 시그널 자동 이관)</h3>
          <table><thead><tr><th>종목</th><th>점수</th><th>기준가</th><th>상한 지정가(+3%)</th><th>손절가</th><th>목표가</th></tr></thead>
          <tbody>{queued_html}</tbody></table>
          <h3>최근 청산 거래 내역</h3>
          <table><thead><tr><th>종목</th><th>매수가</th><th>매도가</th><th>수익률</th><th>보유일</th><th>매도 사유</th></tr></thead>
          <tbody>{hist_html}</tbody></table>
        </section>
        """

    updated = html.escape(kr["updated_at"][:19].replace("T", " "))
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TradingAgents 자동매매 실시간 대시보드</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Pretendard', 'Segoe UI', sans-serif; background:#0b1020; color:#e6edf3; margin:0; padding:24px; }}
  header {{ max-width:1280px; margin:0 auto 24px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; }}
  h1 {{ margin:0; font-size:1.6rem; }}
  .market-panel {{ max-width:1280px; margin:0 auto 28px; background:#131a2e; border:1px solid #26314f; border-radius:14px; padding:20px; }}
  .kpi-grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(170px, 1fr)); gap:12px; margin:14px 0 20px; }}
  .kpi {{ background:#0f1526; border:1px solid #222d49; border-radius:10px; padding:12px; }}
  .kpi .label {{ font-size:0.78rem; color:#8b9bb4; margin-bottom:6px; }}
  .kpi .val {{ font-size:1.15rem; font-weight:700; }}
  .pos {{ color:#3fb950; }} .neg {{ color:#f85149; }} .muted {{ color:#8b9bb4; }}
  .badge {{ font-size:0.78rem; background:#1f2a48; border:1px solid #384c7c; padding:3px 9px; border-radius:999px; margin-left:6px; vertical-align:middle; }}
  table {{ width:100%; border-collapse:collapse; margin-bottom:18px; font-size:0.88rem; }}
  th, td {{ text-align:left; padding:9px 10px; border-bottom:1px solid #1e2842; }}
  th {{ color:#9fb0cc; font-weight:600; background:#0f1526; }}
</style>
</head>
<body>
<header>
  <div>
    <h1>📊 TradingAgents 모의·자동매매 실시간 대시보드</h1>
    <div class="muted">PRISM 10슬롯 추세추종 · 무LLM 장중 하드스탑/주도주 트레일링 · VTS→실전 승격 게이트</div>
  </div>
  <div class="muted">최종 갱신: {updated} KST</div>
</header>
{_market_card(kr, "🇰🇷 한국 주식 자동매매 (KRX)")}
{_market_card(us, "🇺🇸 미국 주식 자동매매 (NYSE/NASDAQ)")}
</body>
</html>
"""


def publish_autotrader_dashboard(
    archive_dir: Path,
    *,
    site_dir: Path | None = None,
    policy: AutotraderPolicy | None = None,
) -> dict[str, Path]:
    archive_dir = Path(archive_dir)
    policy = policy or AutotraderPolicy()
    db_path = archive_dir / "paper" / "autotrader.sqlite"
    kr = build_market_dashboard_payload(db_path, "KR", policy)
    us = build_market_dashboard_payload(db_path, "US", policy)
    html_doc = render_autotrader_dashboard_html(kr, us)

    out_dir = archive_dir / "paper" / "dashboard"
    out_dir.mkdir(parents=True, exist_ok=True)
    kr_json = out_dir / "dashboard_data.json"
    us_json = out_dir / "us_dashboard_data.json"
    index_html = out_dir / "index.html"
    atomic_write_json(kr_json, kr)
    atomic_write_json(us_json, us)
    atomic_write_bytes(index_html, html_doc.encode("utf-8"))

    paths = {"kr_json": kr_json, "us_json": us_json, "html": index_html}
    if site_dir is not None:
        from .public_autotrader_dashboard import build_public_autotrader_dashboard

        paths["site_html"] = build_public_autotrader_dashboard(archive_dir, site_dir, mode=policy.mode)
    return paths
