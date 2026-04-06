# Collects all natures and saves them to a JSON file.
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
import os
from pathlib import Path
import time

BASE_URL = 'https://pokeapi.co/api/v2'
OUTPUT_PATH = 'data/all_natures.json'

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "pokemon-natures-script/2.0"})

def fetch_all_natures():
    os.makedirs('data', exist_ok=True)
    print("Fetching the exact number of natures...")

    response = SESSION.get(f'{BASE_URL}/nature', timeout=15)
    response.raise_for_status()
    initial_request = response.json()
    total_count = initial_request['count']
    print(f"Found {total_count} natures. Starting data collection...")

    response = SESSION.get(f'{BASE_URL}/nature?limit={total_count}', timeout=15)
    response.raise_for_status()
    data = response.json()
    
    natures_data = {}

    for index, item in enumerate(data['results']):
        nature_url = item['url']
        nature_response = SESSION.get(nature_url, timeout=15)
        nature_response.raise_for_status()
        nature_info = nature_response.json()
        
        # Handle modified stats (can be None if the nature is neutral)
        inc_stat = nature_info['increased_stat']['name'] if nature_info['increased_stat'] else None
        dec_stat = nature_info['decreased_stat']['name'] if nature_info['decreased_stat'] else None

        nature_dict = {
            "increase": inc_stat,
            "decrease": dec_stat
        }
        natures_data[nature_info['name']] = nature_dict
        print(f"Fetched nature: {item['name']}")
        time.sleep(0.05)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(natures_data, f, ensure_ascii=False, indent=2)
    print(f"✅ All natures saved in {OUTPUT_PATH}")

if __name__ == "__main__":
    try:
        fetch_all_natures()
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
