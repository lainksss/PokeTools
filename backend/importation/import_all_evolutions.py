# Script to fetch all Pokémon and determine if they can evolve, saving the data to a JSON file.
#
# Example output:
# {
#   "bulbasaur": {
#     "id": 1,
#     "can_evolve": true
#   },
#   "pikachu": {
#     "id": 25,
#     "can_evolve": true
#   },
#   "mew": {
#     "id": 151,
#     "can_evolve": false
#   }
# }

import requests
import time
import json
from pathlib import Path

BASE = "https://pokeapi.co/api/v2"
POKEMON_ENDPOINT = f"{BASE}/pokemon?limit=100&offset=0"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "pokemon-evolution-checker/1.2"})

def fetch_all_pokemon_urls():
    url = POKEMON_ENDPOINT
    urls = []
    while url:
        r = SESSION.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        urls.extend(data["results"])  # contient { "name": "bulbasaur", "url": "..." }
        url = data.get("next")
        time.sleep(0.1)
    return urls

def can_pokemon_evolve(pokemon_name):
    """Retourne True/False si le Pokémon peut évoluer."""
    species_url = f"{BASE}/pokemon-species/{pokemon_name}/"
    r = SESSION.get(species_url, timeout=15)
    if r.status_code == 404:
        return None  # forme alternative
    r.raise_for_status()
    species_data = r.json()

    # si aucune chaîne d’évolution n’est fournie
    if not species_data.get("evolution_chain"):
        return False

    evo_chain_url = species_data["evolution_chain"]["url"]
    r = SESSION.get(evo_chain_url, timeout=15)
    r.raise_for_status()
    chain = r.json()["chain"]

    def check(chain, name):
        if chain["species"]["name"] == name:
            return bool(chain["evolves_to"])
        for evo in chain["evolves_to"]:
            res = check(evo, name)
            if res is not None:
                return res
        return None

    evolves = check(chain, pokemon_name)
    return bool(evolves)

def build_evolution_json(save_to="data/pokemon_evolution.json"):
    Path("data").mkdir(exist_ok=True)
    urls = fetch_all_pokemon_urls()
    print(f"Found {len(urls)} Pokémon. Checking evolutions...")

    all_data = {}
    for i, entry in enumerate(urls, start=1):
        name = entry["name"]
        try:
            evolves = can_pokemon_evolve(name)
            if evolves is None:
                print(f"[SKIP] {name} (no species entry)")
                continue
        except Exception as e:
            print(f"[WARN] failed for {name}: {e}. Skipping.")
            continue

        all_data[name] = {
            "id": i,
            "can_evolve": evolves
        }
        if i % 50 == 0:
            print(f"  -> Processed {i}/{len(urls)} Pokémon")
        time.sleep(0.07)

    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print(f"Saved Pokémon evolution data to {save_to}")

if __name__ == "__main__":
    build_evolution_json()
