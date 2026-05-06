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


def slugify(text):
    return re.sub(r"[^a-zA-Z0-9]", "-", text.lower()).strip("-")


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


# 1. Update Canon R5 to a white version
canon_search = "Canon EOS R50 white mirrorless camera product photo isolated"
canon_filename = "canon-eos-white-premium.jpg"

print(f"Searching: {canon_search}")
canon_urls = search_bing_images(canon_search)
if download_best(canon_urls, canon_filename):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    new_path = f"/static/uploads/{canon_filename}"
    # Update the existing Canon R5 (ID=46) image and name (since R5 doesn't exist in white, we can rename it to R50 white or just edit the image)
    c.execute(
        "UPDATE items SET image = ?, name = ? WHERE name LIKE ?",
        (new_path, "Canon EOS R50 White Mirrorless", "%Canon EOS%"),
    )
    conn.commit()
    print(f"Updated Canon DB: {new_path}")
    conn.close()

# 2. Add new cameras
new_cameras = [
    {
        "name": "Sony Alpha a7 IV Mirrorless",
        "category": "cameras",
        "price": 250000.0,
        "search": "Sony Alpha a7 IV mirrorless camera product photo white background isolated",
        "filename": "sony-alpha-a7-iv-premium.jpg",
        "details": "33MP Full-Frame Exmor R CMOS Sensor. Up to 10 fps Shooting, ISO 100-51200. 4K 60p Video in 10-Bit",
    },
    {
        "name": "Nikon Z6 II Mirrorless",
        "category": "cameras",
        "price": 200000.0,
        "search": "Nikon Z6 II mirrorless camera product photo white background isolated",
        "filename": "nikon-z6-ii-premium.jpg",
        "details": "24.5MP FX-Format BSI CMOS Sensor. Dual EXPEED 6 Image Processors. UHD 4K30 Video",
    },
    {
        "name": "Fujifilm X-T5 Silver Mirrorless",
        "category": "cameras",
        "price": 170000.0,
        "search": "Fujifilm X-T5 mirrorless camera silver product photo white background isolated",
        "filename": "fujifilm-xt5-silver-premium.jpg",
        "details": "40.2MP APS-C X-Trans CMOS 5 HR Sensor. 4K 60p, 6.2K 30p, 4:2:2 10-Bit Video. 7-Stop In-Body Image Stabilization",
    },
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for cam in new_cameras:
    print(f"Searching: {cam['search']}")
    urls = search_bing_images(cam["search"])
    if download_best(urls, cam["filename"]):
        new_path = f"/static/uploads/{cam['filename']}"
        # insert into DB
        c.execute(
            "INSERT INTO items (name, price, category, image, details, stock) VALUES (?, ?, ?, ?, ?, ?)",
            (cam["name"], cam["price"], cam["category"], new_path, cam["details"], 10),
        )
        print(f"Added new camera: {cam['name']}")
    else:
        print(f"Failed to find image for {cam['name']}")

conn.commit()
conn.close()
print("Done!")
