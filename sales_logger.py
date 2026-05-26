from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv
from sheets_client import get_sheet


def parse_sale_arg(arg: str) -> tuple[str, int, float]:
    parts = arg.strip().split(":")
    if len(parts) != 3:
        raise ValueError(
            "รูปแบบคำสั่งต้องเป็น เมนู:จำนวน:ราคา เช่น friedrice:2:120"
        )

    menu, qty_str, price_str = parts
    if not menu:
        raise ValueError("เมนูต้องไม่เป็นค่าว่าง")

    try:
        quantity = int(qty_str)
    except ValueError as exc:
        raise ValueError("จำนวนต้องเป็นจำนวนเต็ม") from exc

    try:
        price = float(price_str)
    except ValueError as exc:
        raise ValueError("ราคาต่อหน่วยต้องเป็นตัวเลข") from exc

    if quantity < 0 or price < 0:
        raise ValueError("จำนวนและราคาต้องไม่เป็นลบ")

    return menu, quantity, price


def main() -> None:
    env_path = Path(__file__).with_name(".env")
    load_dotenv(dotenv_path=env_path)

    if len(sys.argv) != 2:
        print("ใช้งาน: python sales_logger.py เมนู:จำนวน:ราคา")
        print("ตัวอย่าง: python sales_logger.py friedrice:2:120")
        raise SystemExit(1)

    sale_arg = sys.argv[1]
    try:
        menu, quantity, price = parse_sale_arg(sale_arg)
    except ValueError as exc:
        print(f"ข้อผิดพลาด: {exc}")
        raise SystemExit(1)

    total = quantity * price
    row = [menu, quantity, price, total]

    sheet = get_sheet()
    sheet.append_row(row)

    print(f"เพิ่มยอดขายเรียบร้อย: {row}")


if __name__ == "__main__":
    main()
#Action
