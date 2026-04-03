from __future__ import annotations

import logging
import time

import requests

from app.config import ALLOWED_CHAT_ID, TELEGRAM_BOT_TOKEN
from app.reports import build_daily_report
from app.telegram_sender import send_message


logger = logging.getLogger(__name__)


def get_updates(offset: int | None = None, timeout: int = 30) -> dict:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params: dict = {"timeout": timeout}

    if offset is not None:
        params["offset"] = offset

    response = requests.get(url, params=params, timeout=timeout + 10)
    response.raise_for_status()
    return response.json()


def extract_message(update: dict) -> dict | None:
    return update.get("message") or update.get("edited_message")


def handle_report_now(chat_id: str) -> None:
    text = build_daily_report()
    send_message(text, chat_id)


def run_polling() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    logger.info("Telegram polling started")
    offset: int | None = None

    while True:
        try:
            data = get_updates(offset=offset, timeout=30)

            if not data.get("ok"):
                time.sleep(3)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                message = extract_message(update)
                if not message:
                    continue

                chat = message.get("chat", {})
                chat_id = str(chat.get("id", ""))
                text = (message.get("text") or "").strip()

                if ALLOWED_CHAT_ID and chat_id != ALLOWED_CHAT_ID:
                    continue

                if text == "/report_now":
                    logger.info("Received /report_now from chat %s", chat_id)
                    handle_report_now(chat_id)

        except Exception:
            logger.exception("Polling error")
            time.sleep(5)
