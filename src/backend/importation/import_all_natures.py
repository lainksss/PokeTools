# Collects all nature and saves them to a JSON file.
# Each nature includes which stat it boosts and which stat it lowers.

# Example output (excerpt of `data/all_natures.json`):
# {
#   "hardy": {
#     "increase": null,
#     "decrease": null
#   },
#   "bold": {
#     "increase": "defense",
#     "decrease": "attack"
#   }
# }

import requests
import json
from pathlib import Path
import time

BASE = "https://pokeapi.co/api/v2"
NATURE_ENDPOINT = f"{BASE}/nature/"

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "pokemon-natures/1.0"})

def fetch_all_natures():
    """Récupère la liste de toutes les natures avec leurs URLs"""
    r = SESSION.get(NATURE_ENDPOINT, timeout=15)
    r.raise_for_status()
    data = r.json()
    return data['results']

def fetch_nature_detail(url):
    """Récupère le buff et le nerf d'une nature à partir de son URL"""
    r = SESSION.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    return {
        "name": data['name'],
        "increased_stat": data['increased_stat']['name'] if data['increased_stat'] else None,
        "decreased_stat": data['decreased_stat']['name'] if data['decreased_stat'] else None
    }

def build_natures_json(save_to="data/all_natures.json"):
    Path("data").mkdir(exist_ok=True)
    natures_list = fetch_all_natures()
    print(f"Found {len(natures_list)} natures. Fetching details...")

    natures = {}
    for i, n in enumerate(natures_list, start=1):
        try:
            detail = fetch_nature_detail(n['url'])
        except Exception as e:
            print(f"[WARN] failed for {n['name']}: {e}. Retrying once...")
            time.sleep(1)
            detail = fetch_nature_detail(n['url'])
        natures[detail['name']] = {
            "increase": detail['increased_stat'],
            "decrease": detail['decreased_stat']
        }
        if i % 10 == 0:
            print(f"  -> Processed {i}/{len(natures_list)} natures")
        time.sleep(0.05)

    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(natures, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(natures)} natures to {save_to}")
    return natures

if __name__ == "__main__":
    build_natures_json()
