from __future__ import annotations

import logging

from app.bot import run_polling
from app.scheduler import start_scheduler_in_background


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Starting scheduler...")
    start_scheduler_in_background()

    logger.info("Starting Telegram bot polling...")
    run_polling()


if __name__ == "__main__":
    main()
