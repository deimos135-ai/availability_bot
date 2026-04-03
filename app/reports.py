from __future__ import annotations

from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

from app.config import REPORT_LIMIT, TIMEZONE, WORKSHEET_NAME
from app.google_sheets import get_all_rows


def normalize_number(value: str) -> float:
    raw = str(value).strip().replace(" ", "").replace(",", ".")

    if not raw:
        return 0.0

    try:
        return float(raw)
    except ValueError:
        return 0.0


def parse_rows(rows: list[list[str]]) -> list[dict]:
    if len(rows) < 2:
        return []

    data_rows = rows[1:]
    parsed: list[dict] = []

    for row in data_rows:
        name = row[0].strip() if len(row) > 0 else ""
        outages = normalize_number(row[1]) if len(row) > 1 else 0.0
        downtime = normalize_number(row[2]) if len(row) > 2 else 0.0
        subscribers = normalize_number(row[3]) if len(row) > 3 else 0.0
        comment = row[4].strip() if len(row) > 4 else ""

        if not name:
            continue

        parsed.append(
            {
                "name": name,
                "outages": outages,
                "downtime": downtime,
                "subscribers": subscribers,
                "comment": comment,
            }
        )

    return parsed


def build_accessibility_report() -> str:
    rows = get_all_rows(WORKSHEET_NAME)
    items = parse_rows(rows)

    if not items:
        return "Немає даних для звіту."

    total_outages = sum(item["outages"] for item in items)
    total_downtime = sum(item["downtime"] for item in items)
    total_subscribers = sum(item["subscribers"] for item in items)

    items.sort(key=lambda x: (x["downtime"], x["outages"], x["subscribers"]), reverse=True)

    now = datetime.now(ZoneInfo(TIMEZONE)).strftime("%d.%m.%Y %H:%M")

    lines: list[str] = [
        "<b>Звіт по доступності</b>",
        f"Сформовано: {now}",
        "",
        "<b>Загалом:</b>",
        f"• Вузлів у звіті: {len(items)}",
        f"• Відключень: {int(total_outages)}",
        f"• Простій, год: {total_downtime:.1f}",
        f"• Абонентів: {int(total_subscribers)}",
        "",
        f"<b>Топ-{REPORT_LIMIT} по простою:</b>",
    ]

    for index, item in enumerate(items[:REPORT_LIMIT], start=1):
        name = escape(item["name"])
        lines.append(
            f"{index}. <b>{name}</b> — "
            f"{item['downtime']:.1f} год, "
            f"відключень: {int(item['outages'])}, "
            f"абонентів: {int(item['subscribers'])}"
        )

        if item["comment"]:
            comment = escape(item["comment"])
            if len(comment) > 180:
                comment = f"{comment[:177]}..."
            lines.append(f"   {comment}")

    return "\n".join(lines)
