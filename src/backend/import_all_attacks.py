# Fetches all Pokémon moves from PokeAPI and builds a dict:
# { "thunderbolt": {"type":"electric","power":90,"accuracy":100,"damage_class":"special","multi_hit":None}, ... }

import requests
import time
import json
from typing import Dict, List

BASE = "https://pokeapi.co/api/v2"
MOVE_ENDPOINT = f"{BASE}/move"

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "pokemon-move-fetcher/1.0 (by you)"})

def fetch_all_moves_urls() -> List[Dict]:
    """Return the list of resource objects {name, url} for all moves."""
    url = MOVE_ENDPOINT + "?limit=100&offset=0"
    results = []
    while url:
        r = SESSION.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        results.extend(data.get("results", []))
        url = data.get("next")
        time.sleep(0.1)  # polite delay
    return results

def fetch_move_detail(url: str) -> Dict:
    """Fetch move details from its /move/{name} URL."""
    r = SESSION.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    move = {
        "type": data["type"]["name"],
    "power": data["power"],  # base damage
    "accuracy": data["accuracy"],  # accuracy
        "damage_class": data["damage_class"]["name"],  # physical, special, status
        "multi_hit": None
    }
    # Check if the move is multi-hit (e.g. Double Slap, Fury Attack, Bullet Seed, etc.)
    # `meta` can be null in some responses => normalize to dict
    meta = data.get("meta") or {}
    if isinstance(meta, dict) and "hits" in meta:
        move["multi_hit"] = meta["hits"]
    return move

def build_moves_dict(save_to="data/all_moves.json"):
    urls = fetch_all_moves_urls()
    print(f"Found {len(urls)} moves. Fetching details...")
    out: Dict[str, Dict] = {}
    for i, entry in enumerate(urls, start=1):
        try:
            detail = fetch_move_detail(entry["url"])
        except Exception as e:
            print(f"[WARN] error for {entry['name']}: {e}. Retrying once...")
            time.sleep(1)
            try:
                detail = fetch_move_detail(entry["url"])
            except Exception as e2:
                print(f"[ERROR] repeated failure for {entry['name']}: {e2}. Skip.")
                # skip this move and continue
                continue
        out[entry["name"]] = detail
        if i % 50 == 0:
            print(f"  -> fetched {i}/{len(urls)}")
        time.sleep(0.05)
    
    # save to JSON
    from pathlib import Path
    Path("data").mkdir(exist_ok=True)
    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(out)} moves to {save_to}")
    return out

if __name__ == "__main__":
    build_moves_dict()
