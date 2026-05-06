import re
from pathlib import Path
from urllib.parse import urlparse

import requests
from werkzeug.utils import secure_filename
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app import app
from app.db_models import db, Item


BASE_UPLOAD_DIR = Path(app.root_path) / "static" / "uploads"
BASE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def slugify(value: str) -> str:
    value = secure_filename(value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "item"


def data_label_from_slug(slug: str) -> str:
    words = slug.replace("-", " ").title()
    if len(words) <= 28:
        return words
    shortened = []
    total = 0
    for word in words.split():
        if total + len(word) + (1 if shortened else 0) > 28:
            break
        shortened.append(word)
        total += len(word) + (1 if shortened else 0)
    return " ".join(shortened) or "Product"


def download_image(image_url: str, slug: str) -> str:
    if image_url.startswith("/static/"):
        return image_url

    parsed = urlparse(image_url)
    ext = Path(parsed.path).suffix
    if ext.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        ext = ".jpg"
    filename = f"{slug}{ext}"
    destination = BASE_UPLOAD_DIR / filename
    if not destination.exists():
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            destination.write_bytes(response.content)
        except Exception as exc:  # noqa: BLE001 - debugging helper
            print(f"Warning: failed to download {image_url} ({exc})")
            placeholder_name = f"{slug}-placeholder.svg"
            placeholder_path = BASE_UPLOAD_DIR / placeholder_name
            if not placeholder_path.exists():
                text = data_label_from_slug(slug)
                svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='600' height='600'>
<rect width='600' height='600' fill='#0d6efd'/>
<text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='#ffffff' font-family='Arial, sans-serif' font-size='36' font-weight='bold'>{text}</text>
</svg>
"""
                placeholder_path.write_text(svg, encoding="utf-8")
            return f"/static/uploads/{placeholder_name}"
    return f"/static/uploads/{filename}"


import random

NEW_ITEMS = [
    # Smartphones
    {
        "name": "Samsung Galaxy S23 FE (8GB/256GB)",
        "price": 49999,
        "category": "Smartphone",
        "stock": 18,
        "image_url": "/static/uploads/samsung-galaxy-s23-fe-8gb-256gb-real3.png",
        "details": "Official Samsung Kenya warranty, 8GB RAM, 50MP triple camera, 4500mAh battery.",
    },
    {
        "name": "Samsung Galaxy A55 5G (8GB/256GB)",
        "price": 37999,
        "category": "Smartphone",
        "stock": 27,
        "image_url": "/static/uploads/samsung-galaxy-a55-5g-8gb-256gb-real3.png",
        "details": "Super AMOLED 120Hz display, Exynos 1480, 5000mAh battery, IP67 rated.",
    },
    {
        "name": "Tecno Phantom X2 Pro (12GB/256GB)",
        "price": 48999,
        "category": "Smartphone",
        "stock": 14,
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=800&auto=format&fit=crop",
        "details": "Flagship Dimensity 9000, retractable portrait lens, 5160mAh battery.",
    },
    # Laptops
    {
        "name": "HP Spectre x360 14 (Core Ultra 7)",
        "price": 98000,
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1544006659-f0b21f04cb1d?q=80&w=800&auto=format&fit=crop",
        "details": '14" 2.8K OLED touchscreen, Intel Core Ultra 7, 16GB LPDDR5, 1TB SSD, pen included.',
        "stock": random.randint(5, 25),
    },
    {
        "name": "HP Pavilion 15 (Ryzen 7 7730U)",
        "price": 62000,
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1588872674355-6b4246ed5088?q=80&w=800&auto=format&fit=crop",
        "details": '15.6" FHD IPS, 16GB RAM, 512GB SSD, Windows 11 Home.',
        "stock": random.randint(5, 25),
    },
    {
        "name": "Lenovo ThinkPad X1 Carbon Gen 11",
        "price": 95000,
        "category": "laptop",
        "image_url": "/static/uploads/lenovo-thinkpad-x1-carbon-gen-11-real3.png",
        "details": 'Intel Core i7 vPro, 16GB RAM, 1TB SSD, 14" 2.8K display.',
        "stock": random.randint(5, 25),
    },
    {
        "name": "Lenovo IdeaPad Flex 5 (Ryzen 5 7530U)",
        "price": 55000,
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?q=80&w=800&auto=format&fit=crop",
        "details": "Convertible 2-in-1 design, 16GB RAM, 512GB SSD, touchscreen.",
        "stock": random.randint(5, 25),
    },
    # Televisions
    {
        "name": 'Samsung 55" QLED Q60C Smart TV',
        "price": 107999,
        "category": "Television",
        "image_url": "/static/uploads/samsung-55-qled-q60c-smart-tv-real3.png",
        "details": "4K UHD Quantum Processor Lite, Smart Hub.",
        "stock": 4,
    },
    {
        "name": 'Samsung 65" Crystal UHD BU8000',
        "price": 126999,
        "category": "Television",
        "image_url": "/static/uploads/samsung-65-crystal-uhd-bu8000-real3.png",
        "details": "AirSlim design, Crystal Processor 4K.",
        "stock": 3,
    },
    {
        "name": 'TCL 65" P745 4K HDR Google TV',
        "price": 97999,
        "category": "Television",
        "image_url": "/static/uploads/tcl-65-p745-4k-hdr-google-tv-real3.png",
        "details": "Wide Color Gamut, Dolby Atmos sound.",
        "stock": 11,
    },
    {
        "name": "Acer Swift Go 14 Intel Core Ultra 5",
        "price": 77533.0,
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?q=80&w=800&auto=format&fit=crop",
        "details": "High quality laptop - Acer Swift Go 14 Intel Core Ultra 5",
        "stock": 12,
        "price_id": "local-acer-swift-go-14-intel-core-ultra-5",
    },
    {
        "name": "Apple Macbook Air 13 M2 8Gb 256Gb",
        "price": 158578.0,
        "category": "laptop",
        "image_url": "/static/uploads/apple-macbook-air-13-m2-8gb-256gb-real3.jpg",
        "details": "High quality laptop - Apple Macbook Air 13 M2 8Gb 256Gb",
        "stock": 14,
        "price_id": "local-apple-macbook-air-13-m2-8gb-256gb",
    },
    {
        "name": "Asus Tuf Gaming A15 Ryzen 7 Rtx 4060",
        "price": 172685.0,
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?q=80&w=800&auto=format&fit=crop",
        "details": "High quality laptop - Asus Tuf Gaming A15 Ryzen 7 Rtx 4060",
        "stock": 18,
        "price_id": "local-asus-tuf-gaming-a15-ryzen-7-rtx-4060",
    },
    {
        "name": "Asus Zenbook 14 Oled Ux3402",
        "price": 191274.0,
        "category": "Television",
        "image_url": "https://images.unsplash.com/photo-1525598912003-663126343e1f?q=80&w=800&auto=format&fit=crop",
        "details": "High quality television - Asus Zenbook 14 Oled Ux3402",
        "stock": 14,
        "price_id": "local-asus-zenbook-14-oled-ux3402",
    },
    {
        "name": "Dell Inspiron 15 3520 Core I5",
        "price": 148625.0,
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?q=80&w=800&auto=format&fit=crop",
        "details": "High quality laptop - Dell Inspiron 15 3520 Core I5",
        "stock": 7,
        "price_id": "local-dell-inspiron-15-3520-core-i5",
    },
    {
        "name": "Dell Xps 13 Plus 13Th Gen I7",
        "price": 68542.0,
        "category": "laptop",
        "image_url": "/static/uploads/dell-xps-13-plus-13th-gen-i7-real3.png",
        "details": "High quality laptop - Dell Xps 13 Plus 13Th Gen I7",
        "stock": 9,
        "price_id": "local-dell-xps-13-plus-13th-gen-i7",
    },
    {
        "name": "Gaming 5000X3125",
        "price": 162776.0,
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=800&auto=format&fit=crop",
        "details": "High quality laptop - Gaming 5000X3125",
        "stock": 16,
        "price_id": "local-Gaming_5000x3125",
    },
    {
        "name": "Hisense 55 U7H Uled 4K Smart Tv",
        "price": 152990.0,
        "category": "Television",
        "image_url": "/static/uploads/hisense-55-u7h-uled-4k-smart-tv-real3.png",
        "details": "High quality television - Hisense 55 U7H Uled 4K Smart Tv",
        "stock": 11,
        "price_id": "local-hisense-55-u7h-uled-4k-smart-tv",
    },
    {
        "name": "Hisense 65 A6H 4K Uhd Smart Tv",
        "price": 76644.0,
        "category": "Television",
        "image_url": "/static/uploads/hisense-65-a6h-4k-uhd-smart-tv-real3.jpg",
        "details": "High quality television - Hisense 65 A6H 4K Uhd Smart Tv",
        "stock": 23,
        "price_id": "local-hisense-65-a6h-4k-uhd-smart-tv",
    },
    {
        "name": "Infinix Note 40 Pro 5G",
        "price": 72117.0,
        "category": "Smartphone",
        "image_url": "/static/uploads/infinix-note-40-pro-5g-real3.png",
        "details": "High quality smartphone - Infinix Note 40 Pro 5G",
        "stock": 22,
        "price_id": "local-infinix-note-40-pro-5g",
    },
    {
        "name": "Infinix Zero 30 5G 12Gb 256Gb",
        "price": 43907.0,
        "category": "Smartphone",
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=800&auto=format&fit=crop",
        "details": "High quality smartphone - Infinix Zero 30 5G 12Gb 256Gb",
        "stock": 17,
        "price_id": "local-infinix-zero-30-5g-12gb-256gb",
    },
    {
        "name": "Lg 55 C3 Evo Oled 4K Tv",
        "price": 168016.0,
        "category": "Television",
        "image_url": "/static/uploads/lg-55-c3-evo-oled-4k-tv-real3.jpg",
        "details": "High quality television - Lg 55 C3 Evo Oled 4K Tv",
        "stock": 5,
        "price_id": "local-lg-55-c3-evo-oled-4k-tv",
    },
    {
        "name": "Lg 65 Nanocell 4K Nano77 Series",
        "price": 110363.0,
        "category": "Television",
        "image_url": "/static/uploads/lg-65-nanocell-4k-nano77-series-real3.jpg",
        "details": "High quality television - Lg 65 Nanocell 4K Nano77 Series",
        "stock": 8,
        "price_id": "local-lg-65-nanocell-4k-nano77-series",
    },
    {
        "name": "Mac",
        "price": 103164.0,
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?q=80&w=800&auto=format&fit=crop",
        "details": "High quality laptop - Mac",
        "stock": 6,
        "price_id": "local-mac",
    },
    {
        "name": "Macbook",
        "price": 86832.0,
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1629131726692-1accd0c53ce0?q=80&w=800&auto=format&fit=crop",
        "details": "High quality laptop - Macbook",
        "stock": 11,
        "price_id": "local-macbook",
    },
    {
        "name": "Mi Tv",
        "price": 106744.0,
        "category": "Television",
        "image_url": "https://images.unsplash.com/photo-1509281373149-e957c6296406?q=80&w=800&auto=format&fit=crop",
        "details": "High quality television - Mi Tv",
        "stock": 16,
        "price_id": "local-mi tv",
    },
    {
        "name": "Nitro",
        "price": 60893.0,
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?q=80&w=800&auto=format&fit=crop",
        "details": "High quality laptop - Nitro",
        "stock": 22,
        "price_id": "local-nitro",
    },
    {
        "name": "Oppo A79 5G 8Gb 256Gb",
        "price": 20060.0,
        "category": "Smartphone",
        "image_url": "https://images.unsplash.com/photo-1556656793-062ff98782ee?q=80&w=800&auto=format&fit=crop",
        "details": "High quality smartphone - Oppo A79 5G 8Gb 256Gb",
        "stock": 16,
        "price_id": "local-oppo-a79-5g-8gb-256gb",
    },
    {
        "name": "Oppo Reno11 Pro 5G 12Gb 512Gb",
        "price": 42122.0,
        "category": "Smartphone",
        "image_url": "https://images.unsplash.com/photo-1592890288564-76628a30a657?q=80&w=800&auto=format&fit=crop",
        "details": "High quality smartphone - Oppo Reno11 Pro 5G 12Gb 512Gb",
        "stock": 16,
        "price_id": "local-oppo-reno11-pro-5g-12gb-512gb",
    },
    {
        "name": "Sony 55 Bravia Xr A80L Oled",
        "price": 155766.0,
        "category": "Television",
        "image_url": "/static/uploads/sony-55-bravia-xr-a80l-oled-real3.png",
        "details": "High quality television - Sony 55 Bravia Xr A80L Oled",
        "stock": 20,
        "price_id": "local-sony-55-bravia-xr-a80l-oled",
    },
    {
        "name": "Sony 65 Bravia X75K 4K Hdr Led",
        "price": 29634.0,
        "category": "Television",
        "image_url": "/static/uploads/sony-65-bravia-x75k-4k-hdr-led-real3.png",
        "details": "High quality television - Sony 65 Bravia X75K 4K Hdr Led",
        "stock": 23,
        "price_id": "local-sony-65-bravia-x75k-4k-hdr-led",
    },
    {
        "name": "Tcl 55 C755 Qd Mini Led Tv",
        "price": 51689.0,
        "category": "Television",
        "image_url": "/static/uploads/tcl-55-c755-qd-mini-led-tv-real3.png",
        "details": "High quality television - Tcl 55 C755 Qd Mini Led Tv",
        "stock": 7,
        "price_id": "local-tcl-55-c755-qd-mini-led-tv",
    },
    {
        "name": "Tecno Camon 30 Premier 5G",
        "price": 44213.0,
        "category": "Smartphone",
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=800&auto=format&fit=crop",
        "details": "High quality smartphone - Tecno Camon 30 Premier 5G",
        "stock": 13,
        "price_id": "local-tecno-camon-30-premier-5g",
    },
    {
        "name": "Xiaomi Redmi 13C 6Gb 128Gb",
        "price": 73289.0,
        "category": "Smartphone",
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=800&auto=format&fit=crop",
        "details": "High quality smartphone - Xiaomi Redmi 13C 6Gb 128Gb",
        "stock": 25,
        "price_id": "local-xiaomi-redmi-13c-6gb-128gb",
    },
    {
        "name": "Xiaomi Redmi 13C 6Gb 128Gb",
        "price": 73692.0,
        "category": "Smartphone",
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=800&auto=format&fit=crop",
        "details": "High quality smartphone - Xiaomi Redmi 13C 6Gb 128Gb",
        "stock": 11,
        "price_id": "local-xiaomi-redmi-13c-6gb-128gb",
    },
    {
        "name": "Xiaomi Redmi Note 13 Pro 5G",
        "price": 79132.0,
        "category": "Smartphone",
        "image_url": "/static/uploads/xiaomi-redmi-note-13-pro-5g-real3.png",
        "details": "High quality smartphone - Xiaomi Redmi Note 13 Pro 5G",
        "stock": 12,
        "price_id": "local-xiaomi-redmi-note-13-pro-5g",
    },
    {
        "name": "Xiaomi Redmi Note 13 Pro 5G",
        "price": 31107.0,
        "category": "Smartphone",
        "image_url": "/static/uploads/xiaomi-redmi-note-13-pro-5g-real3.png",
        "details": "High quality smartphone - Xiaomi Redmi Note 13 Pro 5G",
        "stock": 16,
        "price_id": "local-xiaomi-redmi-note-13-pro-5g",
    },
    {
        "name": "Nutribullet NB9-1212 high-Speed Blender",
        "price": 14500.0,
        "category": "Appliances",
        "image_url": "/static/uploads/nutribullet-nb9-1212-high-speed-blender-real3.png",
        "details": "High-speed personal blender with 900W motor, perfect for smoothies and nutrient extraction.",
        "stock": 35,
        "price_id": "local-nutribullet-blender",
    },
]


def seed():
    created = 0
    updated = 0

    with app.app_context():
        for data in NEW_ITEMS:
            slug = slugify(data["name"])
            price_id = data.get("price_id") or f"local-{slug}"

            image_url = data["image_url"]
            image_path = download_image(image_url, slug)

            payload = {
                "name": data["name"],
                "price": data["price"],
                "category": data["category"],
                "image": image_path,
                "details": data["details"],
                "price_id": price_id,
                "stock": data.get("stock", random.randint(5, 25)),
            }

            exists = Item.query.filter_by(name=data["name"]).first()

            if exists:
                changed = False
                for key, value in payload.items():
                    if getattr(exists, key) != value:
                        setattr(exists, key, value)
                        changed = True

                if changed:
                    updated += 1
            else:
                item = Item(**payload)
                db.session.add(item)
                created += 1

        if created or updated:
            db.session.commit()

    return created, updated


if __name__ == "__main__":
    added, updated = seed()
    print(f"Added {added} new items.")
    print(f"Updated {updated} existing items.")
