#!/usr/bin/env python3
"""Caption generator for MilkLab cafe Instagram posts.

This script takes a menu item name and price as input, then
returns three Thai-friendly caption styles:
- cute: น่ารัก ๆ
- minimal: เรียบง่าย
- gen-z: เท่ ๆ แบบวัยรุ่น
"""

import argparse


def generate_captions(menu_name: str, price: str) -> dict[str, str]:
    menu = menu_name.strip()
    price_text = price.strip()

    return {
        "cute": (
            f"อยากให้ทุกวันหวานขึ้นลอง {menu} ของเราดูนะ! "
            f"แค่ {price_text} บาทเอง พร้อมให้ฟีลอบอุ่นแบบคาเฟ่ ๆ 💕"
        ),
        "minimal": (
            f"{menu} ราคา {price_text} บาท — Simple แต่ลงตัวมาก เหมาะกับวันที่อยากพักผ่อน"
        ),
        "gen-z": (
            f"สายชิลห้ามพลาด {menu} {price_text} บาท! "
            "อร่อยทันใจ ถ่ายรูปลงไอจีปุ๊บปังปั๊บ 🤙"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="สร้าง caption ภาษาไทยสไตล์เป็นกันเองสำหรับโพสต์คาเฟ่"
    )
    parser.add_argument("menu_name", help="ชื่อเมนูที่จะทำ caption")
    parser.add_argument("price", help="ราคาของเมนู (บาท)")
    parser.add_argument(
        "--style",
        choices=["cute", "minimal", "gen-z", "all"],
        default="all",
        help="เลือกสไตล์ caption ที่ต้องการ (default: all)",
    )

    args = parser.parse_args()
    captions = generate_captions(args.menu_name, args.price)

    if args.style == "all":
        print("Caption ทั้งหมด:")
        for style, text in captions.items():
            print(f"\n[{style}]\n{text}")
    else:
        print(captions[args.style])


if __name__ == "__main__":
    main()
