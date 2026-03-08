"""Coverage analysis endpoints.

POST /api/analyze_coverage_stream - analyse la couverture offensive
POST /api/analyze_type_coverage - analyse la couverture de types
"""

import json
from flask import Blueprint, request, jsonify, Response, stream_with_context

# Support utils import either as top-level `utils` or as `backend.utils`
try:
    from utils.data_loader import load_json
    from utils.helpers import build_actor_from_payload
    from utils.mandatory_items import force_mandatory_item
except Exception:
    from ..utils.data_loader import load_json
    from ..utils.helpers import build_actor_from_payload
    from ..utils.mandatory_items import force_mandatory_item

try:
    from calculate_damages.calculate_damages import calculate_damage
except Exception:
    import importlib
    calculate_damage = importlib.import_module("calculate_damages.calculate_damages").calculate_damage

bp = Blueprint('coverage', __name__)


@bp.route("/analyze_coverage_stream", methods=["POST"])
def analyze_coverage_stream():
    """Analyse la couverture offensive d'un attaquant avec plusieurs attaques (streaming)."""
    payload = request.get_json() or {}
    attacker_data = payload.get("attacker")
    moves_data = payload.get("moves", [])
    ko_mode = payload.get("ko_mode", "OHKO")
    include_no_ko = payload.get("include_no_ko", False)
    field_data = payload.get("field", {})
    bulk_mode = payload.get("bulk_mode", "none")
    custom_evs = payload.get("custom_evs", 0)
    custom_def_evs = int(payload.get("custom_def_evs", 0) or 0)
    custom_spdef_evs = int(payload.get("custom_spdef_evs", 0) or 0)
    custom_hp_evs = int(payload.get("custom_hp_evs", 0) or 0)
    bulk_nature_mode = payload.get("bulk_nature_mode", "byMove")
    bulk_assault_vest = bool(payload.get("bulk_assault_vest", False))
    bulk_evoluroc = bool(payload.get("bulk_evoluroc", False))
    fully_evolved_only = bool(payload.get("fully_evolved_only", False))

    if not attacker_data:
        return jsonify({"error": "attacker required"}), 400
    
    if not moves_data or len(moves_data) == 0:
        return jsonify({"error": "at least one move required"}), 400

    # Force mandatory item for attacker
    attacker_data = force_mandatory_item(attacker_data)

    def generate():
        try:
            all_pokemon_data = load_json("all_pokemon.json") or {}
            evo_map = load_json("pokemon_evolution.json") or {}

            # Build list and optionally filter to fully-evolved only
            all_pokemon = []
            for name, data in all_pokemon_data.items():
                if not data:
                    continue
                if fully_evolved_only:
                    try:
                        can_evolve = bool((evo_map.get(name) or {}).get('can_evolve', False))
                    except Exception:
                        can_evolve = False
                    if can_evolve:
                        continue
                all_pokemon.append({"name": name, **data})

            total_pokemon = len(all_pokemon)

            attacker = build_actor_from_payload(attacker_data)
            evo_map = load_json("pokemon_evolution.json") or {}

            yield f"data: {json.dumps({'type': 'init', 'total': total_pokemon})}\n\n"

            processed = 0
            total_coverage = 0

            for poke in all_pokemon:
                poke_id = poke.get("id")
                poke_slug = poke.get("name", "unknown")
                
                if bulk_mode == "none":
                    evs = {"hp": 0, "defense": 0, "special_defense": 0}
                    nature = "hardy"
                elif bulk_mode == "custom":
                    custom_hp = max(0, min(252, custom_hp_evs))
                    custom_def = max(0, min(252, custom_def_evs))
                    custom_spdef = max(0, min(252, custom_spdef_evs))
                    evs = {"hp": custom_hp, "defense": 0, "special_defense": 0}
                    if bulk_nature_mode == "byMove":
                        nature = "hardy"
                    else:
                        nature = "bold"
                else:  # bulk_mode == "max"
                    evs = {"hp": 252, "defense": 0, "special_defense": 0}
                    nature = "hardy"
                
                best_result = None
                best_move = None
                max_ko_chance = 0

                for move_data in moves_data:
                    try:
                        move_name = move_data.get("name")
                        if move_name:
                            all_moves = load_json("all_moves.json") or {}
                            complete_move_data = all_moves.get(move_name, {})
                            full_move_data = {**complete_move_data, **move_data}
                        else:
                            full_move_data = move_data
                        
                        defender_evs = evs.copy()
                        defender_nature = nature
                        if bulk_mode == "max":
                            damage_class = full_move_data.get("damage_class", "physical")
                            
                            if damage_class == "special":
                                defender_evs = {"hp": 252, "defense": 0, "special_defense": 252, "attack": 0, "special_attack": 0, "speed": 0}
                                defender_nature = "calm"
                            else:
                                defender_evs = {"hp": 252, "defense": 252, "special_defense": 0, "attack": 0, "special_attack": 0, "speed": 0}
                                defender_nature = "bold"
                        elif bulk_mode == "custom":
                            damage_class = full_move_data.get("damage_class", "physical")
                            
                            if damage_class == "special":
                                defender_evs = {"hp": custom_hp, "defense": 0, "special_defense": custom_spdef, "attack": 0, "special_attack": 0, "speed": 0}
                                if bulk_nature_mode == "byMove":
                                    defender_nature = "calm"
                            else:
                                defender_evs = {"hp": custom_hp, "defense": custom_def, "special_defense": 0, "attack": 0, "special_attack": 0, "speed": 0}
                                if bulk_nature_mode == "byMove":
                                    defender_nature = "bold"
                        else:
                            defender_evs = evs
                        
                        item = None
                        slug = poke.get("name")
                        can_evolve = False
                        try:
                            if slug and slug in evo_map:
                                can_evolve = bool(evo_map.get(slug, {}).get("can_evolve", False))
                        except Exception:
                            can_evolve = False

                        if bulk_evoluroc and can_evolve:
                            item = "eviolite"
                        elif bulk_assault_vest:
                            item = "assault-vest"
                        elif bulk_mode == "max" and can_evolve:
                            item = "eviolite"

                        defender_payload = {
                            "pokemon_id": poke_id,
                            "base_stats": poke.get("base_stats", {}),
                            "evs": defender_evs,
                            "nature": defender_nature,
                            "types": poke.get("types", []),
                            "ability": None,
                            "item": item,
                            "is_terastallized": False,
                            "tera_type": None,
                            "name": poke.get("name")
                        }
                        # Force mandatory item for defender
                        defender_payload = force_mandatory_item(defender_payload)
                        defender = build_actor_from_payload(defender_payload)

                        result = calculate_damage(
                            full_move_data,
                            attacker,
                            defender,
                            field=field_data,
                            gen=9,
                            debug=False
                        )

                        damage_all = result.get("damage_all", [])
                        defender_hp = result.get("defender_hp", 1)
                        
                        if ko_mode == "OHKO":
                            ko_count = sum(1 for dmg in damage_all if dmg >= defender_hp)
                        else:
                            ko_count = sum(1 for dmg in damage_all if dmg * 2 >= defender_hp)
                        
                        ko_percent = (ko_count / len(damage_all) * 100) if damage_all else 0

                        if ko_percent > max_ko_chance:
                            max_ko_chance = ko_percent
                            best_result = result
                            best_move = full_move_data

                    except Exception:
                        continue

                if include_no_ko or (best_result and max_ko_chance > 0):
                    if not best_result and include_no_ko:
                        try:
                            move_data = moves_data[0]
                            move_name = move_data.get("name")
                            if move_name:
                                all_moves = load_json("all_moves.json") or {}
                                complete_move_data = all_moves.get(move_name, {})
                                full_move_data = {**complete_move_data, **move_data}
                            else:
                                full_move_data = move_data
                            
                            best_result = calculate_damage(
                                full_move_data,
                                attacker,
                                defender,
                                field=field_data,
                                gen=9,
                                debug=False
                            )
                            best_move = full_move_data
                        except Exception:
                            continue
                    
                    if best_result:
                        damage_all = best_result.get("damage_all", [])
                        defender_hp = best_result.get("defender_hp", 1)
                        
                        if ko_mode == "OHKO":
                            rolls_that_ko = sum(1 for dmg in damage_all if dmg >= defender_hp)
                        else:
                            rolls_that_ko = sum(1 for dmg in damage_all if dmg * 2 >= defender_hp)

                        coverage_entry = {
                            "defender_name": poke_slug.capitalize(),
                            "defender_id": poke_id,
                            "defender_types": poke.get("types", []),
                            "defender_hp": defender_hp,
                            "best_move_name": best_move.get("name", "").replace("-", " ").title(),
                            "best_move_type": best_move.get("type", "normal"),
                            "max_ko_chance": max_ko_chance,
                            "max_rolls_that_ko": rolls_that_ko,
                            "damage_range": damage_all
                        }

                        total_coverage += 1
                        yield f"data: {json.dumps({'type': 'coverage', 'data': coverage_entry})}\n\n"

                processed += 1

                if processed <= 50 and processed % 5 == 0:
                    yield f"data: {json.dumps({'type': 'progress', 'processed': processed, 'total': total_pokemon, 'coverage_found': total_coverage})}\n\n"
                elif processed % 10 == 0:
                    yield f"data: {json.dumps({'type': 'progress', 'processed': processed, 'total': total_pokemon, 'coverage_found': total_coverage})}\n\n"

            yield f"data: {json.dumps({'type': 'complete', 'total_coverage': total_coverage, 'total_processed': processed})}\n\n"

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


