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


# Proposed new Home & Kitchen products
new_appliances = [
    {
        "name": "Nespresso Vertuo Next Coffee Machine",
        "category": "appliances",
        "price": 28500.0,
        "search": "Nespresso Vertuo Next Coffee Machine matte black product isolated white background",
        "filename": "nespresso-vertuo-next-premium.jpg",
        "details": "Versatile coffee maker for 5 different cup sizes. Centrifusion technology for a perfect crema.",
    },
    {
        "name": "Samsung 45L Grill Microwave Oven",
        "category": "appliances",
        "price": 32000.0,
        "search": "Samsung 45L Grill Microwave Oven black stainless steel product isolated white background",
        "filename": "samsung-microwave-45l-premium.jpg",
        "details": "Ceramic Inside for easy cleaning, Grill function, and Eco Mode to save energy.",
    },
    {
        "name": "Dyson V15 Detect Cordless Vacuum",
        "category": "appliances",
        "price": 115000.0,
        "search": "Dyson V15 Detect Cordless Vacuum Cleaner product isolated white background",
        "filename": "dyson-v15-detect-premium.jpg",
        "details": "Powerful suction with laser illumination to reveal invisible dust. Piezo sensor for deep cleaning proof.",
    },
    {
        "name": "KitchenAid Artisan Stand Mixer 4.8L",
        "category": "appliances",
        "price": 85000.0,
        "search": "KitchenAid Artisan Stand Mixer Empire Red 4.8L product isolated white background",
        "filename": "kitchenaid-artisan-mixer-premium.jpg",
        "details": "Iconic tilt-head design with 10 speeds and high-performance motor for effortless mixing.",
    },
    {
        "name": "LG 647L Side-by-Side Refrigerator",
        "category": "appliances",
        "price": 245000.0,
        "search": "LG 647L Side-by-Side Refrigerator Matte Black InstaView product isolated white background",
        "filename": "lg-instaview-fridge-premium.jpg",
        "details": "InstaView ThinQ knock twice to see inside. Inverter Linear Compressor and Water/Ice Dispenser.",
    },
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for item in new_appliances:
    print(f"Searching for: {item['name']}")
    urls = search_bing_images(item["search"])
    if download_best(urls, item["filename"]):
        new_path = f"/static/uploads/{item['filename']}"
        # Check if already exists to avoid duplicates
        c.execute("SELECT id FROM items WHERE name = ?", (item["name"],))
        if not c.fetchone():
            c.execute(
                "INSERT INTO items (name, price, category, image, details, stock) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    item["name"],
                    item["price"],
                    item["category"],
                    new_path,
                    item["details"],
                    8,
                ),
            )
            print(f"  Added: {item['name']}")
        else:
            print(f"  Skip: {item['name']} already in DB.")
    else:
        print(f"  Failed: Could not find image for {item['name']}")

conn.commit()
conn.close()
print("Done!")
