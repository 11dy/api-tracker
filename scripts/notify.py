#!/usr/bin/env python3
"""out/summary.md를 슬랙 Incoming Webhook으로 발송한다.

환경변수: SLACK_WEBHOOK_URL
슬랙 메시지 한도(40,000자) 초과 시 줄 단위로 분할 발송.
"""
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
SUMMARY_FILE = ROOT / "out" / "summary.md"
CHUNK_LIMIT = 38000  # 슬랙 한도 40,000자 대비 안전 마진


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


def send(webhook_url: str, text: str):
    resp = requests.post(webhook_url, json={"text": text}, timeout=20)
    resp.raise_for_status()


def main():
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("환경변수 SLACK_WEBHOOK_URL 필요", file=sys.stderr)
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
        send(webhook_url, chunk)
        print(f"발송 {i}/{len(chunks)} ({len(chunk)}자)")
        if i < len(chunks):
            time.sleep(1)  # 슬랙 rate limit 회피


if __name__ == "__main__":
    main()
