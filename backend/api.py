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
from flask import Flask, request, jsonify, Response, stream_with_context
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

    # Enrichir move_data avec les infos complètes depuis all_moves.json
    move_name = move_data.get("name")
    if move_name:
        all_moves = _load_json("all_moves.json") or {}
        complete_move_data = all_moves.get(move_name, {})
        # Fusionner les données (priorité aux données du payload pour les valeurs déjà présentes)
        move_data = {**complete_move_data, **move_data}

    # Calculer les dégâts
    try:
        # Ajouter battle_mode au field si fourni
        field_data = payload.get("field", {})
        if payload.get("battle_mode"):
            field_data["battle_mode"] = payload.get("battle_mode")
        
        result = calculate_damage(
            move_data,
            attacker,
            defender,
            field=field_data,
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


@app.route("/api/find_threats", methods=["POST"])
def api_find_threats():
    """Trouve tous les Pokémon pouvant OHKO ou 2HKO le défenseur avec streaming progressif."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "missing payload"}), 400

    defender_payload = data.get("defender")
    ko_mode = data.get("ko_mode", "OHKO")  # 'OHKO' or '2HKO'
    field = data.get("field", {})

    if not defender_payload:
        return jsonify({"error": "missing defender"}), 400

    # Construire le défenseur
    defender = build_actor_from_payload(defender_payload)
    defender_hp = defender["hp"]

    # Charger tous les Pokémon
    all_pokemon = _load_json("all_pokemon.json") or {}
    all_moves = _load_json("all_moves.json") or {}
    all_natures = _load_json("all_natures.json") or {}
    pokemon_moves_map = _load_json("all_pokemon_moves.json") or {}

    threats = []
    
    # Natures qui augmentent l'attaque
    attack_boosting_natures = []
    sp_attack_boosting_natures = []
    
    for nature_name, nature_data in all_natures.items():
        inc = nature_data.get("increase")
        if inc == "attack":
            attack_boosting_natures.append(nature_name)
        elif inc == "special-attack":
            sp_attack_boosting_natures.append(nature_name)

    # Pour chaque Pokémon
    for poke_slug, poke_data in all_pokemon.items():
        if not poke_data:
            continue
            
        poke_id = poke_data.get("id")
        poke_name = poke_slug
        poke_types = poke_data.get("types", [])
        base_stats = poke_data.get("base_stats", {})
        
        # Récupérer les moves de ce Pokémon
        poke_moves = pokemon_moves_map.get(str(poke_id), [])
        
        # Tester 2 variants: 
        # 1. Full Attack EVs (252 Attack + 252 Sp.Attack)
        # 2. Full Attack EVs + Nature qui booste l'attaque
        
        variants = [
            {
                "name": "Max EVs",
                "evs": {"hp": 0, "attack": 252, "defense": 0, "special_attack": 252, "special_defense": 0, "speed": 0},
                "nature": "hardy"
            }
        ]
        
        # Ajouter variants avec natures
        if attack_boosting_natures:
            variants.append({
                "name": "Max EVs + Atk Nature",
                "evs": {"hp": 0, "attack": 252, "defense": 0, "special_attack": 0, "special_defense": 0, "speed": 0},
                "nature": attack_boosting_natures[0]
            })
        
        if sp_attack_boosting_natures:
            variants.append({
                "name": "Max EVs + SpA Nature",
                "evs": {"hp": 0, "attack": 0, "defense": 0, "special_attack": 252, "special_defense": 0, "speed": 0},
                "nature": sp_attack_boosting_natures[0]
            })
        
        for variant in variants:
            # Construire l'attaquant
            attacker_payload = {
                "pokemon_id": poke_id,
                "base_stats": base_stats,
                "evs": variant["evs"],
                "nature": variant["nature"],
                "types": poke_types,
                "ability": None,
                "is_terastallized": False,
                "tera_type": None
            }
            
            ko_moves = []  # Liste des moves qui peuvent KO
            
            # Tester chaque move
            for move_slug in poke_moves:
                move_data = all_moves.get(move_slug, {})
                damage_class = move_data.get("damage_class")
                power = move_data.get("power")
                
                # OPTIMISATION: Ignorer uniquement les moves de statut (pas physiques/spéciaux)
                if damage_class == "status":
                    continue
                
                # Construire le payload pour le calcul
                calc_payload = {
                    "attacker": attacker_payload,
                    "defender": defender_payload,
                    "move": {
                        "name": move_slug,
                        "type": move_data.get("type"),
                        "power": power,
                        "damage_class": damage_class
                    },
                    "field": field,
                    "is_critical": False
                }
                
                try:
                    attacker_calc = build_actor_from_payload(calc_payload["attacker"])
                    move = calc_payload["move"]
                    is_crit = calc_payload.get("is_critical", False)
                    
                    dmg_result = calculate_damage(
                        attacker=attacker_calc,
                        defender=defender,
                        move=move,
                        field=field,
                        is_critical=is_crit
                    )
                    
                    damage_min = dmg_result["damage_min"]
                    damage_max = dmg_result["damage_max"]
                    
                    # Vérifier si c'est un KO
                    is_ko = False
                    ko_percent = 0
                    
                    if ko_mode == "OHKO":
                        # OHKO: damage_max >= defender_hp
                        if damage_max >= defender_hp:
                            is_ko = True
                            # Calculer le pourcentage de KO
                            if damage_min >= defender_hp:
                                ko_percent = 100
                            else:
                                # Approximation: probabilité linéaire entre min et max
                                ko_rolls = damage_max - defender_hp + 1
                                total_rolls = damage_max - damage_min + 1
                                ko_percent = min(100, int((ko_rolls / total_rolls) * 100))
                    
                    elif ko_mode == "2HKO":
                        # 2HKO: damage_max * 2 >= defender_hp
                        if damage_max * 2 >= defender_hp:
                            is_ko = True
                            if damage_min * 2 >= defender_hp:
                                ko_percent = 100
                            else:
                                # Calcul simplifié pour 2HKO
                                ko_percent = 50  # Approximation
                    
                    if is_ko:
                        ko_moves.append({
                            "move_name": move_slug,
                            "move_power": power,
                            "damage_min": damage_min,
                            "damage_max": damage_max,
                            "ko_percent": ko_percent,
                            "guaranteed_ko": ko_percent == 100
                        })
                
                except Exception as e:
                    # Ignorer les erreurs de calcul
                    continue
            
            # Si ce variant a au moins un move qui KO
            if ko_moves:
                # Trier par KO garanti d'abord, puis par damage_max
                ko_moves.sort(key=lambda x: (not x["guaranteed_ko"], -x["damage_max"]))
                
                # Prendre le meilleur move
                best_move = ko_moves[0]
                
                threat_entry = {
                    "attacker_name": poke_name.capitalize(),
                    "attacker_id": poke_id,
                    "variant": variant["name"],
                    "move_name": best_move["move_name"],
                    "move_power": best_move["move_power"],
                    "damage_min": best_move["damage_min"],
                    "damage_max": best_move["damage_max"],
                    "ko_percent": best_move["ko_percent"],
                    "guaranteed_ko": best_move["guaranteed_ko"],
                    "other_moves_count": len(ko_moves) - 1
                }
                
                threats.append(threat_entry)
    
    # Trier les menaces par KO garanti d'abord, puis par damage_max
    threats.sort(key=lambda x: (not x["guaranteed_ko"], -x["damage_max"]))
    
    return jsonify({
        "defender_hp": defender_hp,
        "ko_mode": ko_mode,
        "threat_count": len(threats),
        "threats": threats
    })


@app.route("/api/find_threats_stream", methods=["POST"])
def api_find_threats_stream():
    """Version streaming de find_threats - OPTIMISÉE ET CORRIGÉE."""
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "missing payload"}), 400

    defender_payload = data.get("defender")
    ko_mode = data.get("ko_mode", "OHKO")
    field = data.get("field", {})

    if not defender_payload:
        return jsonify({"error": "missing defender"}), 400

    def generate():
        """Générateur qui yield les résultats progressivement."""
        try:
            # Construire le défenseur avec SES stats configurées
            defender = build_actor_from_payload(defender_payload)
            defender_hp = defender["hp"]

            # Charger les données
            all_pokemon = _load_json("all_pokemon.json") or {}
            all_moves = _load_json("all_moves.json") or {}
            all_natures = _load_json("all_natures.json") or {}
            pokemon_moves_map = _load_json("all_pokemon_moves.json") or {}
            pokemon_abilities_map = _load_json("all_pokemon_abilities.json") or {}

            # Trouver les natures qui boostent l'attaque
            attack_boost_nature = None
            sp_attack_boost_nature = None
            
            for nature_name, nature_data in all_natures.items():
                inc = nature_data.get("increase")
                if inc == "attack" and not attack_boost_nature:
                    attack_boost_nature = nature_name
                elif inc == "special-attack" and not sp_attack_boost_nature:
                    sp_attack_boost_nature = nature_name
                if attack_boost_nature and sp_attack_boost_nature:
                    break

            total_pokemon = len(all_pokemon)
            processed = 0
            total_threats = 0
            
            # Envoyer l'initialisation
            yield f"data: {json.dumps({'type': 'init', 'total': total_pokemon, 'defender_hp': defender_hp})}\n\n"

            # Pour chaque Pokémon
            for poke_slug, poke_data in all_pokemon.items():
                if not poke_data:
                    processed += 1
                    continue
                    
                poke_id = poke_data.get("id")
                poke_types = poke_data.get("types", [])
                base_stats = poke_data.get("base_stats", {})
                
                # Vérifier si le Pokémon a un seul talent
                poke_abilities = pokemon_abilities_map.get(str(poke_id), [])
                poke_ability = None
                if len(poke_abilities) == 1:
                    poke_ability = poke_abilities[0]
                
                # Récupérer les moves
                poke_moves = pokemon_moves_map.get(str(poke_id), [])
                if not poke_moves:
                    processed += 1
                    continue
                
                # On va tester les moves et garder max 3 qui KO
                ko_attacks = []
                max_attacks_to_keep = 3
                
                # Tester chaque move
                for move_slug in poke_moves:
                    # Si on a déjà 3 attaques qui KO, on arrête pour ce Pokémon
                    if len(ko_attacks) >= max_attacks_to_keep:
                        break
                    
                    move_data = all_moves.get(move_slug, {})
                    damage_class = move_data.get("damage_class")
                    
                    # DEBUG pour le premier Pokémon
                    if processed == 0 and len(ko_attacks) == 0:
                        print(f"Testing {poke_slug} - Move: {move_slug} - Class: {damage_class}")
                    
                    # Ignorer les moves de statut
                    if damage_class not in ["physical", "special"]:
                        continue
                    
                    # Choisir les EVs et la nature selon le type de move
                    if damage_class == "physical":
                        evs = {"hp": 0, "attack": 252, "defense": 0, "special_attack": 0, "special_defense": 0, "speed": 0}
                        nature = attack_boost_nature or "hardy"
                    else:  # special
                        evs = {"hp": 0, "attack": 0, "defense": 0, "special_attack": 252, "special_defense": 0, "speed": 0}
                        nature = sp_attack_boost_nature or "hardy"
                    
                    # Construire l'attaquant pour ce move
                    attacker_payload = {
                        "pokemon_id": poke_id,
                        "base_stats": base_stats,
                        "evs": evs,
                        "nature": nature,
                        "types": poke_types,
                        "ability": poke_ability,  # Utiliser l'ability si le Pokémon n'en a qu'une
                        "is_terastallized": False,
                        "tera_type": None
                    }
                    
                    attacker = build_actor_from_payload(attacker_payload)
                    
                    move_info = {
                        "name": move_slug,
                        "type": move_data.get("type"),
                        "power": move_data.get("power"),
                        "damage_class": damage_class
                    }
                    
                    try:
                        dmg_result = calculate_damage(
                            attacker=attacker,
                            defender=defender,
                            move=move_info,
                            field=field,
                            is_critical=False
                        )
                        
                        # calculate_damage retourne damage_all, pas damage_min/max
                        damage_all = dmg_result.get("damage_all", [])
                        
                        if not damage_all:
                            continue
                        
                        damage_min = min(damage_all)
                        damage_max = max(damage_all)
                        damage_rolls = damage_all
                        
                        # DEBUG pour le premier Pokémon
                        if processed == 0 and len(ko_attacks) == 0:
                            print(f"  -> Damage: {damage_min}-{damage_max} vs {defender_hp} HP")
                            print(f"  -> Attacker Attack: {attacker.get('attack')}, SpA: {attacker.get('special_attack')}")
                            print(f"  -> Nature: {nature}, EVs: Attack={evs.get('attack')}, SpA={evs.get('special_attack')}")
                        
                        # Vérifier si c'est un KO
                        is_ko = False
                        ko_rolls = 0
                        total_rolls = len(damage_rolls) if damage_rolls else 16
                        
                        if ko_mode == "OHKO":
                            # Compter combien de rolls tuent en 1 coup
                            if damage_rolls:
                                ko_rolls = sum(1 for d in damage_rolls if d >= defender_hp)
                            elif damage_max >= defender_hp:
                                # Approximation si pas de rolls
                                if damage_min >= defender_hp:
                                    ko_rolls = total_rolls
                                else:
                                    ko_rolls = max(1, int((damage_max - defender_hp + 1) / (damage_max - damage_min + 1) * total_rolls))
                            
                            is_ko = ko_rolls > 0
                        
                        elif ko_mode == "2HKO":
                            # Pour 2HKO, il faut gérer les talents qui ne s'activent qu'au full HP
                            # Talents concernés: Multiscale, Shadow Shield, Tera Shell
                            defender_ability = defender.get("ability", "")
                            full_hp_abilities = ["multiscale", "shadow-shield", "tera-shell"]
                            
                            has_full_hp_ability = defender_ability in full_hp_abilities
                            
                            if has_full_hp_ability and damage_rolls:
                                # Recalculer le 2ème coup SANS le talent (defender non-full HP)
                                # Créer un defender temporaire sans HP full
                                defender_second_hit = defender.copy()
                                defender_second_hit["hp"] = defender_hp - 1  # HP non-full pour désactiver le talent
                                
                                try:
                                    dmg_result_second = calculate_damage(
                                        attacker=attacker,
                                        defender=defender_second_hit,
                                        move=move_info,
                                        field=field,
                                        is_critical=False
                                    )
                                    
                                    damage_all_second = dmg_result_second.get("damage_all", [])
                                    
                                    if damage_all_second:
                                        # Compter combien de combinaisons de rolls tuent en 2 coups
                                        # 1er coup (avec talent) + 2ème coup (sans talent)
                                        ko_rolls = 0
                                        for dmg1 in damage_rolls:
                                            for dmg2 in damage_all_second:
                                                if dmg1 + dmg2 >= defender_hp:
                                                    ko_rolls += 1
                                        
                                        total_rolls = len(damage_rolls) * len(damage_all_second)
                                        is_ko = ko_rolls > 0
                                    else:
                                        # Fallback si le calcul échoue
                                        ko_rolls = sum(1 for d in damage_rolls if d * 2 >= defender_hp)
                                        total_rolls = len(damage_rolls)
                                        is_ko = ko_rolls > 0
                                except Exception:
                                    # Fallback en cas d'erreur
                                    ko_rolls = sum(1 for d in damage_rolls if d * 2 >= defender_hp)
                                    total_rolls = len(damage_rolls)
                                    is_ko = ko_rolls > 0
                            else:
                                # Pas de talent full HP ou pas de rolls : calcul simple
                                if damage_rolls:
                                    ko_rolls = sum(1 for d in damage_rolls if d * 2 >= defender_hp)
                                elif damage_max * 2 >= defender_hp:
                                    if damage_min * 2 >= defender_hp:
                                        ko_rolls = total_rolls
                                    else:
                                        ko_rolls = max(1, int((damage_max * 2 - defender_hp + 1) / (damage_max - damage_min + 1) * total_rolls))
                                
                                is_ko = ko_rolls > 0
                        
                        # Si c'est un KO, on l'ajoute
                        if is_ko:
                            # DEBUG
                            if processed == 0:
                                print(f"  -> KO FOUND! {move_slug}: {ko_rolls}/{total_rolls} rolls ({int((ko_rolls/total_rolls)*100)}%)")
                            
                            ko_attacks.append({
                                "move_name": move_slug,
                                "move_type": move_data.get("type"),
                                "move_power": move_data.get("power"),
                                "damage_class": damage_class,
                                "damage_min": damage_min,
                                "damage_max": damage_max,
                                "ko_rolls": ko_rolls,
                                "total_rolls": total_rolls,
                                "ko_percent": int((ko_rolls / total_rolls) * 100) if total_rolls > 0 else 0,
                                "nature_used": nature
                            })
                    
                    except Exception as e:
                        # Ignorer les erreurs de calcul
                        if processed == 0:
                            print(f"  -> ERROR: {str(e)}")
                        continue
                
                # Si on a trouvé au moins une attaque qui KO
                if ko_attacks:
                    # DEBUG
                    if total_threats < 3:
                        print(f"\n*** THREAT FOUND: {poke_slug} with {len(ko_attacks)} KO moves ***\n")
                    
                    # Trier par % de KO (meilleurs d'abord)
                    ko_attacks.sort(key=lambda x: (-x["ko_percent"], -x["damage_max"]))
                    
                    # Créer l'entrée de menace avec toutes les attaques trouvées (max 3)
                    threat_entry = {
                        "attacker_name": poke_slug.capitalize(),
                        "attacker_id": poke_id,
                        "ko_attacks": ko_attacks[:3],  # Maximum 3 attaques
                        "best_ko_percent": ko_attacks[0]["ko_percent"]
                    }
                    
                    total_threats += 1
                    
                    # Envoyer la menace trouvée
                    yield f"data: {json.dumps({'type': 'threat', 'data': threat_entry})}\n\n"
                
                processed += 1
                
                # Envoyer la progression tous les 20 Pokémon
                if processed % 20 == 0:
                    yield f"data: {json.dumps({'type': 'progress', 'processed': processed, 'total': total_pokemon, 'threats_found': total_threats})}\n\n"

            # Envoyer la fin
            yield f"data: {json.dumps({'type': 'complete', 'total_threats': total_threats, 'total_processed': processed})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


if __name__ == "__main__":
    # Run the API locally; allow environment override for host/port
    import os
    host = os.environ.get("API_HOST", "0.0.0.0")
    port = int(os.environ.get("API_PORT", "5000"))
    app.run(host=host, port=port, debug=True)
