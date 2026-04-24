import sqlite3
import os

db_path = r"c:\Users\sammy\OneDrive\Desktop\electronics e commerce\app\test.db"

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

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Checking items in database:")
    for item in items_to_check:
        cursor.execute("SELECT id, name, image FROM items WHERE name LIKE ?", (f"%{item}%",))
        result = cursor.fetchone()
        if result:
            print(f"FOUND: {result[0]} | {result[1]} | {result[2]}")
        else:
            print(f"NOT FOUND: {item}")
    
    conn.close()
else:
    print(f"Database not found at {db_path}")
