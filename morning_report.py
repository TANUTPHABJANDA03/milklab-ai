from __future__ import annotations

import datetime
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from sheets_client import get_sheet


def parse_date(value: str) -> datetime.date | None:
    text = value.strip()
    if not text:
        return None

    formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"]
    for fmt in formats:
        try:
            return datetime.datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    try:
        return datetime.datetime.fromisoformat(text).date()
    except ValueError:
        return None


def safe_int(value: str) -> int:
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def safe_float(value: str) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def detect_date_column(header_row: list[str]) -> int | None:
    lower = [cell.strip().lower() for cell in header_row]
    for idx, cell in enumerate(lower):
        if any(keyword in cell for keyword in ["date", "วันที่", "day", "timestamp"]):
            return idx
    return None


def build_summary(rows: list[list[str]], date_col: int | None) -> tuple[str, bool]:
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    filtered: list[list[str]] = []

    if date_col is not None:
        for row in rows:
            if len(row) <= date_col:
                continue
            row_date = parse_date(row[date_col])
            if row_date == yesterday:
                filtered.append(row)
    else:
        normalized = [cell.strip() for cell in rows[0]]
        if len(normalized) >= 4 and any(cell.lower() in ["menu", "เมนู"] for cell in normalized):
            return (
                "ยังไม่สามารถกรองยอดขายของเมื่อวานได้ เพราะข้อมูลในแผ่นงานไม่มีคอลัมน์วันที่ 😢\n"
                "กรุณาเพิ่มคอลัมน์วันที่ไว้ด้วย เช่น Date หรือ วันที่ แล้วลองใหม่อีกครั้ง",
                False,
            )
        filtered = rows

    if not filtered:
        return (
            f"💤 ไม่มียอดขายของเมื่อวาน ({yesterday.strftime('%Y-%m-%d')}) เลยนะคะ\n"
            "พักผ่อนสบาย ๆ ก่อน แล้วค่อยดูอีกทีนะคะ 😊",
            True,
        )

    menu_totals: dict[str, float] = {}
    total_revenue = 0.0
    total_items = 0

    for row in filtered:
        if len(row) >= 4:
            menu = row[1].strip() if date_col is not None else row[0].strip()
            quantity = safe_int(row[2] if date_col is not None else row[1])
            price = safe_float(row[3] if date_col is not None else row[2])
            revenue = quantity * price
        elif len(row) == 3:
            menu = row[0].strip()
            quantity = safe_int(row[1])
            price = safe_float(row[2])
            revenue = quantity * price
        else:
            continue

        total_revenue += revenue
        total_items += quantity
        menu_totals[menu] = menu_totals.get(menu, 0.0) + revenue

    if not menu_totals:
        return (
            "ยังไม่พบข้อมูลยอดขายที่อ่านได้สำหรับเมื่อวานค่ะ 🧐\n"
            "ลองตรวจสอบรูปแบบแผ่นงานให้มี เมนู, จำนวน, ราคา, ยอดรวม หรือ Date ตามลำดับ",
            False,
        )

    best_menu = max(menu_totals.items(), key=lambda item: item[1])
    best_menu_name, best_menu_value = best_menu

    summary = (
        f"🌞 สรุปยอดขายเมื่อวาน ({yesterday.strftime('%Y-%m-%d')})\n"
        f"ยอดขายรวม: {total_revenue:.2f} บาท 💸\n"
        f"จำนวนแก้ว/ชิ้นทั้งหมด: {total_items} ชิ้น 🧋\n"
        f"เมนูขายดีสุด: {best_menu_name} ({best_menu_value:.2f} บาท) 🏆\n"
        "ขอบคุณที่ดูแลร้านอย่างน่ารักนะคะ 💕"
    )
    return summary, True


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    response = requests.post(url, data=payload, timeout=15)
    response.raise_for_status()


def main() -> None:
    env_path = Path(__file__).with_name(".env")
    load_dotenv(dotenv_path=env_path)

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        raise SystemExit("ไม่พบ TELEGRAM_BOT_TOKEN หรือ TELEGRAM_CHAT_ID ใน .env")

    sheet = get_sheet()
    rows = sheet.get_all_values()
    if not rows:
        raise SystemExit("ไม่สามารถอ่านข้อมูลจาก Google Sheet ได้ หรือแผ่นงานว่างอยู่")

    header = rows[0]
    data_rows = rows[1:] if len(rows) > 1 else []
    date_col = detect_date_column(header)

    message, success = build_summary(data_rows, date_col)
    if not success and date_col is None:
        send_telegram_message(bot_token, chat_id, message)
        raise SystemExit(1)

    send_telegram_message(bot_token, chat_id, message)
    print("ส่งสรุปไปยัง Telegram เรียบร้อยแล้ว")


if __name__ == "__main__":
    main()
