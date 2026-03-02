import csv
import requests
import io
import json

# URLs raw GitHub
URL_MOVE_FLAGS = "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/move_flags.csv"
URL_MOVE_FLAG_MAP = "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/move_flag_map.csv"
URL_MOVES = "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/moves.csv"

def download_csv(url: str) -> io.StringIO:
    """Télécharge un CSV depuis GitHub et renvoie un buffer exploitable."""
    r = requests.get(url)
    r.raise_for_status()
    return io.StringIO(r.text)

def load_move_flags():
    """Retourne un dict {flag_id : identifier}."""
    f = download_csv(URL_MOVE_FLAGS)
    reader = csv.DictReader(f)
    return {row["id"]: row["identifier"] for row in reader}

def load_move_flag_map():
    """Retourne un dict {move_id : [flag_id, ...]}."""
    f = download_csv(URL_MOVE_FLAG_MAP)
    reader = csv.DictReader(f)
    mapping = {}
    for row in reader:
        move_id = row["move_id"]
        flag_id = row["move_flag_id"]
        mapping.setdefault(move_id, []).append(flag_id)
    return mapping

def load_moves():
    """Retourne un dict {move_id : move_name}."""
    f = download_csv(URL_MOVES)
    reader = csv.DictReader(f)
    return {row["id"]: row["identifier"] for row in reader}

def build_move_flag_json():
    """
    Génère :
    {
        "move_name": ["flag1", "flag2", ...]
    }
    """
    print("Téléchargement des CSV…")
    flags = load_move_flags()
    flag_map = load_move_flag_map()
    moves = load_moves()

    print("Construction de la map finale…")
    result = {}

    for move_id, flag_ids in flag_map.items():
        if move_id not in moves:
            continue

        move_name = moves[move_id]
        flag_names = [flags[fid] for fid in flag_ids if fid in flags]

        result[move_name] = flag_names

    return result

def save_json(data, path="data/moves_with_flags.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"JSON généré → {path}")

if __name__ == "__main__":
    move_flags = build_move_flag_json()
    save_json(move_flags)
