# pokemon_weight_height.py
# Fetches all Pokémon with their weight and height
#
# Example output (saved in data/all_pokemon_weight_height.json):
# {
#   "1": {
#     "weight_kg": 6.9,
#     "height_m": 0.7
#   },
#   "2": {
#     "weight_kg": 13.0,
#     "height_m": 1.0
#   },
#   "3": {
#     "weight_kg": 100.0,
#     "height_m": 2.0
#   }
# }

import requests
import time
import json
from pathlib import Path

BASE = "https://pokeapi.co/api/v2"
POKEMON_ENDPOINT = f"{BASE}/pokemon?limit=100&offset=0"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "pokemon-weight-height/1.0"})

def fetch_all_pokemon_urls():
    """Fetch all Pokémon URLs."""
    url = POKEMON_ENDPOINT
    urls = []
    while url:
        r = SESSION.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        urls.extend([p["url"] for p in data["results"]])
        url = data.get("next")
        time.sleep(0.1)
    return urls

def fetch_pokemon_weight_height(pokemon_url):
    """Fetch weight (kg) and height (m) of a Pokémon."""
    r = SESSION.get(pokemon_url, timeout=15)
    r.raise_for_status()
    data = r.json()
    weight_kg = data["weight"] / 10  # hectograms to kg
    height_m = data["height"] / 10   # decimeters to meters
    return weight_kg, height_m

def build_weight_height_json(save_to="data/all_pokemon_weight_height.json"):
    Path("data").mkdir(exist_ok=True)
    urls = fetch_all_pokemon_urls()
    print(f"Found {len(urls)} Pokémon. Fetching weight & height...")

    all_data = {}
    for i, url in enumerate(urls, start=1):
        try:
            weight, height = fetch_pokemon_weight_height(url)
        except Exception as e:
            print(f"[WARN] Failed for {url}: {e}. Retrying once...")
            time.sleep(1)
            weight, height = fetch_pokemon_weight_height(url)
        pokemon_id = url.rstrip("/").split("/")[-1]
        all_data[pokemon_id] = {
            "weight_kg": weight,
            "height_m": height
        }
        if i % 50 == 0:
            print(f"  -> Processed {i}/{len(urls)} Pokémon")
        time.sleep(0.07)

    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print(f"Saved weight & height for {len(all_data)} Pokémon to {save_to}")

if __name__ == "__main__":
    build_weight_height_json()
