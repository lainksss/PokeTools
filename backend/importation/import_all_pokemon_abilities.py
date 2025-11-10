# Fetch all Pokémon abilities and save a compact JSON file.

# Notes:
#  - The script paginates through the PokéAPI `pokemon` endpoint and requests
#    each Pokémon entry to read the `abilities` field.
#  - A small sleep between requests reduces the risk of being rate-limited.

# Example (excerpt of the saved file `data/all_pokemon_abilities.json`):

# {
#   "1": [
#     "overgrow",
#     "chlorophyll"
#   ],
#   "3": [
#     "overgrow",
#     "chlorophyll"
#   ],
#   "4": [
#     "blaze",
#     "solar-power"
#   ],
#   "7": [
#     "torrent",
#     "rain-dish"
#   ],
#   "8": [
#     "torrent",
#     "rain-dish"
#   ]
# }

import requests
import time
import json
from pathlib import Path

BASE = "https://pokeapi.co/api/v2"
POKEMON_ENDPOINT = f"{BASE}/pokemon?limit=100&offset=0"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "pokemon-abilities-only/1.0"})


def fetch_all_pokemon_urls():
    """Retrieve the URLs for all Pokémon from the paginated API endpoint."""
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


def fetch_pokemon_abilities(pokemon_url):
    """Fetch only the abilities for a single Pokémon by its API URL."""
    r = SESSION.get(pokemon_url, timeout=15)
    r.raise_for_status()
    data = r.json()
    abilities = [a["ability"]["name"] for a in data["abilities"]]
    return abilities


def build_all_pokemon_abilities(save_to="data/all_pokemon_abilities.json"):
    """Build and save the abilities mapping to disk.

    The mapping key is the Pokémon identifier (name or numeric id) and the
    value is a list of ability slugs.
    """
    Path("data").mkdir(exist_ok=True)
    urls = fetch_all_pokemon_urls()
    print(f"Found {len(urls)} Pokémon. Fetching abilities...")

    all_abilities = {}
    for i, url in enumerate(urls, start=1):
        try:
            abilities = fetch_pokemon_abilities(url)
        except Exception as e:
            print(f"[WARN] failed for {url}: {e}. Retrying once...")
            time.sleep(1)
            abilities = fetch_pokemon_abilities(url)
        pokemon_name = url.split("/")[-2]
        all_abilities[pokemon_name] = abilities
        if i % 50 == 0:
            print(f"  -> Processed {i}/{len(urls)} Pokémon")
        time.sleep(0.07)

    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(all_abilities, f, indent=2, ensure_ascii=False)
    print(f"Saved all Pokémon abilities to {save_to}")


if __name__ == "__main__":
    build_all_pokemon_abilities()
