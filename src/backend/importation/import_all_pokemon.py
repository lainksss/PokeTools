# Fetches all Pokémon from PokeAPI and builds a dict:
#
# Example export (sample structure saved to data/all_pokemon.json):
# {
#   "bulbasaur": {
#     "id": 1,
#     "types": ["grass", "poison"],
#     "base_stats": {
#       "hp": 45,
#       "attack": 49,
#       "defense": 49,
#       "special-attack": 65,
#       "special-defense": 65,
#       "speed": 45
#     }
#   },
#   "charmander": {
#     "id": 4,
#     "types": ["fire"],
#     "base_stats": {
#       "hp": 39,
#       "attack": 52,
#       "defense": 43,
#       "special-attack": 60,
#       "special-defense": 50,
#       "speed": 65
#     }
#   }
# }

import requests
import time
import json
from typing import Dict, List

BASE = "https://pokeapi.co/api/v2"
POKEMON_ENDPOINT = f"{BASE}/pokemon"

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "pokemon-dump-script/1.0 (by you)"})

def fetch_all_pokemon_urls() -> List[Dict]:
    """Return the list of resource objects {name, url} for all Pokémon."""
    url = POKEMON_ENDPOINT + "?limit=100&offset=0"
    results = []
    while url:
        r = SESSION.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        results.extend(data.get("results", []))
        url = data.get("next")
        # be polite with the API (rate-limit throttling prevention)
        time.sleep(0.12)
    return results

def fetch_pokemon_detail(url: str) -> Dict:
    """Fetch details (types + stats) for a Pokémon from a /pokemon/{name} URL."""
    r = SESSION.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    # types (order as given by the API)
    types = [t["type"]["name"] for t in sorted(data.get("types", []), key=lambda x: x["slot"])]
    # stats -> convert to dict
    stats = {}
    for s in data.get("stats", []):
        stat_name = s["stat"]["name"]  # e.g. "hp", "attack", "defense", "special-attack", ...
        base = s["base_stat"]
        stats[stat_name] = base
    return {
        "id": data.get("id"),
        "name": data.get("name"),
        "types": types,
        "base_stats": stats
    }

def build_pokemon_dict(save_to="data/all_pokemon.json"):
    urls = fetch_all_pokemon_urls()
    print(f"Found {len(urls)} pokemon entries. Fetching details...")
    out = {}
    for i, entry in enumerate(urls, start=1):
        try:
            detail = fetch_pokemon_detail(entry["url"])
        except Exception as e:
            print(f"[WARN] error for {entry['name']}: {e}. Retrying once...")
            time.sleep(1)
            detail = fetch_pokemon_detail(entry["url"])
        name = detail["name"]
        out[name] = {
            "id": detail["id"],
            "types": detail["types"],
            "base_stats": detail["base_stats"]
        }
        if i % 50 == 0:
            print(f"  -> fetched {i}/{len(urls)}")
        time.sleep(0.07)
    # saving to file
    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(out)} pokemon to {save_to}")
    return out

if __name__ == "__main__":
    build_pokemon_dict()
