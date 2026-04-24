import sqlite3
import requests
import os
import re

# Configuration
DB_PATH = r"c:\Users\sammy\OneDrive\Desktop\electronics e commerce\app\test.db"
UPLOADS_DIR = r"c:\Users\sammy\OneDrive\Desktop\electronics e commerce\app\static\uploads"

products_data = [
  {
    "name": "Philips Airfryer XXL XXL Digital",
    "image_url": "https://us.home-appliances.philips/cdn/shop/files/HD9867_16_00_hero_image.jpg?v=1765209118&width=2000"
  },
  {
    "name": "Xiaomi Redmi Note 13 Pro 5G",
    "image_url": "https://i01.appmifile.com/v1/MI_18455B3E4DA706226CF7535A58E875F0267/pms_1703056094.01524823.png"
  },
  {
    "name": "Sony 65 Bravia X75K 4K Hdr Led",
    "image_url": "https://m.media-amazon.com/images/I/81vXwYV3uXL.jpg"
  },
  {
    "name": "Infinix Note 40 Pro 5G",
    "image_url": "https://infinixmobility.com/storage/product/note-40-pro-5g/white-bg.png"
  },
  {
    "name": "Hisense 55 U7H Uled 4K Smart Tv",
    "image_url": "https://hisense-usa.com/wp-content/uploads/2022/04/55U7H_Hero_White_Background.png"
  },
  {
    "name": "Dell Xps 13 Plus 13Th Gen I7",
    "image_url": "https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/dell-client-computing/notebooks/xps-notebooks/xps-13-9320/media-gallery/laptop-xps-13-9320-white-gallery-1.psd?fmt=png-alpha&wid=1000&hei=1000"
  },
  {
    "name": "Asus Zenbook 14 Oled Ux3402",
    "image_url": "https://dlcdnwebimgs.asus.com/gain/3D70E9F9-7B1A-4C2E-B9F0-7350713344BB/w1000/h1000"
  },
  {
    "name": "Lenovo ThinkPad X1 Carbon Gen 11",
    "image_url": "https://p1-ofp.static.pub/medias/25446059555_X1_Carbon_G11_202211301041151671201509148.png"
  },
  {
    "name": "HP Pavilion 15 (Ryzen 7 7730U)",
    "image_url": "https://ssl-product-images.www8.hp.com/c08477610_1750x1285.png"
  },
  {
    "name": "HP Spectre x360 14 (Core Ultra 7)",
    "image_url": "https://ssl-product-images.www8.hp.com/c08920151_1750x1285.png"
  },
  {
    "name": "Samsung Galaxy A55 5G (8GB/256GB)",
    "image_url": "https://images.samsung.com/is/image/samsung/p6pim/in/sm-a556elbzins/gallery/in-galaxy-a55-5g-sm-a556-sm-a556elbzins-540328905?$650_519_PNG$"
  },
  {
    "name": "Samsung Galaxy S23 FE (8GB/256GB)",
    "image_url": "https://images.samsung.com/is/image/samsung/p6pim/in/sm-s711blgdeub/gallery/in-galaxy-s23-fe-sm-s711-sm-s711blgdeub-thumb-538356193?$650_519_PNG$"
  }
]

def slugify(text):
    return re.sub(r'[^a-zA-Z0-9]', '-', text.lower()).strip('-')

def download_image(url, filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            file_path = os.path.join(UPLOADS_DIR, filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"Failed to download {url}: Status {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return False

def update_db():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for item in products_data:
        name = item['name']
        url = item['image_url']
        
        # Determine extension from URL or fallback to .png
        if '.jpg' in url.lower() or '.jpeg' in url.lower():
            ext = '.jpg'
        elif '.webp' in url.lower():
            ext = '.webp'
        else:
            ext = '.png'
            
        filename = f"{slugify(name)}-premium{ext}"
        
        print(f"Processing: {name}...")
        if download_image(url, filename):
            new_path = f"/static/uploads/{filename}"
            cursor.execute("UPDATE items SET image = ? WHERE name LIKE ?", (new_path, f"%{name}%"))
            if cursor.rowcount > 0:
                print(f"  SUCCESS: Updated DB with {new_path}")
            else:
                print(f"  WARNING: Item '{name}' not found in DB to update.")
        else:
            print(f"  FAILED to download image for '{name}'")

    conn.commit()
    conn.close()
    print("Database update complete.")

if __name__ == "__main__":
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)
    update_db()
