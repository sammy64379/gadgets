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

# New Power & Charging Gadgets
new_power = [
    {
        "name": "Anker 737 Power Bank (PowerCore 24K)",
        "category": "power",
        "price": 18500.0,
        "search": "Anker 737 Power Bank PowerCore 24K product isolated white background",
        "filename": "anker-737-powerbank-premium.jpg",
        "details": "Ultra-Powerful Two-Way Charging with 140W max output and smart digital display.",
    },
    {
        "name": "EcoFlow RIVER 2 Portable Power Station",
        "category": "power",
        "price": 35000.0,
        "search": "EcoFlow RIVER 2 Portable Power Station product isolated white background",
        "filename": "ecoflow-river2-premium.jpg",
        "details": "Charge 0-100% in just 60 mins. LiFePO4 battery chemistry with up to 10 years of use.",
    },
    {
        "name": "Belkin BoostCharge Pro 3-in-1 Wireless Stand",
        "category": "power",
        "price": 16500.0,
        "search": "Belkin BoostCharge Pro 3-in-1 Wireless Charging Stand with MagSafe isolated white background",
        "filename": "belkin-boostcharge-3in1-premium.jpg",
        "details": "15W faster wireless charging with MagSafe. Charge your iPhone, Apple Watch, and AirPods simultaneously.",
    },
    {
        "name": "UGREEN Nexode 100W USB C Charger",
        "category": "power",
        "price": 8500.0,
        "search": "UGREEN Nexode 100W 4-Port USB C Charger product isolated white background",
        "filename": "ugreen-nexode-100w-premium.jpg",
        "details": "Gallium Nitride (GaN) charger. Fast charge 4 devices simultaneously with smart power distribution.",
    },
    {
        "name": "Satechi 200W USB-C 6-Port GaN Charger",
        "category": "power",
        "price": 19000.0,
        "search": "Satechi 200W USB-C 6-Port GaN Charger product isolated white background",
        "filename": "satechi-200w-charger-premium.jpg",
        "details": "Next-gen Gallium Nitride technology. Charge up to 6 devices with an ultimate output of 200W.",
    }
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for item in new_power:
    print(f"Searching for: {item['name']}")
    urls = search_bing_images(item['search'])
    if download_best(urls, item['filename']):
        new_path = f"/static/uploads/{item['filename']}"
        # Check if already exists to avoid duplicates
        c.execute("SELECT id FROM items WHERE name = ?", (item['name'],))
        if not c.fetchone():
            c.execute("INSERT INTO items (name, price, category, image, details, stock) VALUES (?, ?, ?, ?, ?, ?)", 
                     (item['name'], item['price'], item['category'], new_path, item['details'], 20))
            print(f"  Added: {item['name']}")
        else:
            print(f"  Skip: {item['name']} already in DB.")
    else:
        print(f"  Failed: Could not find image for {item['name']}")

conn.commit()
conn.close()
print("Done!")
