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

laptops_to_update = [
    {
        "search_term": "Dell Inspiron 15 3520 Core I5 laptop product photo white background",
        "db_name": "Dell Inspiron 15 3520 Core I5",
        "filename": "dell-inspiron-15-3520-premium.jpg"
    },
    {
        "search_term": "Asus TUF Gaming A15 Ryzen 7 RTX 4060 laptop product photo white background",
        "db_name": "Asus Tuf Gaming A15 Ryzen 7 Rtx 4060",
        "filename": "asus-tuf-gaming-a15-premium.jpg"
    },
    {
        "search_term": "Lenovo IdeaPad Flex 5 Ryzen 5 laptop product photo white background",
        "db_name": "Lenovo IdeaPad Flex 5 (Ryzen 5 7530U)",
        "filename": "lenovo-ideapad-flex-5-premium.jpg"
    },
    {
        # 'Gaming 5000X3125' is a weird generic name, let's substitute it visually with an AW or Razer
        "search_term": "Alienware m16 R2 Gaming Laptop product photo white background",
        "db_name": "Gaming 5000X3125",
        "new_name": "Alienware m16 R2 Gaming Laptop", # Renaming it so it sounds like a real premium product
        "filename": "alienware-m16-r2-premium.jpg"
    }
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for laptop in laptops_to_update:
    print(f"Updating image for: {laptop['db_name']}")
    urls = search_bing_images(laptop['search_term'])
    if download_best(urls, laptop['filename']):
        new_path = f"/static/uploads/{laptop['filename']}"
        new_name = laptop.get('new_name', laptop['db_name'])
        c.execute("UPDATE items SET image = ?, name = ? WHERE name LIKE ?", (new_path, new_name, f"%{laptop['db_name']}%"))
        print(f"  Updated: {new_name}")
    else:
        print(f"  Failed to find image for {laptop['db_name']}")

conn.commit()
conn.close()
print("Done!")
