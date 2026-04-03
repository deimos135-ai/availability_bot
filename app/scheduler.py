from __future__ import annotations

import logging
import threading
import time
from datetime import date
from zoneinfo import ZoneInfo
from datetime import datetime

from app.config import DAILY_REPORT_HOUR, DAILY_REPORT_MINUTE, TELEGRAM_CHAT_ID, TIMEZONE
from app.reports import build_daily_report
from app.telegram_sender import send_message


logger = logging.getLogger(__name__)


class DailyReportScheduler:
    def __init__(self) -> None:
        self._tz = ZoneInfo(TIMEZONE)
        self._last_sent_date: date | None = None

    def should_send_now(self) -> bool:
        now = datetime.now(self._tz)

        if now.hour != DAILY_REPORT_HOUR:
            return False

        if now.minute != DAILY_REPORT_MINUTE:
            return False

        if self._last_sent_date == now.date():
            return False

        return True

    def mark_sent(self) -> None:
        now = datetime.now(self._tz)
        self._last_sent_date = now.date()

    def run_forever(self) -> None:
        if not TELEGRAM_CHAT_ID:
            raise RuntimeError("TELEGRAM_CHAT_ID is not set")

        logger.info(
            "Scheduler started, daily report at %02d:%02d %s",
            DAILY_REPORT_HOUR,
            DAILY_REPORT_MINUTE,
            TIMEZONE,
        )

        while True:
            try:
                if self.should_send_now():
                    logger.info("Sending scheduled daily report")
                    text = build_daily_report()
                    send_message(text, TELEGRAM_CHAT_ID)
                    self.mark_sent()

                time.sleep(20)

            except Exception:
                logger.exception("Scheduler error")
                time.sleep(30)


def start_scheduler_in_background() -> threading.Thread:
    scheduler = DailyReportScheduler()
    thread = threading.Thread(target=scheduler.run_forever, daemon=True)
    thread.start()
    return thread
