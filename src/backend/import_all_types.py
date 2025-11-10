# types_fetcher.py
# Fetch all Pokémon type relations from the PokeAPI and save them to JSON

import requests
import json
from pathlib import Path

BASE = "https://pokeapi.co/api/v2"
TYPES_ENDPOINT = f"{BASE}/type"

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "pokemon-type-fetcher/1.0 (by you)"})

def fetch_all_types() -> dict:
    """Fetch all types and their offensive/defensive relations."""
    r = SESSION.get(TYPES_ENDPOINT, timeout=15)
    r.raise_for_status()
    all_types = [t["name"] for t in r.json()["results"]]

    type_chart = {}
    for t in all_types:
        r = SESSION.get(f"{TYPES_ENDPOINT}/{t}", timeout=15)
        r.raise_for_status()
        data = r.json()
        rel = data["damage_relations"]
        type_chart[t] = {
            "weak_to": [d["name"] for d in rel["double_damage_from"]],
            "resistant_to": [d["name"] for d in rel["half_damage_from"]],
            "immune_to": [d["name"] for d in rel["no_damage_from"]],
            "strong_against": [d["name"] for d in rel["double_damage_to"]],
            "weak_against": [d["name"] for d in rel["half_damage_to"]],
            "no_damage_to": [d["name"] for d in rel["no_damage_to"]],
        }
    return type_chart

def save_to_json(data: dict, path="data/all_types.json"):
    Path("data").mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} types to {path}")

if __name__ == "__main__":
    types_data = fetch_all_types()
    save_to_json(types_data)
