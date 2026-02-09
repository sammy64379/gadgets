import re
from pathlib import Path
from urllib.parse import urlparse

import requests
from werkzeug.utils import secure_filename

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


NEW_ITEMS = [
    # Smartphones
    {
        "name": "Samsung Galaxy S23 FE (8GB/256GB)",
        "price": 49999,
        "category": "Apple",
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "details": "Official Samsung Kenya warranty, 8GB RAM, 50MP triple camera, 4500mAh battery.",
    },
    {
        "name": "Samsung Galaxy A55 5G (8GB/256GB)",
        "price": 37999,
        "category": "Apple",
        "image_url": "https://images.pexels.com/photos/607812/pexels-photo-607812.jpeg?auto=compress&cs=tinysrgb&w=800",
        "details": "Super AMOLED 120Hz display, Exynos 1480, 5000mAh battery, IP67 rated.",
    },
    {
        "name": "Tecno Phantom X2 Pro (12GB/256GB)",
        "price": 48999,
        "category": "Apple",
        "image_url": "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "details": "Flagship Dimensity 9000, retractable portrait lens, 5160mAh battery, 45W fast charge.",
    },
    {
        "name": "Tecno Camon 30 Premier 5G",
        "price": 45999,
        "category": "Apple",
        "image_url": "https://images.pexels.com/photos/404280/pexels-photo-404280.jpeg?auto=compress&cs=tinysrgb&w=800",
        "details": "Sony IMX890 sensor, 120Hz LTPO AMOLED, 70W Ultra Charge, vegan leather back.",
    },
    {
        "name": "Infinix Zero 30 5G (12GB/256GB)",
        "price": 42999,
        "category": "Apple",
        "image_url": "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "details": "4K 60fps front camera, curved 144Hz AMOLED display, 68W fast charging.",
    },
    {
        "name": "Infinix Note 40 Pro 5G",
        "price": 40999,
        "category": "Apple",
        "image_url": "https://images.unsplash.com/photo-1511376777868-611b54f68947?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "details": "MagCharge wireless kit, 120Hz AMOLED, Dimensity 7020 5G chipset.",
    },
    {
        "name": "OPPO Reno11 Pro 5G (12GB/512GB)",
        "price": 49999,
        "category": "Apple",
        "image_url": "https://images.unsplash.com/photo-1470246973918-29a93221c455?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "details": "Portrait Expert Engine, 80W SUPERVOOC charge, 1.5K curved screen.",
    },
    {
        "name": "Xiaomi Redmi 13C (6GB/128GB)",
        "price": 14999,
        "category": "Apple",
        "image_url": "https://images.pexels.com/photos/1092644/pexels-photo-1092644.jpeg?auto=compress&cs=tinysrgb&w=800",
        "details": "Affordable 90Hz display, 50MP AI camera, 5000mAh battery with Type-C fast charge.",
    },
    # Laptops
    {
        "name": "HP Spectre x360 14 (Core Ultra 7)",
        "price": 98000,
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1517430816045-df4b7de11d1d?ixlib=rb-4.0.3&auto=format&fit=crop&w=900&q=80",
        "details": "14\" 2.8K OLED touchscreen, Intel Core Ultra 7, 16GB LPDDR5, 1TB SSD, pen included.",
    },
    {
        "name": "HP Pavilion 15 (Ryzen 7 7730U)",
        "price": 62000,
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1516251193007-45ef944ab0c6?ixlib=rb-4.0.3&auto=format&fit=crop&w=900&q=80",
        "details": "15.6\" FHD IPS, 16GB RAM, 512GB SSD, backlit keyboard, Windows 11 Home.",
    },
    {
        "name": "Lenovo ThinkPad X1 Carbon Gen 11",
        "price": 95000,
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?ixlib=rb-4.0.3&auto=format&fit=crop&w=900&q=80",
        "details": "Intel Core i7 vPro, 16GB RAM, 1TB SSD, 14\" 2.8K display, MIL-STD durability.",
    },
    {
        "name": "Lenovo IdeaPad Flex 5 (Ryzen 5 7530U)",
        "price": 55000,
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?ixlib=rb-4.0.3&auto=format&fit=crop&w=900&q=80",
        "details": "Convertible 2-in-1 design, 16GB RAM, 512GB SSD, digital pen support, 14\" touchscreen.",
    },
    {
        "name": "Dell XPS 13 Plus (13th Gen i7)",
        "price": 99000,
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1485988412941-77a35537dae4?ixlib=rb-4.0.3&auto=format&fit=crop&w=900&q=80",
        "details": "InfinityEdge OLED display, 32GB RAM, 1TB SSD, edge-to-edge touch haptic trackpad.",
    },
    {
        "name": "Dell Inspiron 15 3520 (Core i5)",
        "price": 58000,
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1457305237443-44c3d5a30b89?ixlib=rb-4.0.3&auto=format&fit=crop&w=900&q=80",
        "details": "12th Gen Intel Core i5, 8GB RAM, 512GB SSD, numeric keypad, Windows 11 Home.",
    },
    {
        "name": "Acer Swift Go 14 (Intel Core Ultra 5)",
        "price": 42000,
        "category": "laptop",
        "image_url": "https://images.pexels.com/photos/18105/pexels-photo.jpg?auto=compress&cs=tinysrgb&w=900",
        "details": "Intel Core Ultra AI PC, 16GB LPDDR5X, 512GB SSD, 2.8K OLED display, Wi-Fi 6E.",
    },
    {
        "name": "Apple MacBook Air 13 M2 (8GB/256GB)",
        "price": 184999,
        "category": "laptop",
        "image_url": "https://images.unsplash.com/photo-1529333166437-7750a6dd5a70?ixlib=rb-4.0.3&auto=format&fit=crop&w=900&q=80",
        "details": "M2 chip, 13.6\" Liquid Retina display, 18-hour battery, fanless design, 30W USB-C charger.",
    },
    # Televisions
    {
        "name": "Samsung 55\" QLED Q60C Smart TV",
        "price": 107999,
        "category": "Television",
        "image_url": "https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
        "details": "4K UHD Quantum Processor Lite, Dual LED backlight, Smart Hub with built-in Alexa.",
    },
    {
        "name": "Samsung 65\" Crystal UHD BU8000",
        "price": 126999,
        "category": "Television",
        "image_url": "https://images.unsplash.com/photo-1522069394066-326005dc26b2?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
        "details": "AirSlim design, Crystal Processor 4K, built-in voice assistants, PC on TV feature.",
    },
    {
        "name": "LG 55\" C3 evo OLED 4K TV",
        "price": 189999,
        "category": "Television",
        "image_url": "https://images.unsplash.com/photo-1489515217757-5fd1be406fef?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
        "details": "α9 AI Processor 4K Gen6, Dolby Vision & Atmos, webOS 23 with ThinQ AI.",
    },
    {
        "name": "LG 65\" NanoCell 4K NANO77 Series",
        "price": 154999,
        "category": "Television",
        "image_url": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
        "details": "Pure colours with NanoCell, HDR10 Pro, Game Optimizer, Google Assistant built-in.",
    },
    {
        "name": "Sony 55\" Bravia XR A80L OLED",
        "price": 224999,
        "category": "Television",
        "image_url": "https://images.unsplash.com/photo-1523475472560-d2df97ec485c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
        "details": "Cognitive Processor XR, Acoustic Surface Audio+, Google TV, PS5 perfect paired features.",
    },
    {
        "name": "Sony 65\" Bravia X75K 4K HDR LED",
        "price": 164999,
        "category": "Television",
        "image_url": "https://images.unsplash.com/photo-1505691938895-1758d7feb511?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
        "details": "4K Processor X1, Motionflow XR, Google Assistant voice control, Chromecast built-in.",
    },
    {
        "name": "Hisense 55\" U7H ULED 4K Smart TV",
        "price": 93999,
        "category": "Television",
        "image_url": "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
        "details": "Quantum ULED, 120Hz native panel, Dolby Vision IQ & Atmos, Game Mode Pro.",
    },
    {
        "name": "Hisense 65\" A6H 4K UHD Smart TV",
        "price": 86999,
        "category": "Television",
        "image_url": "https://images.unsplash.com/photo-1484704849700-f032a568e944?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
        "details": "Dolby Vision HDR, Google TV platform, 3 HDMI 2.1 ports, DTS Virtual:X audio.",
    },
    {
        "name": "TCL 55\" C755 QD-Mini LED TV",
        "price": 99999,
        "category": "Television",
        "image_url": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
        "details": "144Hz Game Accelerator, Dolby Vision IQ, ONKYO 2.1 Hi-Fi audio, Google TV.",
    },
    {
        "name": "TCL 65\" P745 4K HDR Google TV",
        "price": 97999,
        "category": "Television",
        "image_url": "https://images.unsplash.com/photo-1517048676732-d65bc937f952?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
        "details": "Wide Color Gamut, MEMC motion, Hands-free voice control, Dolby Atmos sound.",
    },
]


def seed():
    created = 0
    updated = 0
    with app.app_context():
        for data in NEW_ITEMS:
            slug = slugify(data["name"])
            price_id = data.get("price_id") or f"local-{slug}"
            image_url = data.pop("image_url")
            image_path = download_image(image_url, slug)
            payload = {
                "name": data["name"],
                "price": data["price"],
                "category": data["category"],
                "image": image_path,
                "details": data["details"],
                "price_id": price_id,
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

