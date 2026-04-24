import requests
import re
import urllib.parse
import json
import os
import sqlite3

DB_PATH = r"c:\Users\sammy\OneDrive\Desktop\electronics e commerce\app\test.db"
UPLOADS_DIR = r"c:\Users\sammy\OneDrive\Desktop\electronics e commerce\app\static\uploads"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
}

def search_bing_images(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}&qft=+filterui:imagesize-large"
    response = requests.get(url, headers=headers, timeout=10)
    murls = re.findall(r'murl&quot;:&quot;(.*?)&quot;', response.text)
    return murls

def slugify(text):
    return re.sub(r'[^a-zA-Z0-9]', '-', text.lower()).strip('-')

def download_best(urls, filename, min_size=15000):
    """Try each URL; keep the first one whose content >= min_size bytes."""
    for url in urls:
        url = url.replace('&amp;', '&')
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                continue
            ct = resp.headers.get('Content-Type', '')
            if 'text/html' in ct:
                continue
            if len(resp.content) < min_size:
                print(f"    Skipped {url[:80]}... ({len(resp.content)} bytes, too small)")
                continue
            path = os.path.join(UPLOADS_DIR, filename)
            with open(path, 'wb') as f:
                f.write(resp.content)
            print(f"    Downloaded {len(resp.content):,} bytes -> {filename}")
            return True
        except Exception as e:
            print(f"    Error: {e}")
    return False

# Items that need better images (< 25KB currently)
items_to_fix = [
    {
        "search": "Xiaomi Redmi Note 13 Pro 5G phone product photo",
        "db_name": "Xiaomi Redmi Note 13 Pro 5G",
        "filename": "xiaomi-redmi-note-13-pro-5g-premium.png",
    },
    {
        "search": "ASUS Zenbook 14 OLED UX3402 laptop product photo",
        "db_name": "Asus Zenbook 14 Oled Ux3402",
        "filename": "asus-zenbook-14-oled-ux3402-premium.png",
    },
    {
        "search": "Samsung Galaxy A55 5G phone product photo",
        "db_name": "Samsung Galaxy A55 5G (8GB/256GB)",
        "filename": "samsung-galaxy-a55-5g--8gb-256gb-premium.png",
    },
    {
        "search": "Samsung Galaxy S23 FE phone product photo",
        "db_name": "Samsung Galaxy S23 FE (8GB/256GB)",
        "filename": "samsung-galaxy-s23-fe--8gb-256gb-premium.jpg",
    },
    {
        "search": "Hisense 55U7H ULED 4K Smart TV product photo",
        "db_name": "Hisense 55 U7H Uled 4K Smart Tv",
        "filename": "hisense-55-u7h-uled-4k-smart-tv-premium.jpg",
    },
    {
        "search": "HP Spectre x360 14 laptop product photo",
        "db_name": "HP Spectre x360 14 (Core Ultra 7)",
        "filename": "hp-spectre-x360-14--core-ultra-7-premium.png",
    },
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

for item in items_to_fix:
    print(f"\nSearching: {item['search']}")
    urls = search_bing_images(item["search"])
    print(f"  Found {len(urls)} candidate URLs")

    if download_best(urls, item["filename"]):
        new_path = f"/static/uploads/{item['filename']}"
        cursor.execute("UPDATE items SET image = ? WHERE name LIKE ?", (new_path, f"%{item['db_name']}%"))
        if cursor.rowcount > 0:
            print(f"  DB updated: {new_path}")
        else:
            print(f"  WARNING: '{item['db_name']}' not found in DB")
    else:
        print(f"  FAILED - no suitable image found for {item['db_name']}")

conn.commit()
conn.close()
print("\nDone!")
