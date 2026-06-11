#!/usr/bin/env python3
"""out/summary.md를 텔레그램 봇으로 발송한다.

환경변수: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
4096자 초과 시 줄 단위로 분할 발송. Markdown 파싱 실패 시 plain text로 재시도.
"""
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
SUMMARY_FILE = ROOT / "out" / "summary.md"
TELEGRAM_LIMIT = 4096
CHUNK_LIMIT = 4000  # 안전 마진


def split_message(text: str, limit: int = CHUNK_LIMIT):
    """줄 단위로 limit 이하 청크로 분할. 한 줄이 limit를 넘으면 강제 절단."""
    chunks, current = [], ""
    for line in text.splitlines(keepends=True):
        while len(line) > limit:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(line[:limit])
            line = line[limit:]
        if len(current) + len(line) > limit:
            chunks.append(current)
            current = line
        else:
            current += line
    if current.strip():
        chunks.append(current)
    return [c for c in (c.strip("\n") for c in chunks) if c]


def send(token: str, chat_id: str, text: str):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, json=payload, timeout=20)
    if resp.status_code == 400:
        # Markdown 파싱 실패(특수문자 등) 시 plain text로 재시도
        payload.pop("parse_mode")
        resp = requests.post(url, json=payload, timeout=20)
    resp.raise_for_status()


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("환경변수 TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 필요", file=sys.stderr)
        sys.exit(1)

    if not SUMMARY_FILE.exists():
        print(f"{SUMMARY_FILE} 없음 — 발송할 내용 없음", file=sys.stderr)
        sys.exit(1)

    text = SUMMARY_FILE.read_text(encoding="utf-8").strip()
    if not text:
        print("summary.md 비어 있음 — 발송 생략")
        return

    chunks = split_message(text)
    for i, chunk in enumerate(chunks, 1):
        send(token, chat_id, chunk)
        print(f"발송 {i}/{len(chunks)} ({len(chunk)}자)")
        if i < len(chunks):
            time.sleep(1)  # 텔레그램 rate limit 회피


if __name__ == "__main__":
    main()
