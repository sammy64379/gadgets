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

# New Bluetooth & Headphones
new_audio = [
    {
        "name": "Apple AirPods Pro (2nd Generation)",
        "category": "electronics",
        "price": 32500.0,
        "search": "Apple AirPods Pro 2nd Gen USB-C product isolated white background",
        "filename": "apple-airpods-pro-2-premium.jpg",
        "details": "Active Noise Cancellation, Transparency mode, and Personalized Spatial Audio with dynamic head tracking.",
    },
    {
        "name": "Bose QuietComfort Ultra Headphones",
        "category": "electronics",
        "price": 58000.0,
        "search": "Bose QuietComfort Ultra Headphones Black product isolated white background",
        "filename": "bose-qc-ultra-premium.jpg",
        "details": "World-class noise cancellation, breakthrough spatialized audio, and elevated design for maximum comfort.",
    },
    {
        "name": "JBL Charge 5 Portable Speaker",
        "category": "electronics",
        "price": 22500.0,
        "search": "JBL Charge 5 Blue product isolated white background",
        "filename": "jbl-charge-5-premium.jpg",
        "details": "IP67 waterproof and dustproof, 20 hours of playtime, and built-in powerbank to charge your devices.",
    },
    {
        "name": "Sony SRS-XE300 Portable Speaker",
        "category": "electronics",
        "price": 19500.0,
        "search": "Sony SRS-XE300 Black product isolated white background",
        "filename": "sony-srs-xe300-premium.jpg",
        "details": "Line-Shape Diffuser for wide sound distribution, X-Balanced Speaker Unit, and IP67 rating.",
    },
    {
        "name": "Marshall Stanmore III Speaker",
        "category": "electronics",
        "price": 45000.0,
        "search": "Marshall Stanmore III Bluetooth Speaker Black product isolated white background",
        "filename": "marshall-stanmore-3-premium.jpg",
        "details": "Iconic design with room-filling sound. Dynamic Loudness and next-generation Bluetooth connectivity.",
    }
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for item in new_audio:
    print(f"Searching for: {item['name']}")
    urls = search_bing_images(item['search'])
    if download_best(urls, item['filename']):
        new_path = f"/static/uploads/{item['filename']}"
        c.execute("SELECT id FROM items WHERE name = ?", (item['name'],))
        if not c.fetchone():
            c.execute("INSERT INTO items (name, price, category, image, details, stock) VALUES (?, ?, ?, ?, ?, ?)", 
                     (item['name'], item['price'], item['category'], new_path, item['details'], 15))
            print(f"  Added: {item['name']}")
        else:
            print(f"  Skip: {item['name']} already in DB.")
    else:
        print(f"  Failed: Could not find image for {item['name']}")

conn.commit()
conn.close()
print("Done!")
