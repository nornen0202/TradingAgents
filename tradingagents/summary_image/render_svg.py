from __future__ import annotations

import html
from pathlib import Path
from typing import Any


WIDTH = 1120
HEIGHT = 1400


def render_summary_svg(spec: dict[str, Any]) -> str:
    title = _escape(spec.get("title") or "TradingAgents 리포트 요약")
    run = spec.get("run") or {}
    badges = spec.get("badges") or {}
    account = spec.get("account") or {}
    counts = spec.get("counts") or {}
    summary = spec.get("summary_text") or {}
    guide = spec.get("position_guide") or {}
    footer = _escape(spec.get("footer") or "")
    parts = [
        _svg_header(),
        f"<text x='150' y='72' class='title'>{title}</text>",
        f"<text x='154' y='112' class='sub'>Run: {_escape(run.get('run_id'))} · {_escape(run.get('date'))}</text>",
        _badge(32, 145, f"{run.get('successful_tickers', 0)}개 성공 / {run.get('failed_tickers', 0)}개 실패", "good"),
        _badge(325, 145, str(badges.get("market_regime") or "시장 확인"), "info"),
        _badge(708, 145, f"상태: {badges.get('status') or '-'}", "warn" if run.get("status") != "success" else "good"),
        _section_header(36, 232, "1", "투자자 한줄 요약"),
        _summary_box(summary),
        _section_header(548, 232, "2", "계좌 현황"),
        _account_cards(account),
        _section_header(36, 568, "3", "핵심 요약"),
        _count_cards(counts),
        _priority_bar(spec.get("top_priority") or []),
        _section_header(36, 904, "4", "다음 체크포인트"),
        _checkpoint_cards(spec.get("next_checkpoints") or []),
        _section_header(36, 1124, "5", "대표 포지션 가이드"),
        _position_guide(guide),
        _section_header(622, 1124, "6", "주요 리스크"),
        _risk_box(spec.get("risks") or []),
        f"<rect x='18' y='1350' width='1084' height='36' rx='8' class='footerBox'/>",
        f"<text x='52' y='1375' class='footer'>{footer}</text>",
        "</svg>",
    ]
    return "\n".join(parts)


def write_summary_svg(spec: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_summary_svg(spec), encoding="utf-8")
    return path


