import requests
import re
import urllib.parse
import json


def search_bing_images(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}"
    response = requests.get(url, headers=headers)

    # Extract murl from the raw HTML
    murls = re.findall(r"murl&quot;:&quot;(.*?)&quot;", response.text)
    return murls[:3]


products = [
    "Sony 65 Bravia X75K 4K Hdr Led",
    "Infinix Note 40 Pro 5G",
    "Hisense 55 U7H Uled 4K Smart Tv",
    "Dell Xps 13 Plus 13Th Gen I7",
    "Lenovo ThinkPad X1 Carbon Gen 11",
    "HP Pavilion 15 Ryzen 7 7730U",
    "HP Spectre x360 14 Core Ultra 7",
    "Samsung Galaxy A55 5G",
    "Samsung Galaxy S23 FE",
]

results = {}
for p in products:
    print(f"Searching for {p}...")
    urls = search_bing_images(p + " transparent background white")
    results[p] = urls
    print(urls)

with open("scratch/found_images.json", "w") as f:
    json.dump(results, f, indent=2)
