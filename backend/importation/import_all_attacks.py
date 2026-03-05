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
        time.sleep(0.1)
    return results


def fetch_move_detail(url: str) -> Dict:
    """Fetch move details from its /move/{name} URL."""

    r = SESSION.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    meta = data.get("meta") or {}

    # --- multi hit ---
    min_hits = meta.get("min_hits")
    max_hits = meta.get("max_hits")

    multi_hit = None
    if min_hits and max_hits:
        multi_hit = {
            "min": min_hits,
            "max": max_hits
        }
    # --- crit detection ---
    crit = False
    if meta.get("crit_rate") == 6:
        crit = True

    move = {
        "type": data["type"]["name"],
        "power": data["power"],
        "accuracy": data["accuracy"],
        "damage_class": data["damage_class"]["name"],
        "multi_hit": multi_hit,
        "crit": crit,
        "targets": 1
    }

    # --- target detection ---
    target_info = data.get("target", {})
    target_name = target_info.get("name", "")
    if target_name in ["all-opponents", "all-other-pokemon"]:
        move["targets"] = 2
    elif target_name in ["entire-field", "all-pokemon"]:
        move["targets"] = 3
    else:
        move["targets"] = 1
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
                continue
        out[entry["name"]] = detail
        if i % 50 == 0:
            print(f"  -> fetched {i}/{len(urls)}")
        time.sleep(0.05)
    from pathlib import Path
    Path("data").mkdir(exist_ok=True)
    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(out)} moves to {save_to}")
    return out

if __name__ == "__main__":
    build_moves_dict()