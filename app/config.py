from __future__ import annotations

import os


GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "").strip()
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "").strip()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

TIMEZONE = os.getenv("TIMEZONE", "Europe/Kyiv").strip()
WORKSHEET_NAME = os.getenv("WORKSHEET_NAME", "СІЧЕНЬ").strip()

ALLOWED_CHAT_ID = os.getenv("ALLOWED_CHAT_ID", TELEGRAM_CHAT_ID).strip()

DAILY_REPORT_HOUR = int(os.getenv("DAILY_REPORT_HOUR", "20"))
DAILY_REPORT_MINUTE = int(os.getenv("DAILY_REPORT_MINUTE", "0"))
