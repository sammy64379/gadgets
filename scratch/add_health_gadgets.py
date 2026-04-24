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
    # Use headers to avoid basic bot detection
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

# New Health & Medical Gadgets
new_health = [
    {
        "name": "Omron Platinum Blood Pressure Monitor",
        "category": "health",
        "price": 12500.0,
        "search": "Omron Platinum Blood Pressure Monitor product isolated white background",
        "filename": "omron-platinum-bpm-premium.jpg",
        "details": "Accurate and reliable digital blood pressure monitor with Dual Display, Bluetooth connectivity, and Advanced Averaging.",
    },
    {
        "name": "Withings Thermo Smart Thermometer",
        "category": "health",
        "price": 14500.0,
        "search": "Withings Thermo Smart Temporal Thermometer product isolated white background",
        "filename": "withings-thermo-premium.jpg",
        "details": "Fast and non-invasive smart temporal thermometer. Syncs with the Health Mate app via Wi-Fi or Bluetooth.",
    },
    {
        "name": "Theragun Pro (5th Generation)",
        "category": "health",
        "price": 85000.0,
        "search": "Theragun Pro 5th Gen massage gun product isolated white background",
        "filename": "theragun-pro-premium.jpg",
        "details": "Professional-grade percussion therapy device. QuietForce Technology, OLED screen, and customizable speed range.",
    },
    {
        "name": "Oral-B iO Series 9 Electric Toothbrush",
        "category": "health",
        "price": 35000.0,
        "search": "Oral-B iO Series 9 Black Onyx product isolated white background",
        "filename": "oralb-io9-premium.jpg",
        "details": "Revolutionary iO technology with linear magnetic drive. AI Tracking with 3D Teeth Tracking. 7 Smart Modes.",
    },
    {
        "name": "Zacurate Pro Pulse Oximeter",
        "category": "health",
        "price": 4500.0,
        "search": "Zacurate Pro Series 500DL Pulse Oximeter product isolated white background",
        "filename": "zacurate-oximeter-premium.jpg",
        "details": "Reliable SpO2 and Pulse Rate readings for sports or aviation use. Silicon cover for durability.",
    }
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for item in new_health:
    print(f"Searching for: {item['name']}")
    urls = search_bing_images(item['search'])
    if download_best(urls, item['filename']):
        new_path = f"/static/uploads/{item['filename']}"
        # Check if already exists to avoid duplicates
        c.execute("SELECT id FROM items WHERE name = ?", (item['name'],))
        if not c.fetchone():
            c.execute("INSERT INTO items (name, price, category, image, details, stock) VALUES (?, ?, ?, ?, ?, ?)", 
                     (item['name'], item['price'], item['category'], new_path, item['details'], 10))
            print(f"  Added: {item['name']}")
        else:
            print(f"  Skip: {item['name']} already in DB.")
    else:
        print(f"  Failed: Could not find image for {item['name']}")

conn.commit()
conn.close()
print("Done!")
