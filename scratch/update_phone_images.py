import requests
import re
import urllib.parse
import os
import sqlite3

DB_PATH = r"c:\Users\sammy\OneDrive\Desktop\electronics e commerce\app\test.db"
UPLOADS_DIR = (
    r"c:\Users\sammy\OneDrive\Desktop\electronics e commerce\app\static\uploads"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
}


def search_bing_images(query):
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}&qft=+filterui:imagesize-large"
    response = requests.get(url, headers=HEADERS, timeout=10)
    return re.findall(r"murl&quot;:&quot;(.*?)&quot;", response.text)


def download_best(urls, filename, min_size=15000):
    for url in urls:
        url = url.replace("&amp;", "&")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200 or "text/html" in resp.headers.get(
                "Content-Type", ""
            ):
                continue
            if len(resp.content) < min_size:
                continue
            path = os.path.join(UPLOADS_DIR, filename)
            with open(path, "wb") as f:
                f.write(resp.content)
            return True
        except Exception:
            pass
    return False


phones_to_update = [
    {
        "search_term": "Xiaomi Redmi 13C Clover Green product photo white background",
        "db_name": "Xiaomi Redmi 13C 6Gb 128Gb",
        "filename": "redmi-13c-green-premium.jpg",
    },
    {
        "search_term": "Oppo Reno11 Pro 5G Pearl White product photo white background isolated",
        "db_name": "Oppo Reno11 Pro 5G 12Gb 512Gb",
        "filename": "oppo-reno11-pro-premium.jpg",
    },
    {
        "search_term": "Oppo A79 5G Glowing Green product photo white background",
        "db_name": "Oppo A79 5G 8Gb 256G",
        "filename": "oppo-a79-green-premium.jpg",
    },
    {
        "search_term": "Infinix Zero 30 5G Rome Green product photo white background isolated",
        "db_name": "Infinix Zero 30 5G 12Gb 256Gb",
        "filename": "infinix-zero-30-premium.jpg",
    },
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for phone in phones_to_update:
    print(f"Updating image for: {phone['db_name']}")
    urls = search_bing_images(phone["search_term"])
    if download_best(urls, phone["filename"]):
        new_path = f"/static/uploads/{phone['filename']}"
        # Using LIKE to catch variations in naming if any
        c.execute(
            "UPDATE items SET image = ? WHERE name LIKE ?",
            (new_path, f"%{phone['db_name']}%"),
        )
        if c.rowcount > 0:
            print(f"  Updated: {phone['db_name']} with {new_path}")
        else:
            print(f"  Warning: No entry found for {phone['db_name']}")
    else:
        print(f"  Failed: Could not find image for {phone['search_term']}")

conn.commit()
conn.close()
print("Done!")
