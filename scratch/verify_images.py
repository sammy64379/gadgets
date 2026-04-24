# -*- coding: utf-8 -*-
import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"c:\Users\sammy\OneDrive\Desktop\electronics e commerce\app\test.db"
UPLOADS_DIR = r"c:\Users\sammy\OneDrive\Desktop\electronics e commerce\app\static\uploads"

items_to_check = [
    "Philips Airfryer XXL XXL Digital",
    "Xiaomi Redmi Note 13 Pro 5G",
    "Sony 65 Bravia X75K 4K Hdr Led",
    "Infinix Note 40 Pro 5G",
    "Hisense 55 U7H Uled 4K Smart Tv",
    "Dell Xps 13 Plus 13Th Gen I7",
    "Asus Zenbook 14 Oled Ux3402",
    "Lenovo ThinkPad X1 Carbon Gen 11",
    "HP Pavilion 15 (Ryzen 7 7730U)",
    "HP Spectre x360 14 (Core Ultra 7)",
    "Samsung Galaxy A55 5G (8GB/256GB)",
    "Samsung Galaxy S23 FE (8GB/256GB)"
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print(f"{'STATUS':<10} {'ID':<5} {'NAME':<45} {'IMAGE FILE EXISTS?':<20} {'IMAGE PATH'}")
print("-" * 140)

all_ok = True
for item in items_to_check:
    cursor.execute("SELECT id, name, image FROM items WHERE name LIKE ?", (f"%{item}%",))
    result = cursor.fetchone()
    if result:
        item_id, name, image_path = result
        # Check if the physical file exists
        if image_path.startswith("/static/uploads/"):
            filename = image_path.replace("/static/uploads/", "")
            full_path = os.path.join(UPLOADS_DIR, filename)
            file_exists = "✓ YES" if os.path.exists(full_path) else "✗ NO"
            if "NO" in file_exists:
                all_ok = False
        else:
            file_exists = "EXTERNAL URL"
        is_placeholder = "placeholder.svg" in image_path
        status = "❌ PLACEHOLDER" if is_placeholder else "✅ OK"
        if is_placeholder:
            all_ok = False
        print(f"{status:<10} {item_id:<5} {name:<45} {file_exists:<20} {image_path}")
    else:
        print(f"{'NOT FOUND':<10} {'?':<5} {item:<45}")
        all_ok = False

conn.close()
print()
if all_ok:
    print("✅ ALL PRODUCTS have valid images!")
else:
    print("⚠️  Some products may need attention (see above).")
