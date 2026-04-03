from __future__ import annotations

import requests

from app.config import TELEGRAM_BOT_TOKEN


TELEGRAM_MESSAGE_LIMIT = 4000


def split_text(text: str, limit: int = TELEGRAM_MESSAGE_LIMIT) -> list[str]:
    text = text.strip()

    if not text:
        return []

    if len(text) <= limit:
        return [text]

    parts: list[str] = []
    current = ""

    for line in text.splitlines():
        candidate = f"{current}\n{line}" if current else line

        if len(candidate) <= limit:
            current = candidate
            continue

        if current:
            parts.append(current)
            current = ""

        while len(line) > limit:
            parts.append(line[:limit])
            line = line[limit:]

        current = line

    if current:
        parts.append(current)

    return parts


def send_message(text: str, chat_id: str) -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    if not chat_id:
        raise RuntimeError("chat_id is not set")

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    for chunk in split_text(text):
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": chunk,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
        response.raise_for_status()