@bp.route("/deep_analyze_coverage_stream", methods=["POST"])
def deep_analyze_coverage_stream():
    """Recherche approfondie: teste la couverture offensive en testant tous les talents/statuts des défenseurs.
    
    Logique:
    - Pour chaque defense Pokémon
    - Pour chaque attaque de l'attaquant
    - Tester tous les talents du défenseur × 3 statuts (normal, brûlé, empoisonné)
    - Garder le PIRE résultat (le plus bas KO%) pour cette attaque
    - Afficher les 4 attaques avec leurs pires résultats
    - Compter comme couverture positive si au moins une attaque peut tuer le défenseur dans le pire cas
    """
    payload = request.get_json() or {}
    attacker_data = payload.get("attacker")
    moves_data = payload.get("moves", [])
    ko_mode = payload.get("ko_mode", "OHKO")
    field_data = payload.get("field", {})
    fully_evolved_only = bool(payload.get("fully_evolved_only", False))
    include_no_ko = bool(payload.get("include_no_ko", False))

    if not attacker_data:
        return jsonify({"error": "attacker required"}), 400
    
    if not moves_data or len(moves_data) == 0:
        return jsonify({"error": "at least one move required"}), 400

    # Force mandatory item for attacker
    attacker_data = force_mandatory_item(attacker_data)

    def generate():
        try:
            all_pokemon_data = load_json("all_pokemon.json") or {}
            evo_map = load_json("pokemon_evolution.json") or {}
            pokemon_abilities_map = load_json("all_pokemon_abilities.json") or {}
            all_moves = load_json("all_moves.json") or {}

            # Build list of defenders and optionally filter to fully-evolved only
            all_defenders = []
            for name, data in all_pokemon_data.items():
                if not data:
                    continue
                if fully_evolved_only:
                    try:
                        can_evolve = bool((evo_map.get(name) or {}).get('can_evolve', False))
                    except Exception:
                        can_evolve = False
                    if can_evolve:
                        continue
                all_defenders.append({"name": name, **data})

            total_defenders = len(all_defenders)
            attacker = build_actor_from_payload(attacker_data)

            yield f"data: {json.dumps({'type': 'init', 'total': total_defenders})}\n\n"

            processed = 0
            total_coverage = 0

            for defender_poke in all_defenders:
                poke_id = defender_poke.get("id")
                poke_slug = defender_poke.get("name", "unknown")
                poke_types = defender_poke.get("types", [])
                base_stats = defender_poke.get("base_stats", {})
                
                # Get defender's abilities
                defender_abilities = pokemon_abilities_map.get(str(poke_id), []) or [None]
                
                # For each move, calculate worst-case KO% across all abilities/statuses
                move_results = []  # List of (move_name, worst_ko%, damage_info)

                for move_data in moves_data:
                    try:
                        move_name = move_data.get("name")
                        if move_name:
                            complete_move_data = all_moves.get(move_name, {})
                            full_move_data = {**complete_move_data, **move_data}
                        else:
                            full_move_data = move_data

                        move_name = full_move_data.get("name", "unknown")
                        move_type = full_move_data.get("type", "normal")
                        
                        # Track worst KO% for this move across all ability/status combos
                        worst_ko_for_move = float('inf')  # Initialize to infinity to ensure first result is taken
                        worst_damage_info = None

                        # Get defender's abilities (or use [None] if no abilities)
                        abilities_to_test = defender_abilities if defender_abilities else [None]

                        for ability in abilities_to_test:
                            for status in ['normal', 'burn', 'poison']:
                                try:
                                    defender_payload = {
                                        "pokemon_id": poke_id,
                                        "base_stats": base_stats,
                                        "evs": {"hp": 0, "attack": 0, "defense": 0, "special_attack": 0, "special_defense": 0, "speed": 0},
                                        "nature": "hardy",
                                        "types": poke_types,
                                        "ability": ability,
                                        "item": None,
                                        "is_terastallized": False,
                                        "tera_type": None,
                                        "status": status,
                                        "name": poke_slug
                                    }

                                    # Force mandatory item for defender
                                    defender_payload = force_mandatory_item(defender_payload)
                                    defender = build_actor_from_payload(defender_payload)

                                    result = calculate_damage(
                                        full_move_data,
                                        attacker,
                                        defender,
                                        field=field_data,
                                        gen=9,
                                        debug=False
                                    )

                                    damage_all = result.get("damage_all", [])
                                    defender_hp = result.get("defender_hp", defender.get("hp", 1))
                                    
                                    # Debug: log if damage_all is empty
                                    if not damage_all and full_move_data.get("power", 0) > 0:
                                        import sys
                                        print(f"DEBUG: Empty damage_all for {move_name} vs {poke_slug}", file=sys.stderr)
                                        print(f"  move: {full_move_data}", file=sys.stderr)
                                        print(f"  defender_hp from result: {result.get('defender_hp')}", file=sys.stderr)
                                        print(f"  defender dict: {defender}", file=sys.stderr)
                                    
                                    if ko_mode == "OHKO":
                                        ko_count = sum(1 for dmg in damage_all if dmg >= defender_hp)
                                    else:
                                        ko_count = sum(1 for dmg in damage_all if dmg * 2 >= defender_hp)
                                    
                                    ko_percent = (ko_count / len(damage_all) * 100) if damage_all else 0

                                    # compute damage range for this config
                                    damage_min = min(damage_all) if damage_all else 0
                                    damage_max = max(damage_all) if damage_all else 0

                                    # Update worst-case: prefer lower ko%, and when equal choose lower damage
                                    if (
                                        ko_percent < worst_ko_for_move or
                                        (ko_percent == worst_ko_for_move and (
                                            worst_damage_info is None or damage_min < worst_damage_info.get("damage_min", float('inf'))
                                        ))
                                    ):
                                        worst_ko_for_move = ko_percent
                                        worst_damage_info = {
                                            "damage_min": damage_min,
                                            "damage_max": damage_max,
                                            "defender_hp": defender_hp,
                                            "worst_ability": ability,
                                            "worst_status": status
                                        }

                                except Exception:
                                    continue

                        # Add this move result
                        move_results.append({
                            "move_name": move_name,
                            "move_type": move_type,
                            "worst_ko_percent": worst_ko_for_move,
                            "damage_info": worst_damage_info
                        })

                    except Exception:
                        continue

                # Sort moves by worst KO% (descending) and take top 4
                move_results.sort(key=lambda x: -x["worst_ko_percent"])
                top_moves = move_results[:4]

                # Prepare coverage entry
                coverage_entry = None
                has_any_ko = False

                if top_moves:
                    # Check if any move has a positive worst-case KO%
                    for move_result in top_moves:
                        if move_result["worst_ko_percent"] > 0:
                            has_any_ko = True
                            break

                    # Always create coverage entry (whether it KOs or not)
                    coverage_entry = {
                        "defender_name": poke_slug.capitalize() if poke_slug else f"Pokemon_{poke_id}",
                        "defender_id": poke_id,
                        "defender_types": poke_types,
                        "moves": [
                            {
                                "name": m["move_name"],
                                "type": m["move_type"],
                                "worst_ko_percent": round(m["worst_ko_percent"], 1),
                                "damage_min": m["damage_info"]["damage_min"] if m["damage_info"] else 0,
                                "damage_max": m["damage_info"]["damage_max"] if m["damage_info"] else 0,
                                "defender_hp": m["damage_info"]["defender_hp"] if m["damage_info"] else 1,
                                "worst_ability": m["damage_info"]["worst_ability"] if m["damage_info"] else None,
                                "worst_status": m["damage_info"]["worst_status"] if m["damage_info"] else None
                            }
                            for m in top_moves
                        ]
                    }

                if coverage_entry:
                    if has_any_ko:
                        total_coverage += 1
                    yield f"data: {json.dumps({'type': 'coverage', 'data': coverage_entry})}\n\n"

                processed += 1

                if processed % 10 == 0:
                    yield f"data: {json.dumps({'type': 'progress', 'processed': processed, 'total': total_defenders, 'coverage_found': total_coverage})}\n\n"

            yield f"data: {json.dumps({'type': 'complete', 'total_coverage': total_coverage, 'total_processed': processed})}\n\n"

        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


