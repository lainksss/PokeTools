# It gets all the localized names for each Pokémon move (from /move endpoint).
# Exemple export (sample structure saved to data/all_move_names_multilang.json):
# {
#   "tackle": {
#     "en": "Tackle",
#     "fr": "Charge",
#     "ja-Hrkt": "たいあたり",
#     "de": "Tackle"
#   },
#   "vine-whip": {
#     "en": "Vine Whip",
#     "fr": "Fouet Lianes",
#     "ja-Hrkt": "つるのムチ"
#   }
# }

import requests
import time
import json
from pathlib import Path

BASE = "https://pokeapi.co/api/v2"
MOVE_ENDPOINT = f"{BASE}/move?limit=200&offset=0"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "pokemon-move-names-multilang/1.0"})

def fetch_all_move_urls():
    """Collect all move URLs from paginated /move endpoint."""
    url = MOVE_ENDPOINT
    urls = []
    while url:
        r = SESSION.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        urls.extend([m["url"] for m in data["results"]])
        url = data.get("next")
        time.sleep(0.1)
    return urls

def fetch_move_names_in_all_languages(move_url):
    """Fetch all localized move names."""
    r = SESSION.get(move_url, timeout=15)
    r.raise_for_status()
    data = r.json()
    return {entry["language"]["name"]: entry["name"] for entry in data["names"]}

def build_all_move_names(save_to="data/all_move_names_multilang.json"):
    Path("data").mkdir(exist_ok=True)
    urls = fetch_all_move_urls()
    print(f"Found {len(urls)} moves. Fetching translations...")

    all_moves = {}
    for i, url in enumerate(urls, start=1):
        move_key = url.split("/")[-2]
        try:
            names = fetch_move_names_in_all_languages(url)
        except Exception as e:
            print(f"[WARN] failed for {url}: {e}. Retrying once...")
            time.sleep(1)
            try:
                names = fetch_move_names_in_all_languages(url)
            except Exception as e2:
                print(f"[ERROR] Skipping {move_key}: {e2}")
                names = None

        if names:
            all_moves[move_key] = names
        else:
            print(f"[SKIP] No data for {move_key}")

        if i % 50 == 0:
            print(f"  -> Processed {i}/{len(urls)} moves")
        time.sleep(0.07)

    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(all_moves, f, indent=2, ensure_ascii=False)
    print(f"Saved all move translations to {save_to}")

if __name__ == "__main__":
    build_all_move_names()
