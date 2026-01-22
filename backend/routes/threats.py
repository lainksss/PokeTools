"""Threat analysis endpoints.

POST /api/find_threats - trouve les menaces OHKO/2HKO (non-streaming)
POST /api/find_threats_stream - version streaming
"""

import json
from flask import Blueprint, request, jsonify, Response, stream_with_context

from utils.data_loader import load_json
from utils.helpers import build_actor_from_payload

try:
    from calculate_damages.calculate_damages import calculate_damage
except Exception:
    import importlib
    calculate_damage = importlib.import_module("calculate_damages.calculate_damages").calculate_damage

bp = Blueprint('threats', __name__)


@bp.route("/find_threats", methods=["POST"])
def find_threats():
    """Trouve tous les Pokémon pouvant OHKO ou 2HKO le défenseur."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "missing payload"}), 400

    defender_payload = data.get("defender")
    ko_mode = data.get("ko_mode", "OHKO")  # 'OHKO' or '2HKO'
    field = data.get("field", {})
    analysis_options = data.get("analysis_options", {}) or {}

    attack_mode = analysis_options.get("attack_mode", "default")
    custom_evs = int(analysis_options.get("custom_evs", 0) or 0)
    nature_boost = bool(analysis_options.get("nature_boost", False))
    item_choice = bool(analysis_options.get("item_choice", False))
    life_orb = bool(analysis_options.get("life_orb", False))

    if not defender_payload:
        return jsonify({"error": "missing defender"}), 400

    # Construire le défenseur
    defender = build_actor_from_payload(defender_payload)
    defender_hp = defender["hp"]

    # Charger tous les Pokémon
    all_pokemon = load_json("all_pokemon.json") or {}
    all_moves = load_json("all_moves.json") or {}
    all_natures = load_json("all_natures.json") or {}
    pokemon_moves_map = load_json("all_pokemon_moves.json") or {}

    threats = []
    
    # Natures qui augmentent l'attaque (choisir la première disponible)
    attack_boosting_nature = None
    sp_attack_boosting_nature = None
    for nature_name, nature_data in all_natures.items():
        inc = nature_data.get("increase")
        if inc == "attack" and not attack_boosting_nature:
            attack_boosting_nature = nature_name
        elif inc == "special-attack" and not sp_attack_boosting_nature:
            sp_attack_boosting_nature = nature_name
        if attack_boosting_nature and sp_attack_boosting_nature:
            break

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
        if not poke_moves:
            continue

        # Pour chaque move, déterminer EVs/nature/item selon les analysis_options
        ko_moves = []
        for move_slug in poke_moves:
            move_data = all_moves.get(move_slug, {})
            damage_class = move_data.get("damage_class")
            power = move_data.get("power")

            # Ignorer les moves de statut
            if damage_class not in ("physical", "special"):
                continue

            # Determine evs and nature based on attack_mode
            if attack_mode == 'none':
                evs = {"hp": 0, "attack": 0, "defense": 0, "special_attack": 0, "special_defense": 0, "speed": 0}
                nature = 'hardy'
            elif attack_mode == 'custom':
                evs = {"hp": 0, "attack": custom_evs, "defense": 0, "special_attack": custom_evs, "special_defense": 0, "speed": 0}
                if nature_boost:
                    nature = attack_boosting_nature if damage_class == 'physical' else sp_attack_boosting_nature or 'hardy'
                else:
                    nature = 'hardy'
            elif attack_mode == 'max':
                evs = {"hp": 0, "attack": 252, "defense": 0, "special_attack": 252, "special_defense": 0, "speed": 0}
                if nature_boost:
                    nature = attack_boosting_nature if damage_class == 'physical' else sp_attack_boosting_nature or 'hardy'
                else:
                    nature = 'hardy'
            else:  # default behavior
                if damage_class == 'physical':
                    evs = {"hp": 0, "attack": 252, "defense": 0, "special_attack": 0, "special_defense": 0, "speed": 0}
                    nature = attack_boosting_nature or 'hardy'
                else:
                    evs = {"hp": 0, "attack": 0, "defense": 0, "special_attack": 252, "special_defense": 0, "speed": 0}
                    nature = sp_attack_boosting_nature or 'hardy'

            # Determine item (life orb or choice) if requested
            item = None
            if life_orb:
                item = 'life-orb'
            elif item_choice:
                item = 'choice-band' if damage_class == 'physical' else 'choice-specs'
            elif attack_mode == 'max':
                item = 'choice-band' if damage_class == 'physical' else 'choice-specs'

            # Construire le payload pour le calcul
            calc_payload = {
                "attacker": {
                    "pokemon_id": poke_id,
                    "base_stats": base_stats,
                    "evs": evs,
                    "nature": nature,
                    "types": poke_types,
                    "ability": None,
                    "item": item,
                    "is_terastallized": False,
                    "tera_type": None
                },
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

                damage_min = dmg_result.get("damage_min") or 0
                damage_max = dmg_result.get("damage_max") or 0

                # Vérifier si c'est un KO
                is_ko = False
                ko_percent = 0

                if ko_mode == "OHKO":
                    if damage_max >= defender_hp:
                        is_ko = True
                        if damage_min >= defender_hp:
                            ko_percent = 100
                        else:
                            total_rolls = max(1, damage_max - damage_min + 1)
                            ko_rolls = max(1, damage_max - defender_hp + 1)
                            ko_percent = min(100, int((ko_rolls / total_rolls) * 100))
                else:  # 2HKO approximation
                    if damage_max * 2 >= defender_hp:
                        is_ko = True
                        if damage_min * 2 >= defender_hp:
                            ko_percent = 100
                        else:
                            ko_percent = 50

                if is_ko:
                    ko_moves.append({
                        "move_name": move_slug,
                        "move_power": power,
                        "damage_min": damage_min,
                        "damage_max": damage_max,
                        "ko_percent": ko_percent,
                        "guaranteed_ko": ko_percent == 100
                    })

            except Exception:
                continue

        # Si on a trouvé des moves qui KO pour ce pokémon
        if ko_moves:
            ko_moves.sort(key=lambda x: (not x.get("guaranteed_ko", False), -x.get("damage_max", 0)))
            best_move = ko_moves[0]
            threat_entry = {
                "attacker_name": poke_name.capitalize(),
                "attacker_id": poke_id,
                "variant": attack_mode,
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


@bp.route("/find_threats_stream", methods=["POST"])
def find_threats_stream():
    """Version streaming de find_threats."""
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "missing payload"}), 400

    defender_payload = data.get("defender")
    ko_mode = data.get("ko_mode", "OHKO")
    field = data.get("field", {})
    analysis_options = data.get("analysis_options", {}) or {}

    attack_mode = analysis_options.get("attack_mode", "default")
    custom_evs = int(analysis_options.get("custom_evs", 0) or 0)
    nature_boost = bool(analysis_options.get("nature_boost", False))
    item_choice = bool(analysis_options.get("item_choice", False))
    life_orb = bool(analysis_options.get("life_orb", False))

    if not defender_payload:
        return jsonify({"error": "missing defender"}), 400

    def generate():
        """Générateur qui yield les résultats progressivement."""
        try:
            defender = build_actor_from_payload(defender_payload)
            defender_hp = defender["hp"]

            # Charger les données
            all_pokemon = load_json("all_pokemon.json") or {}
            all_moves = load_json("all_moves.json") or {}
            all_natures = load_json("all_natures.json") or {}
            pokemon_moves_map = load_json("all_pokemon_moves.json") or {}
            pokemon_abilities_map = load_json("all_pokemon_abilities.json") or {}

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
                
                ko_attacks = []
                max_attacks_to_keep = 3
                
                # Tester chaque move
                for move_slug in poke_moves:
                    if len(ko_attacks) >= max_attacks_to_keep:
                        break
                    
                    move_data = all_moves.get(move_slug, {})
                    damage_class = move_data.get("damage_class")
                    
                    # Ignorer les moves de statut
                    if damage_class not in ["physical", "special"]:
                        continue

                    # Choisir les EVs et la nature
                    if attack_mode == 'none':
                        evs = {"hp": 0, "attack": 0, "defense": 0, "special_attack": 0, "special_defense": 0, "speed": 0}
                        nature = 'hardy'
                    elif attack_mode == 'custom':
                        evs = {"hp": 0, "attack": custom_evs, "defense": 0, "special_attack": custom_evs, "special_defense": 0, "speed": 0}
                        nature = (attack_boost_nature if damage_class == 'physical' else sp_attack_boost_nature) if nature_boost else 'hardy'
                    elif attack_mode == 'max':
                        evs = {"hp": 0, "attack": 252, "defense": 0, "special_attack": 252, "special_defense": 0, "speed": 0}
                        nature = (attack_boost_nature if damage_class == 'physical' else sp_attack_boost_nature) if nature_boost else 'hardy'
                    else:
                        # default
                        if damage_class == "physical":
                            evs = {"hp": 0, "attack": 252, "defense": 0, "special_attack": 0, "special_defense": 0, "speed": 0}
                            nature = attack_boost_nature or "hardy"
                        else:
                            evs = {"hp": 0, "attack": 0, "defense": 0, "special_attack": 252, "special_defense": 0, "speed": 0}
                            nature = sp_attack_boost_nature or "hardy"
                    
                    # Determine item if requested
                    item = None
                    if life_orb:
                        item = 'life-orb'
                    elif item_choice:
                        item = 'choice-band' if damage_class == 'physical' else 'choice-specs'
                    elif attack_mode == 'max':
                        item = 'choice-band' if damage_class == 'physical' else 'choice-specs'

                    attacker_payload = {
                        "pokemon_id": poke_id,
                        "base_stats": base_stats,
                        "evs": evs,
                        "nature": nature,
                        "types": poke_types,
                        "ability": poke_ability,
                        "item": item,
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
                        
                        damage_all = dmg_result.get("damage_all", [])
                        
                        if not damage_all:
                            continue
                        
                        damage_min = min(damage_all)
                        damage_max = max(damage_all)
                        damage_rolls = damage_all
                        
                        # Vérifier si c'est un KO
                        is_ko = False
                        ko_rolls = 0
                        total_rolls = len(damage_rolls) if damage_rolls else 16
                        
                        if ko_mode == "OHKO":
                            if damage_rolls:
                                ko_rolls = sum(1 for d in damage_rolls if d >= defender_hp)
                            elif damage_max >= defender_hp:
                                if damage_min >= defender_hp:
                                    ko_rolls = total_rolls
                                else:
                                    ko_rolls = max(1, int((damage_max - defender_hp + 1) / (damage_max - damage_min + 1) * total_rolls))
                            
                            is_ko = ko_rolls > 0
                        
                        elif ko_mode == "2HKO":
                            defender_ability = defender.get("ability", "")
                            full_hp_abilities = ["multiscale", "shadow-shield", "tera-shell"]
                            
                            has_full_hp_ability = defender_ability in full_hp_abilities
                            
                            if has_full_hp_ability and damage_rolls:
                                defender_second_hit = defender.copy()
                                defender_second_hit["hp"] = defender_hp - 1
                                
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
                                        ko_rolls = 0
                                        for dmg1 in damage_rolls:
                                            for dmg2 in damage_all_second:
                                                if dmg1 + dmg2 >= defender_hp:
                                                    ko_rolls += 1
                                        
                                        total_rolls = len(damage_rolls) * len(damage_all_second)
                                        is_ko = ko_rolls > 0
                                    else:
                                        ko_rolls = sum(1 for d in damage_rolls if d * 2 >= defender_hp)
                                        total_rolls = len(damage_rolls)
                                        is_ko = ko_rolls > 0
                                except Exception:
                                    ko_rolls = sum(1 for d in damage_rolls if d * 2 >= defender_hp)
                                    total_rolls = len(damage_rolls)
                                    is_ko = ko_rolls > 0
                            else:
                                if damage_rolls:
                                    ko_rolls = sum(1 for d in damage_rolls if d * 2 >= defender_hp)
                                elif damage_max * 2 >= defender_hp:
                                    if damage_min * 2 >= defender_hp:
                                        ko_rolls = total_rolls
                                    else:
                                        ko_rolls = max(1, int((damage_max * 2 - defender_hp + 1) / (damage_max - damage_min + 1) * total_rolls))
                                
                                is_ko = ko_rolls > 0
                        
                        if is_ko:
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
                    
                    except Exception:
                        continue
                
                if ko_attacks:
                    ko_attacks.sort(key=lambda x: (-x["ko_percent"], -x["damage_max"]))
                    
                    threat_entry = {
                        "attacker_name": poke_slug.capitalize(),
                        "attacker_id": poke_id,
                        "ko_attacks": ko_attacks[:3],
                        "best_ko_percent": ko_attacks[0]["ko_percent"]
                    }
                    
                    total_threats += 1
                    
                    yield f"data: {json.dumps({'type': 'threat', 'data': threat_entry})}\n\n"
                
                processed += 1
                
                if processed % 20 == 0:
                    yield f"data: {json.dumps({'type': 'progress', 'processed': processed, 'total': total_pokemon, 'threats_found': total_threats})}\n\n"

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
