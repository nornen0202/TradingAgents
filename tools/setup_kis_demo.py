"""Small Windows registration window. Saves encrypted demo settings; reads only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import queue
import sys
import threading
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tradingagents.execution.demo_secrets import (  # noqa: E402
    SecretStoreError,
    credential_bundle,
    save_demo_settings,
    storage_path,
)
from tools.check_kis_demo import check  # noqa: E402

DEMO_APPLY_URL = "https://securities.koreainvestment.com/main/research/virtual/_static/TF07da010000.jsp"
API_APPLY_URL = (
    "https://securities.koreainvestment.com/main/customer/systemdown/RestAPIService.jsp"
)


def save_and_check(app_key, app_secret, account):
    save_demo_settings(credential_bundle(app_key, app_secret, account))
    return check_saved()


def check_saved():
    result = check(connect=True)
    output = storage_path().with_name("kis-demo-readiness.json")
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return result


def status_message(result):
    messages = {
        "READ_CONNECTION_VERIFIED": "연결 확인 완료. 잔고와 당일 주문을 조회했습니다. 다음 단계는 계좌 대사입니다.",
        "MISSING_DEMO_SETTINGS": "모의투자 전용 정보를 입력해주세요.",
        "CONFIGURATION_UNREADABLE": "저장 정보를 열 수 없습니다. 현재 Windows 사용자로 다시 등록해주세요.",
        "CONNECTION_UNVERIFIED": "정보는 저장됐지만 조회 연결을 확인하지 못했습니다. 모의계좌 발급·API 신청 상태를 확인한 뒤 다시 점검해주세요.",
    }
    return messages.get(
        result.get("status"), "모의투자 전용 정보를 입력하고 연결을 확인해주세요."
    )


def create_window():
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("TradingAgents · 모의투자 연결")
    root.geometry("690x650")
    root.minsize(640, 620)
    root.option_add("*Font", ("Malgun Gothic", 10))
    frame = ttk.Frame(root, padding=24)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="모의투자 연결", font=("Malgun Gothic", 18, "bold")).pack(
        anchor="w"
    )
    ttk.Label(
        frame,
        text="1. 한국투자증권에서 모의계좌 발급과 API 신청을 완료하세요.\n2. 모의투자용 키 2개와 전체 계좌번호만 입력하세요.",
        wraplength=620,
    ).pack(anchor="w", pady=(10, 8))
    links = ttk.Frame(frame)
    links.pack(anchor="w", pady=(0, 15))
    ttk.Button(
        links,
        text="모의계좌 신청 열기",
        command=lambda: webbrowser.open(DEMO_APPLY_URL),
    ).pack(side="left", padx=(0, 8))
    ttk.Button(
        links, text="KIS API 신청 열기", command=lambda: webbrowser.open(API_APPLY_URL)
    ).pack(side="left")
    fields = []
    for label in (
        "모의투자 App Key",
        "모의투자 App Secret",
        "모의계좌번호 전체 10자리 (8자리-2자리)",
    ):
        ttk.Label(frame, text=label).pack(anchor="w", pady=(8, 4))
        entry = ttk.Entry(frame, show="*", width=62)
        entry.pack(fill="x")
        fields.append(entry)
    show = tk.BooleanVar(value=False)
    ttk.Checkbutton(
        frame,
        text="입력 내용 표시",
        variable=show,
        command=lambda: [
            entry.configure(show="" if show.get() else "*") for entry in fields
        ],
    ).pack(anchor="w", pady=9)
    ttk.Label(
        frame,
        text="정보는 현재 Windows 사용자용으로 암호화해 저장합니다.\n이 화면은 인증·잔고·주문 조회만 수행하며 매매 주문을 전송하지 않습니다.",
        wraplength=620,
    ).pack(anchor="w", pady=(0, 12))
    feedback = tk.StringVar(
        value="발급받은 모의투자 정보를 입력해주세요. 키를 채팅으로 보낼 필요는 없습니다."
    )
    messages = queue.Queue()
    buttons = []

    def start(save):
        values = tuple(entry.get() for entry in fields) if save else None
        if save:
            try:
                credential_bundle(*values)
            except SecretStoreError:
                feedback.set(
                    "키 2개와 계좌번호 10자리를 모두 확인해주세요. 상품코드 2자리까지 필요합니다."
                )
                return
        for button in buttons:
            button.configure(state="disabled")
        for entry in fields:
            entry.delete(0, "end")
            entry.configure(state="disabled")
        feedback.set("모의투자 연결을 확인하고 있습니다. 잠시 기다려주세요.")

        def work():
            try:
                messages.put(
                    status_message(save_and_check(*values) if save else check_saved())
                )
            except Exception:
                # Do not surface traceback, key values, account IDs or broker bodies.
                messages.put(
                    "연결 준비를 완료하지 못했습니다. 현재 Windows 사용자 권한과 모의투자 신청 상태를 확인해주세요."
                )

        threading.Thread(target=work, daemon=True).start()

    actions = ttk.Frame(frame)
    actions.pack(anchor="w", pady=5)
    buttons.append(
        ttk.Button(actions, text="저장하고 연결 확인", command=lambda: start(True))
    )
    buttons.append(
        ttk.Button(
            actions, text="저장된 정보로 다시 확인", command=lambda: start(False)
        )
    )
    for button in buttons:
        button.pack(side="left", padx=(0, 8))
    ttk.Label(frame, textvariable=feedback, wraplength=610, foreground="#17456b").pack(
        anchor="w", fill="x", pady=18
    )

    def receive():
        try:
            feedback.set(messages.get_nowait())
            for button in buttons:
                button.configure(state="normal")
            for entry in fields:
                entry.configure(state="normal")
        except queue.Empty:
            pass
        root.after(150, receive)

    root.after(150, receive)
    return root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Build and close the window; no settings or network",
    )
    args = parser.parse_args()
    root = create_window()
    if args.smoke_test:
        root.after(200, root.destroy)
    root.mainloop()


if __name__ == "__main__":
    main()
