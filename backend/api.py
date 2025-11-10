"""Refactored Flask API exposing calculation and data endpoints.

Exposes:
- GET  /api/health
- GET  /api/pokemon (liste complète des pokémons)
- GET  /api/pokemon/:id (détails d'un pokémon spécifique)
- GET  /api/pokemon/:id/moves (mouvements d'un pokémon)
- GET  /api/pokemon/:id/abilities (talents d'un pokémon)
- GET  /api/types (liste de tous les types)
- GET  /api/natures (liste de toutes les natures)
- POST /api/calc_stats (calcul des stats finales)
- POST /api/calc_damage (calcul des dégâts)

This file loads the helper modules from the local backend package and reads
the prebuilt JSON files from the repository `data/` directory.
"""

from pathlib import Path
import sys
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# path setup: ensure backend package can be imported
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA_DIR = ROOT / "data"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

app = Flask(__name__)
CORS(app)

# import calculators (fall back to importlib if necessary)
try:
    from calculate_statistics.calculate_statistics import calc_all_stats
except Exception:
    import importlib
    calc_all_stats = importlib.import_module("calculate_statistics.calculate_statistics").calc_all_stats

try:
    from calculate_damages.calculate_damages import calculate_damage
except Exception:
    import importlib
    calculate_damage = importlib.import_module("calculate_damages.calculate_damages").calculate_damage


# --- Data loading helpers (lazy cached) ---
_CACHE = {}

def _load_json(filename: str):
    if filename in _CACHE:
        return _CACHE[filename]
    path = DATA_DIR / filename
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            _CACHE[filename] = data
            return data
    except Exception:
        return None


def build_actor_from_payload(p):
    """Build a minimal attacker/defender dict expected by calculate_damage.

    p: payload from frontend (keys: pokemon_id, base_stats, evs, nature, ability, move, is_terastallized, tera_type)
    """
    base_stats = p.get("base_stats") or {}
    evs = p.get("evs") or {}
    
    # Convertir nature en multiplicateurs
    nature_name = p.get("nature")
    natures_map = {}
    if nature_name:
        all_natures = _load_json("all_natures.json") or {}
        nature_data = all_natures.get(nature_name)
        if nature_data:
            inc = nature_data.get("increase")
            dec = nature_data.get("decrease")
            # Normaliser les noms de stats (special-attack -> special_attack)
            if inc:
                inc_normalized = inc.replace("-", "_")
                natures_map[inc_normalized] = 1.1
            if dec:
                dec_normalized = dec.replace("-", "_")
                natures_map[dec_normalized] = 0.9

    # Normaliser base_stats (special-attack -> special_attack)
    bases_normalized = {}
    for k, v in base_stats.items():
        key_normalized = k.replace("-", "_")
        bases_normalized[key_normalized] = v

    # Calculer les stats finales
    stats = calc_all_stats(bases_normalized, evs=evs, natures=natures_map)

    actor = {
        "attack": stats.get("attack"),
        "defense": stats.get("defense"),
        "special_attack": stats.get("special_attack"),
        "special_defense": stats.get("special_defense"),
        "speed": stats.get("speed"),
        "hp": stats.get("hp"),
        "max_hp": stats.get("hp"),
        "types": p.get("types", []),
        "ability": p.get("ability"),
        "status": p.get("status"),
        "stages": p.get("stages", {}),
        "is_terastallized": p.get("is_terastallized", False),
        "tera_type": p.get("tera_type"),
        "orig_types": p.get("types", []),
    }
    return actor


# --- Calculation endpoints ---
@app.route("/api/calc_stats", methods=["POST"])
def api_calc_stats():
    """Calcule les stats finales d'un pokémon."""
    data = request.get_json() or {}
    base_stats = data.get("base_stats")
    if not base_stats:
        return jsonify({"error": "base_stats required"}), 400
    
    evs = data.get("evs", {})
    nature_name = data.get("nature")
    
    # Convertir nature en multiplicateurs
    natures_map = {}
    if nature_name:
        all_natures = _load_json("all_natures.json") or {}
        nature_data = all_natures.get(nature_name)
        if nature_data:
            inc = nature_data.get("increase")
            dec = nature_data.get("decrease")
            if inc:
                inc_normalized = inc.replace("-", "_")
                natures_map[inc_normalized] = 1.1
            if dec:
                dec_normalized = dec.replace("-", "_")
                natures_map[dec_normalized] = 0.9
    
    # Normaliser base_stats
    bases_normalized = {}
    for k, v in base_stats.items():
        key_normalized = k.replace("-", "_")
        bases_normalized[key_normalized] = v
    
    stats = calc_all_stats(bases_normalized, evs=evs, natures=natures_map)
    return jsonify({"stats": stats})


