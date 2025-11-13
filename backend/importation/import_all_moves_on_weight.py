import requests
import json
import time
import random
import string
from pathlib import Path

BASE = "https://pokeapi.co/api/v2"
MOVE_ENDPOINT = f"{BASE}/move?limit=10000"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "weight-moves-exporter/1.0"})

def fetch_all_moves():
    r = SESSION.get(MOVE_ENDPOINT, timeout=15)
    r.raise_for_status()
    data = r.json()
    return data.get("results", [])

def fetch_move_detail(url):
    r = SESSION.get(url, timeout=15)
    r.raise_for_status()
    return r.json()

def is_weight_move(move_detail):
    """Check if the move description in English mentions 'weight'"""
    for entry in move_detail.get("effect_entries", []):
        if entry["language"]["name"] == "en" and "weight" in entry["effect"].lower():
            return True
    return False

def export_weight_moves():
    Path("data").mkdir(exist_ok=True)
    all_moves = fetch_all_moves()
    weight_moves = {}

    print(f"Checking {len(all_moves)} moves for 'weight' scaling...")
    for i, move in enumerate(all_moves, start=1):
        try:
            detail = fetch_move_detail(move["url"])
        except Exception as e:
            print(f"[WARN] failed for {move['name']}: {e}. Retrying once...")
            time.sleep(1)
            detail = fetch_move_detail(move["url"])
        
        # Exclude "transform"
        if detail["name"].lower() == "transform":
            continue

        if is_weight_move(detail):
            weight_moves[detail["name"]] = {
                "id": detail["id"],
                "power": detail["power"],
                "type": detail["type"]["name"],
                "pp": detail["pp"],
                "accuracy": detail["accuracy"],
                "effect": [e["effect"] for e in detail.get("effect_entries", []) if e["language"]["name"]=="en"][0]
            }

        if i % 50 == 0:
            print(f"  -> Processed {i}/{len(all_moves)} moves")
        time.sleep(0.05)

    filename = Path("data") / "all_pokemon_weight_moves.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(weight_moves, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(weight_moves)} weight-based moves to {filename}")


    print(f"Saved {len(weight_moves)} weight-based moves to {filename}")

if __name__ == "__main__":
    export_weight_moves()
