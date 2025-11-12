# It gets all Pokémon abilities with all localized names and descriptions.
# Exemple export (sample structure saved to data/all_ability_translations.json):
# {
#   "strong-jaw": {
#     "names": {
#       "en": "Strong Jaw",
#       "fr": "Prognathe",
#       "ja-Hrkt": "がんじょうあご",
#       "de": "Titankiefer"
#     },
#     "descriptions": {
#       "en": "Boosts the power of biting moves.",
#       "fr": "Augmente la puissance des attaques de type morsure.",
#       "es": "Aumenta la potencia de los ataques de tipo mordisco.",
#       "ja-Hrkt": "かみつく こうげきの いりょくが あがる。"
#     }
#   },
#   ...
# }

import requests
import time
import json
from pathlib import Path

BASE = "https://pokeapi.co/api/v2"
ABILITY_ENDPOINT = f"{BASE}/ability?limit=200&offset=0"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "pokemon-ability-translations/1.0"})

def fetch_all_ability_urls():
    """Collect all ability URLs from paginated /ability endpoint."""
    url = ABILITY_ENDPOINT
    urls = []
    while url:
        r = SESSION.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        urls.extend([a["url"] for a in data["results"]])
        url = data.get("next")
        time.sleep(0.1)
    return urls

def fetch_ability_translations(ability_url):
    """Fetch all localized names and flavor texts for an ability."""
    r = SESSION.get(ability_url, timeout=15)
    r.raise_for_status()
    data = r.json()

    names = {entry["language"]["name"]: entry["name"] for entry in data["names"]}
    descriptions = {}

    # flavor_text_entries contains the translated descriptions
    for entry in data["flavor_text_entries"]:
        lang = entry["language"]["name"]
        text = entry["flavor_text"].replace("\n", " ").replace("\f", " ").strip()
        # Keep only one description per language (avoid duplicates across versions)
        if lang not in descriptions:
            descriptions[lang] = text

    return {"names": names, "descriptions": descriptions}

def build_all_ability_translations(save_to="data/all_ability_translations.json"):
    Path("data").mkdir(exist_ok=True)
    urls = fetch_all_ability_urls()
    print(f"Found {len(urls)} abilities. Fetching translations...")

    all_abilities = {}
    for i, url in enumerate(urls, start=1):
        ability_key = url.split("/")[-2]
        try:
            translations = fetch_ability_translations(url)
        except Exception as e:
            print(f"[WARN] failed for {url}: {e}. Retrying once...")
            time.sleep(1)
            try:
                translations = fetch_ability_translations(url)
            except Exception as e2:
                print(f"[ERROR] Skipping {ability_key}: {e2}")
                translations = None

        if translations:
            all_abilities[ability_key] = translations
        else:
            print(f"[SKIP] No data for {ability_key}")

        if i % 50 == 0:
            print(f"  -> Processed {i}/{len(urls)} abilities")
        time.sleep(0.07)

    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(all_abilities, f, indent=2, ensure_ascii=False)
    print(f"Saved all ability translations to {save_to}")

if __name__ == "__main__":
    build_all_ability_translations()
