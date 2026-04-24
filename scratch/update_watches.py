import requests
import re
import urllib.parse
import os
import sqlite3

DB_PATH = r"c:\Users\sammy\OneDrive\Desktop\electronics e commerce\app\test.db"
UPLOADS_DIR = r"c:\Users\sammy\OneDrive\Desktop\electronics e commerce\app\static\uploads"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
}

def search_bing_images(query):
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}&qft=+filterui:imagesize-large"
    response = requests.get(url, headers=HEADERS, timeout=10)
    return re.findall(r'murl&quot;:&quot;(.*?)&quot;', response.text)

def download_best(urls, filename, min_size=15000):
    for url in urls:
        url = url.replace('&amp;', '&')
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200 or 'text/html' in resp.headers.get('Content-Type', ''):
                continue
            if len(resp.content) < min_size:
                continue
            path = os.path.join(UPLOADS_DIR, filename)
            with open(path, 'wb') as f:
                f.write(resp.content)
            return True
        except Exception:
            pass
    return False

# 1. Update Existing Watches (Solo Product, No Hands)
watches_to_update = [
    {
        "name": "Apple Watch Series 9 GPS 45mm",
        "search": "Apple Watch Series 9 45mm product isolated white background no hand",
        "filename": "apple-watch-s9-solo-premium.jpg"
    },
    {
        "name": "Samsung Galaxy Watch 6 classic",
        "search": "Samsung Galaxy Watch 6 Classic product isolated white background no hand",
        "filename": "samsung-galaxy-watch6-solo-premium.jpg"
    }
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for watch in watches_to_update:
    print(f"Updating image for: {watch['name']}")
    urls = search_bing_images(watch['search'])
    if download_best(urls, watch['filename']):
        new_path = f"/static/uploads/{watch['filename']}"
        c.execute("UPDATE items SET image = ? WHERE name LIKE ?", (new_path, f"%{watch['name']}%"))
        print(f"  Updated: {watch['name']}")
    else:
        print(f"  Failed to find solo image for {watch['name']}")

# 2. Add New Smartwatches
new_smartwatches = [
    {
        "name": "Google Pixel Watch 2",
        "category": "wearables",
        "price": 38500.0,
        "search": "Google Pixel Watch 2 product isolated white background",
        "filename": "google-pixel-watch-2-premium.jpg",
        "details": "Advanced health and fitness tracking, AI-powered heart rate, and 24-hour battery with Always-on Display.",
    },
    {
        "name": "Garmin Fenix 7 Pro Sapphire Solar",
        "category": "wearables",
        "price": 95000.0,
        "search": "Garmin Fenix 7 Pro Sapphire Solar product isolated white background",
        "filename": "garmin-fenix-7-pro-premium.jpg",
        "details": "Multisport GPS watch with solar charging, built-in LED flashlight, and advanced training features.",
    },
    {
        "name": "Huawei Watch GT 4 (46mm)",
        "category": "wearables",
        "price": 24000.0,
        "search": "Huawei Watch GT 4 46mm black product isolated white background",
        "filename": "huawei-watch-gt4-premium.jpg",
        "details": "Strong battery life up to 14 days, professional-level sports tracking, and geometric aesthetic design.",
    }
]

for watch in new_smartwatches:
    print(f"Searching for: {watch['name']}")
    urls = search_bing_images(watch['search'])
    if download_best(urls, watch['filename']):
        new_path = f"/static/uploads/{watch['filename']}"
        c.execute("SELECT id FROM items WHERE name = ?", (watch['name'],))
        if not c.fetchone():
            c.execute("INSERT INTO items (name, price, category, image, details, stock) VALUES (?, ?, ?, ?, ?, ?)", 
                     (watch['name'], watch['price'], watch['category'], new_path, watch['details'], 12))
            print(f"  Added: {watch['name']}")
        else:
            print(f"  Skip: {watch['name']} already in DB.")
    else:
        print(f"  Failed: Could not find image for {watch['name']}")

conn.commit()
conn.close()
print("Done!")
