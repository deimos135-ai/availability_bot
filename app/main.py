from __future__ import annotations

import logging

from app.reports import build_daily_report
from app.telegram_sender import send_message


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Building daily report...")
    text = build_daily_report()

    logger.info("Sending message to Telegram...")
    send_message(text)

    logger.info("Done")


if __name__ == "__main__":
    main()