def _svg_header() -> str:
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='{WIDTH}' height='{HEIGHT}' viewBox='0 0 {WIDTH} {HEIGHT}' role='img' aria-label='TradingAgents summary image'>
<defs>
  <style>
    .bg {{ fill: #f7fbff; }}
    .panel {{ fill: #ffffff; stroke: #bfd0e6; stroke-width: 1.4; }}
    .soft {{ fill: #f3f8ff; stroke: #bfd0e6; stroke-width: 1.2; }}
    .good {{ fill: #f0fff3; stroke: #22813a; }}
    .info {{ fill: #eefcff; stroke: #16818c; }}
    .warn {{ fill: #fff7e6; stroke: #d97706; }}
    .risk {{ fill: #fff4ee; stroke: #d6532f; }}
    .title {{ font: 700 45px 'Malgun Gothic', 'Apple SD Gothic Neo', Arial, sans-serif; fill: #071b44; }}
    .sub {{ font: 20px 'Malgun Gothic', Arial, sans-serif; fill: #23456f; }}
    .h {{ font: 700 25px 'Malgun Gothic', Arial, sans-serif; fill: #071b44; }}
    .body {{ font: 18px 'Malgun Gothic', Arial, sans-serif; fill: #0d1b2f; }}
    .small {{ font: 15px 'Malgun Gothic', Arial, sans-serif; fill: #24364f; }}
    .metric {{ font: 700 43px 'Malgun Gothic', Arial, sans-serif; fill: #073b7a; }}
    .green {{ fill: #116a2a; }}
    .orange {{ fill: #b94b16; }}
    .teal {{ fill: #087579; }}
    .sectionNum {{ font: 700 23px Arial, sans-serif; fill: white; }}
    .footer {{ font: 16px 'Malgun Gothic', Arial, sans-serif; fill: #20344f; }}
    .footerBox {{ fill: #f8fafc; stroke: #cad7e8; }}
  </style>
</defs>
<rect width='1120' height='1400' rx='10' class='bg'/>
<rect x='26' y='36' width='86' height='86' rx='14' fill='#08224d'/>
<path d='M48 96 L74 75 L93 83 L104 55' stroke='#74e2d0' stroke-width='7' fill='none' stroke-linecap='round' stroke-linejoin='round'/>
<path d='M95 55 L107 55 L107 68' stroke='#bdf7ef' stroke-width='6' fill='none' stroke-linecap='round'/>
<rect x='49' y='100' width='11' height='18' fill='white'/>
<rect x='70' y='91' width='11' height='27' fill='white'/>
<rect x='91' y='82' width='11' height='36' fill='white'/>
<path d='M960 210 C990 170 1010 190 1035 140 C1052 105 1070 85 1100 55' stroke='#b9cce7' stroke-width='4' fill='none' opacity='.65'/>
<g opacity='.25'>
  <rect x='970' y='86' width='10' height='74' fill='#9db8d8'/><rect x='995' y='112' width='10' height='48' fill='#9db8d8'/><rect x='1020' y='72' width='10' height='88' fill='#9db8d8'/><rect x='1045' y='58' width='10' height='102' fill='#9db8d8'/><rect x='1070' y='38' width='10' height='122' fill='#9db8d8'/>
</g>"""


def _badge(x: int, y: int, text: str, cls: str) -> str:
    return (
        f"<rect x='{x}' y='{y}' width='270' height='54' rx='9' class='{cls}'/>"
        f"<text x='{x + 22}' y='{y + 35}' class='h'>{_escape(text)}</text>"
    )


def _section_header(x: int, y: int, number: str, title: str) -> str:
    return (
        f"<rect x='{x}' y='{y}' width='31' height='31' rx='6' fill='#08224d'/>"
        f"<text x='{x + 9}' y='{y + 23}' class='sectionNum'>{_escape(number)}</text>"
        f"<text x='{x + 52}' y='{y + 24}' class='h'>{_escape(title)}</text>"
    )


def _summary_box(summary: dict[str, Any]) -> str:
    lines = [
        str(summary.get("headline") or "조건 확인 우선"),
        str(summary.get("one_sentence") or ""),
        *[str(item) for item in (summary.get("why") or [])[:3]],
    ]
    text = _text_lines(lines, 88, 318, width=390, line_height=31, css="body")
    return f"<rect x='32' y='276' width='480' height='260' rx='8' class='soft'/>{text}"


def _account_cards(account: dict[str, Any]) -> str:
    labels = [
        ("계좌 평가금액", account.get("account_value")),
        ("가용 현금", account.get("available_cash")),
        ("최소 현금 버퍼", account.get("min_cash_buffer")),
        ("운용 모드", account.get("mode")),
    ]
    parts = ["<rect x='540' y='276' width='548' height='260' rx='8' class='panel'/>"]
    for index, (label, value) in enumerate(labels):
        x = 565 + index * 128
        parts.append(f"<rect x='{x}' y='304' width='112' height='150' rx='8' class='soft'/>")
        parts.append(f"<text x='{x + 56}' y='355' text-anchor='middle' class='small'>{_escape(label)}</text>")
        parts.extend(_centered_lines(str(value or "-"), x + 56, 392, max_chars=11, css="h"))
    parts.append("<rect x='565' y='470' width='498' height='46' rx='8' class='warn'/>")
    parts.append("<text x='590' y='500' class='body'>오늘 요약은 리포트 기반 추천이며 자동 주문이 아닙니다</text>")
    return "\n".join(parts)


def _count_cards(counts: dict[str, Any]) -> str:
    items = [
        ("오늘 바로\n실행 가능", counts.get("add_now", 0), "teal"),
        ("장중 pilot\n가능", counts.get("pilot_ready", 0), ""),
        ("종가 확인 후\n실행 후보", counts.get("close_confirm", 0), ""),
        ("줄여서 살\n후보", counts.get("trim_to_fund", 0), "green"),
        ("위험 축소\n후보", counts.get("reduce_risk", 0), "orange"),
        ("손절/청산\n후보", int(counts.get("stop_loss", 0) or 0) + int(counts.get("exit", 0) or 0), "orange"),
    ]
    parts = ["<rect x='32' y='612' width='1056' height='210' rx='8' class='panel'/>"]
    for index, (label, value, color) in enumerate(items):
        x = 55 + index * 171
        parts.append(f"<rect x='{x}' y='642' width='145' height='142' rx='8' class='soft'/>")
        parts.extend(_centered_lines(label, x + 72, 688, max_chars=10, css="body"))
        css = f"metric {color}".strip()
        parts.append(f"<text x='{x + 72}' y='765' text-anchor='middle' class='{css}'>{int(value or 0)}개</text>")
    return "\n".join(parts)


def _priority_bar(items: list[dict[str, Any]]) -> str:
    labels = [str(item.get("ticker") or "") for item in items if str(item.get("ticker") or "").strip()]
    text = " > ".join(labels[:4]) if labels else "조건 확인 후 우선순위 산정"
    return (
        "<rect x='32' y='836' width='1056' height='48' rx='8' class='soft'/>"
        f"<text x='560' y='868' text-anchor='middle' class='h'>전략상 우선순위: {_escape(text)}</text>"
    )


def _checkpoint_cards(items: list[dict[str, Any]]) -> str:
    padded = list(items[:3])
    while len(padded) < 3:
        padded.append({"ticker": "-", "condition": "다음 조건 확인 대기", "action": "관찰"})
    parts: list[str] = []
    for index, item in enumerate(padded):
        x = 36 + index * 360
        parts.append(f"<rect x='{x}' y='948' width='330' height='132' rx='8' class='info'/>")
        parts.append(f"<text x='{x + 22}' y='992' class='h'>{_escape(item.get('ticker'))}</text>")
        parts.extend(_text_lines([str(item.get("condition") or "")], x + 22, 1024, width=280, line_height=24, css="small").splitlines())
        parts.append(f"<text x='{x + 22}' y='1062' class='small'>액션: {_escape(item.get('action'))}</text>")
    return "\n".join(parts)


def _position_guide(guide: dict[str, Any]) -> str:
    hold = guide.get("hold_or_add") or []
    trim = guide.get("trim_to_fund") or []
    risk = guide.get("risk_reduce") or []
    parts = ["<rect x='36' y='1168' width='550' height='156' rx='8' class='panel'/>"]
    parts.append("<text x='64' y='1205' class='body green'>보유 유지 / 조건부 추가</text>")
    parts.append("<text x='330' y='1205' class='body orange'>축소 / 리스크 관리</text>")
    parts.extend(_text_lines(_bullets(hold[:5] or ["해당 없음"]), 72, 1238, width=210, line_height=22, css="small").splitlines())
    parts.extend(_text_lines(_bullets((trim + risk)[:5] or ["해당 없음"]), 338, 1238, width=210, line_height=22, css="small").splitlines())
    return "\n".join(parts)


def _risk_box(risks: list[str]) -> str:
    lines = _bullets([str(item) for item in risks[:4]] or ["주요 리스크 없음"])
    return (
        "<rect x='622' y='1168' width='466' height='156' rx='8' class='risk'/>"
        + _text_lines(lines, 660, 1210, width=370, line_height=26, css="body")
    )


def _text_lines(lines: list[str], x: int, y: int, *, width: int, line_height: int, css: str) -> str:
    output: list[str] = []
    line_no = 0
    max_chars = max(8, width // 14)
    for line in lines:
        for chunk in _wrap(str(line), max_chars=max_chars):
            output.append(f"<text x='{x}' y='{y + line_no * line_height}' class='{css}'>{_escape(chunk)}</text>")
            line_no += 1
    return "\n".join(output)


def _centered_lines(value: str, x: int, y: int, *, max_chars: int, css: str) -> list[str]:
    lines = _wrap(value, max_chars=max_chars)[:3]
    return [f"<text x='{x}' y='{y + index * 26}' text-anchor='middle' class='{css}'>{_escape(line)}</text>" for index, line in enumerate(lines)]


def _bullets(values: list[str]) -> list[str]:
    return [f"• {value}" for value in values]


def _wrap(value: str, *, max_chars: int) -> list[str]:
    text = " ".join(str(value or "").split())
    if not text:
        return [""]
    words = text.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        if len(word) > max_chars:
            if current:
                lines.append(current)
                current = ""
            lines.extend(word[index : index + max_chars] for index in range(0, len(word), max_chars))
            continue
        candidate = word if not current else f"{current} {word}"
        if len(candidate) > max_chars:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _escape(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)
