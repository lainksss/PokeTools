# It gets all the moves for each Pokémon, but only saves the move names.
# Exemple export (sample structure saved to data/all_pokemon_moves.json):
# {
#   "bulbasaur": [
#     "razor-wind",
#     "swords-dance",
#     "cut",
#     "bind",
#     "vine-whip",
#     "headbutt",
#     "tackle",
#     "body-slam",
#     "take-down",
#     "double-edge",
#     "growl"
#   ],
#   "ivysaur": [
#     "swords-dance",
#     "cut",
#     "bind",
#     "vine-whip",
#     "headbutt",
#     "tackle",
#     "body-slam",
#     "take-down",
#     "double-edge",
#     "growl",
#     "roar"
#   ]
# }

import requests
import time
import json
from pathlib import Path

BASE = "https://pokeapi.co/api/v2"
POKEMON_ENDPOINT = f"{BASE}/pokemon?limit=100&offset=0"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "pokemon-moves-names-only/1.0"})

def fetch_all_pokemon_urls():
    """Collect all pokemon's url."""
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

def fetch_pokemon_move_names(pokemon_url):
    """Collect only the move's name."""
    r = SESSION.get(pokemon_url, timeout=15)
    r.raise_for_status()
    data = r.json()
    move_names = [m["move"]["name"] for m in data["moves"]]
    return move_names

def build_all_pokemon_moves(save_to="data/all_pokemon_moves.json"):
    Path("data").mkdir(exist_ok=True)
    urls = fetch_all_pokemon_urls()
    print(f"Found {len(urls)} Pokémon. Fetching move names...")

    all_moves = {}
    for i, url in enumerate(urls, start=1):
        try:
            moves = fetch_pokemon_move_names(url)
        except Exception as e:
            print(f"[WARN] failed for {url}: {e}. Retrying once...")
            time.sleep(1)
            moves = fetch_pokemon_move_names(url)
        all_moves[url.split("/")[-2]] = moves  # key: pokemon name from URL
        if i % 50 == 0:
            print(f"  -> Processed {i}/{len(urls)} Pokémon")
        time.sleep(0.07)

    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(all_moves, f, indent=2, ensure_ascii=False)
    print(f"Saved all Pokémon move names to {save_to}")

if __name__ == "__main__":
    build_all_pokemon_moves()