@bp.route("/analyze_type_coverage", methods=["POST"])
def analyze_type_coverage():
    """Analyse la couverture de types : trouve les Pokémon qui ne sont PAS touchés en super efficace."""
    payload = request.get_json() or {}
    moves_data = payload.get("moves", [])
    attacker_data = payload.get("attacker", {})

    if not moves_data or len(moves_data) == 0:
        return jsonify({"error": "at least one move required"}), 400

    fully_evolved_only = bool(payload.get('fully_evolved_only', False))

    try:
        all_pokemon_data = load_json("all_pokemon.json") or {}
        evo_map = load_json("pokemon_evolution.json") or {}
        all_moves = load_json("all_moves.json") or {}
        type_chart = load_json("all_types.json") or {}
        
        is_terastallized = attacker_data.get("is_terastallized", False)
        tera_type = attacker_data.get("tera_type")

        move_types = []
        for move_data in moves_data:
            move_name = move_data.get("name")
            if move_name and move_name in all_moves:
                move_info = all_moves[move_name]
                damage_class = move_info.get("damage_class", "status")
                
                if damage_class in ["physical", "special"]:
                    move_type = move_info.get("type")
                    
                    if move_name == "tera-blast" and is_terastallized and tera_type:
                        move_type = tera_type
                    
                    if move_type:
                        move_types.append({
                            "name": move_name,
                            "type": move_type,
                            "damage_class": damage_class
                        })

        if not move_types:
            return jsonify({"error": "No damaging moves found"}), 400

        not_super_effective = []
        
        for poke_name, poke_data in all_pokemon_data.items():
            if fully_evolved_only:
                try:
                    can_evolve = bool((evo_map.get(poke_name) or {}).get('can_evolve', False))
                except Exception:
                    can_evolve = False
                if can_evolve:
                    continue
            poke_id = poke_data.get("id")
            poke_types = poke_data.get("types", [])
            
            best_effectiveness = 0.0
            best_move = None
            best_move_type = None
            
            for move in move_types:
                from calculate_damages.calculate_types import type_effectiveness
                effectiveness = type_effectiveness(move["type"], poke_types, type_chart)
                
                if effectiveness > best_effectiveness:
                    best_effectiveness = effectiveness
                    best_move = move["name"]
                    best_move_type = move["type"]
            
            if best_effectiveness < 1.0:
                not_super_effective.append({
                    "pokemon_id": poke_id,
                    "pokemon_name": poke_name,
                    "types": poke_types,
                    "best_effectiveness": best_effectiveness,
                    "best_move": best_move,
                    "best_move_type": best_move_type
                })
        
        not_super_effective.sort(key=lambda x: x["best_effectiveness"])
        
        return jsonify({
            "not_super_effective": not_super_effective,
            "total_pokemon": len(all_pokemon_data),
            "not_covered": len(not_super_effective),
            "move_types_used": [m["type"] for m in move_types]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
