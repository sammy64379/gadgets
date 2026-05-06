import sqlite3
import requests
import os
import re
import json

DB_PATH = r"c:\Users\sammy\OneDrive\Desktop\electronics e commerce\app\test.db"
UPLOADS_DIR = (
    r"c:\Users\sammy\OneDrive\Desktop\electronics e commerce\app\static\uploads"
)


def slugify(text):
    return re.sub(r"[^a-zA-Z0-9]", "-", text.lower()).strip("-")


def download_image(urls, filename):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    }
    for url in urls:
        # cleanup some bing artifacting
        url = url.replace("&amp;", "&")
        print(f"  Trying {url}...")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                if "text/html" in response.headers.get("Content-Type", ""):
                    print("  Skipping, returned HTML.")
                    continue
                file_path = os.path.join(UPLOADS_DIR, filename)
                with open(file_path, "wb") as f:
                    f.write(response.content)
                return True
            else:
                print(f"  Failed: Status {response.status_code}")
        except Exception as e:
            print(f"  Error: {e}")
    return False


def update_db():
    with open("scratch/found_images.json", "r") as f:
        data = json.load(f)

    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for name, urls in data.items():
        # Ensure we keep the name exactly as we searched for it if we truncated it
        search_name = name
        if "Ryzen" in name:
            search_name = "HP Pavilion 15 (Ryzen 7 7730U)"
        elif "Core Ultra 7" in name:
            search_name = "HP Spectre x360 14 (Core Ultra 7)"
        elif "Samsung Galaxy A55 5G" == name:
            search_name = "Samsung Galaxy A55 5G (8GB/256GB)"
        elif "Samsung Galaxy S23 FE" == name:
            search_name = "Samsung Galaxy S23 FE (8GB/256GB)"

        ext = ".jpg"
        for url in urls:
            if ".png" in url.lower():
                ext = ".png"
            if ".webp" in url.lower():
                ext = ".webp"

        filename = f"{slugify(search_name)}-premium{ext}"

        print(f"Processing: {search_name}...")
        if download_image(urls, filename):
            new_path = f"/static/uploads/{filename}"
            # Need to find actual item name to use the LIKE clause safely
            # Let's fetch original name to match DB
            cursor.execute(
                "SELECT name FROM items WHERE name LIKE ? or name LIKE ?",
                (f"%{search_name}%", f"%{name}%"),
            )
            row = cursor.fetchone()
            if row:
                actual_name = row[0]
                cursor.execute(
                    "UPDATE items SET image = ? WHERE name = ?", (new_path, actual_name)
                )
                if cursor.rowcount > 0:
                    print(f"  SUCCESS: Updated DB with {new_path}")
            else:
                print(
                    f"  WARNING: Item '{search_name}' or '{name}' not found in DB to update."
                )
        else:
            print(f"  FAILED to download image for '{search_name}'")

    conn.commit()
    conn.close()
    print("Database update complete.")


if __name__ == "__main__":
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)
    update_db()
