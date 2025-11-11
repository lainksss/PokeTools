# It gets all the localized names for each Pokémon (from /pokemon-species endpoint).
# Exemple export (sample structure saved to data/all_pokemon_names_multilang.json):
# {
#   "bulbasaur": {
#     "en": "Bulbasaur",
#     "fr": "Bulbizarre",
#     "ja-Hrkt": "フシギダネ",
#     "de": "Bisasam",
#     "es": "Bulbasaur",
#     "it": "Bulbasaur"
#   },
#   "ivysaur": {
#     "en": "Ivysaur",
#     "fr": "Herbizarre",
#     "ja-Hrkt": "フシギソウ",
#     "de": "Bisaknosp",
#     "es": "Ivysaur"
#   }
# }
#
# The script fetches all Pokémon from /pokemon, then calls /pokemon-species/{id}
# to retrieve the translated names in all available languages.
# It saves the result as a JSON file in ./data/all_pokemon_names_multilang.json

import requests
import time
import json
from pathlib import Path

BASE = "https://pokeapi.co/api/v2"
POKEMON_ENDPOINT = f"{BASE}/pokemon?limit=100&offset=0"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "pokemon-names-multilang/1.0"})

def fetch_all_pokemon_urls():
    """Collect all Pokémon URLs from paginated /pokemon endpoint."""
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

def fetch_pokemon_names_in_all_languages(pokemon_url):
    """Fetch all localized Pokémon names from /pokemon-species endpoint."""
    species_url = pokemon_url.replace("/pokemon/", "/pokemon-species/")
    r = SESSION.get(species_url, timeout=15)
    # Some forms (like mega or gmax) don't have species data
    if r.status_code == 404:
        return None
    r.raise_for_status()
    data = r.json()
    names = {entry["language"]["name"]: entry["name"] for entry in data["names"]}
    return names

def build_all_pokemon_names(save_to="data/all_pokemon_names_multilang.json"):
    Path("data").mkdir(exist_ok=True)
    urls = fetch_all_pokemon_urls()
    print(f"Found {len(urls)} Pokémon. Fetching translations...")

    all_names = {}
    for i, url in enumerate(urls, start=1):
        name_key = url.split("/")[-2]
        try:
            translations = fetch_pokemon_names_in_all_languages(url)
        except Exception as e:
            print(f"[WARN] failed for {url}: {e}. Retrying once...")
            time.sleep(1)
            try:
                translations = fetch_pokemon_names_in_all_languages(url)
            except Exception as e2:
                print(f"[ERROR] Skipping {name_key} (still failed): {e2}")
                translations = None

        if translations is None:
            print(f"[SKIP] No species data for {name_key}")
        else:
            all_names[name_key] = translations

        if i % 50 == 0:
            print(f"  -> Processed {i}/{len(urls)} Pokémon")
        time.sleep(0.07)

    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(all_names, f, indent=2, ensure_ascii=False)
    print(f"Saved all Pokémon translations to {save_to}")

if __name__ == "__main__":
    build_all_pokemon_names()