@app.route("/api/calc_damage", methods=["POST"])
def api_calc_damage():
    """Calcule les dégâts d'une attaque."""
    payload = request.get_json() or {}
    attacker_data = payload.get("attacker")
    defender_data = payload.get("defender")
    move_data = payload.get("move")

    if not attacker_data or not defender_data:
        return jsonify({"error": "attacker and defender required"}), 400
    
    if not move_data:
        return jsonify({"error": "move required"}), 400

    attacker = build_actor_from_payload(attacker_data)
    defender = build_actor_from_payload(defender_data)

    # Calculer les dégâts
    try:
        result = calculate_damage(
            move_data,
            attacker,
            defender,
            field=payload.get("field", {}),
            defender_hp=payload.get("defender_hp"),
            is_critical=payload.get("is_critical", False),
            random_range=payload.get("random_range"),
            gen=payload.get("gen", 9),
            debug=payload.get("debug", False),
        )
    except Exception as e:
        return jsonify({"error": "calculation failed", "message": str(e)}), 500

    return jsonify(result)


@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"ok": True, "service": "pokemon-calculator-backend"})


# --- Data endpoints ---
@app.route("/api/pokemon", methods=["GET"])
def api_pokemon_list():
    """Retourne la liste complète des pokémons avec leurs stats de base."""
    pok = _load_json("all_pokemon.json") or {}
    results = []
    for slug, data in pok.items():
        if not data:
            continue
        entry = {
            "id": data.get("id"),
            "name": slug,
            "types": data.get("types", []),
            "base_stats": data.get("base_stats", {})
        }
        results.append(entry)
    # Trier par ID
    results.sort(key=lambda x: x.get("id", 0))
    return jsonify({"count": len(results), "results": results})


@app.route("/api/pokemon/<int:pokemon_id>", methods=["GET"])
def api_pokemon_detail(pokemon_id: int):
    """Retourne les détails d'un pokémon spécifique par son ID."""
    pok = _load_json("all_pokemon.json") or {}
    for slug, data in pok.items():
        if data and data.get("id") == pokemon_id:
            return jsonify({
                "id": data.get("id"),
                "name": slug,
                "types": data.get("types", []),
                "base_stats": data.get("base_stats", {})
            })
    return jsonify({"error": "pokemon not found"}), 404


@app.route("/api/pokemon/<int:pokemon_id>/moves", methods=["GET"])
def api_pokemon_moves(pokemon_id: int):
    """Retourne la liste des moves d'un pokémon par son ID."""
    mapping = _load_json("all_pokemon_moves.json") or {}
    moves = mapping.get(str(pokemon_id))
    if moves is None:
        return jsonify({"error": "moves not found"}), 404
    
    # Charger les détails des moves
    all_moves = _load_json("all_moves.json") or {}
    detailed_moves = []
    for move_slug in moves:
        move_data = all_moves.get(move_slug, {})
        detailed_moves.append({
            "name": move_slug,
            "type": move_data.get("type"),
            "power": move_data.get("power"),
            "accuracy": move_data.get("accuracy"),
            "damage_class": move_data.get("damage_class")
        })
    
    return jsonify({"pokemon_id": pokemon_id, "count": len(detailed_moves), "moves": detailed_moves})


@app.route("/api/pokemon/<int:pokemon_id>/abilities", methods=["GET"])
def api_pokemon_abilities(pokemon_id: int):
    """Retourne la liste des talents d'un pokémon par son ID."""
    mapping = _load_json("all_pokemon_abilities.json") or {}
    abilities = mapping.get(str(pokemon_id))
    if abilities is None:
        return jsonify({"error": "abilities not found"}), 404
    return jsonify({"pokemon_id": pokemon_id, "count": len(abilities), "abilities": abilities})


@app.route("/api/types", methods=["GET"])
def api_types():
    """Retourne la liste de tous les types."""
    types_data = _load_json("all_types.json") or {}
    type_names = sorted(list(types_data.keys()))
    return jsonify({"count": len(type_names), "types": type_names})


@app.route("/api/natures", methods=["GET"])
def api_natures():
    """Retourne la liste de toutes les natures avec leurs effets."""
    natures_data = _load_json("all_natures.json") or {}
    results = []
    for name, data in natures_data.items():
        results.append({
            "name": name,
            "increase": data.get("increase"),
            "decrease": data.get("decrease")
        })
    # Trier alphabétiquement
    results.sort(key=lambda x: x.get("name", ""))
    return jsonify({"count": len(results), "natures": results})


if __name__ == "__main__":
    # Run the API locally; allow environment override for host/port
    import os
    host = os.environ.get("API_HOST", "0.0.0.0")
    port = int(os.environ.get("API_PORT", "5000"))
    app.run(host=host, port=port, debug=True)
