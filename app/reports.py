from __future__ import annotations

from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

from app.config import TIMEZONE, WORKSHEET_NAME
from app.google_sheets import get_all_rows


def get_now() -> datetime:
    return datetime.now(ZoneInfo(TIMEZONE))


def normalize_date(value: str) -> str:
    raw = str(value).strip()
    if not raw:
        return ""

    parts = raw.split(".")
    if len(parts) < 2:
        return raw

    day = parts[0].zfill(2)
    month = parts[1].zfill(2)
    return f"{day}.{month}"


def clean_text(value: str) -> str:
    return str(value).strip()


def is_zero_duration(value: str) -> bool:
    raw = clean_text(value)
    return raw in {"", "0", "00:00", "00:00:00"}


def row_has_incident(row: list[str]) -> bool:
    time_off = clean_text(row[3]) if len(row) > 3 else ""
    time_on = clean_text(row[4]) if len(row) > 4 else ""
    downtime = clean_text(row[5]) if len(row) > 5 else ""

    return bool(
        time_off
        or time_on
        or (downtime and not is_zero_duration(downtime))
    )


def parse_incidents_for_date(rows: list[list[str]], target_date: str) -> list[dict]:
    incidents: list[dict] = []
    current_date = ""

    for row in rows[2:]:
        date_cell = clean_text(row[0]) if len(row) > 0 else ""
        if date_cell:
            current_date = normalize_date(date_cell)

        if current_date != target_date:
            continue

        if not row_has_incident(row):
            continue

        incidents.append(
            {
                "node": clean_text(row[1]) if len(row) > 1 else "",
                "place": clean_text(row[2]) if len(row) > 2 else "",
                "time_off": clean_text(row[3]) if len(row) > 3 else "",
                "time_on": clean_text(row[4]) if len(row) > 4 else "",
                "downtime": clean_text(row[5]) if len(row) > 5 else "",
                "what_happened": clean_text(row[6]) if len(row) > 6 else "",
                "reason": clean_text(row[7]) if len(row) > 7 else "",
            }
        )

    return incidents


def format_incident(item: dict) -> str:
    node = escape(item["node"]) if item["node"] else "—"
    place = escape(item["place"]) if item["place"] else "—"
    time_off = escape(item["time_off"]) if item["time_off"] else "—"
    time_on = escape(item["time_on"]) if item["time_on"] else "—"
    downtime = escape(item["downtime"]) if item["downtime"] else "—"

    lines = [
        f"⚠️ <b>{node}</b> — <b>{place}</b>",
        f"⏱ Відключення: <b>{time_off}</b> → <b>{time_on}</b>",
        f"🕒 Простій: <b>{downtime}</b>",
    ]

    if item["what_happened"]:
        lines.append(f"📝 Що сталось: {escape(item['what_happened'])}")

    if item["reason"]:
        lines.append(f"🔧 Причина: {escape(item['reason'])}")

    return "\n".join(lines)


def build_daily_report() -> str:
    now = get_now()
    target_date = now.strftime("%d.%m")
    report_date = now.strftime("%d.%m.%Y")

    rows = get_all_rows(WORKSHEET_NAME)
    incidents = parse_incidents_for_date(rows, target_date)

    if not incidents:
        return (
            f"📡 <b>Звіт по доступності за {report_date}</b>\n\n"
            "✅ Аварійних випадків не зафіксовано, гарного вечора."
        )

    lines = [f"📡 <b>Звіт по доступності за {report_date}</b>", ""]

    for item in incidents:
        lines.append(format_incident(item))
        lines.append("")

    return "\n".join(lines).strip()
