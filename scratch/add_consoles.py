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

def slugify(text):
    return re.sub(r'[^a-zA-Z0-9]', '-', text.lower()).strip('-')

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

# 1. Update PlayStation 5 to Black
ps5_search = "Sony PlayStation 5 Console Midnight Black plates covers product isolated white background"
ps5_filename = "sony-playstation-5-black-premium.jpg"

print(f"Searching: {ps5_search}")
ps5_urls = search_bing_images(ps5_search)
if download_best(ps5_urls, ps5_filename):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    new_path = f"/static/uploads/{ps5_filename}"
    c.execute("UPDATE items SET image = ?, name = ? WHERE name LIKE ?", (new_path, "Sony PlayStation 5 Console (Midnight Black)", "%PlayStation 5 Console%"))
    conn.commit()
    print(f"Updated PS5 DB: {new_path}")
    conn.close()

# 2. Add new gaming consoles
new_consoles = [
    {
        "name": "Nintendo Switch OLED Model",
        "category": "gaming",
        "price": 55000.0,
        "search": "Nintendo Switch OLED model neon red blue white background isolated product photo",
        "filename": "nintendo-switch-oled-premium.jpg",
        "details": "7-inch OLED screen, 64GB internal storage, enhanced audio, and a wide adjustable stand.",
    },
    {
        "name": "Xbox Series S 512GB Console",
        "category": "gaming",
        "price": 45000.0,
        "search": "Xbox Series S 512GB Console product photo white background isolated",
        "filename": "xbox-series-s-premium.jpg",
        "details": "All-digital next-gen gaming. 512GB Custom NVMe SSD. 120 FPS high framerate.",
    },
    {
        "name": "Steam Deck OLED 512GB",
        "category": "gaming",
        "price": 95000.0,
        "search": "Steam Deck OLED 512GB product photo white background isolated",
        "filename": "steam-deck-oled-premium.jpg",
        "details": "7.4 inch HDR OLED screen, 90Hz refresh rate, 512GB NVMe SSD, Wi-Fi 6E.",
    }
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for console in new_consoles:
    print(f"Searching: {console['search']}")
    urls = search_bing_images(console['search'])
    if download_best(urls, console['filename']):
        new_path = f"/static/uploads/{console['filename']}"
        c.execute("INSERT INTO items (name, price, category, image, details, stock) VALUES (?, ?, ?, ?, ?, ?)", 
                 (console['name'], console['price'], console['category'], new_path, console['details'], 15))
        print(f"Added new console: {console['name']}")
    else:
        print(f"Failed to find image for {console['name']}")

conn.commit()
conn.close()
print("Done!")
