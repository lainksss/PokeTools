"""Calculation endpoints for PokeTools API.

POST /api/calc_stats - calcul des stats finales
POST /api/calc_damage - calcul des dégâts
"""

from flask import Blueprint, request, jsonify

# Support importing utils when module is used as `backend.routes` or as top-level `routes`
try:
    from utils.data_loader import load_json
    from utils.helpers import build_actor_from_payload, compute_weight_based_power
except Exception:
    from ..utils.data_loader import load_json
    from ..utils.helpers import build_actor_from_payload, compute_weight_based_power

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

bp = Blueprint('calculations', __name__, url_prefix='/api')


@bp.route("/calc_stats", methods=["POST"])
def calc_stats():
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
        all_natures = load_json("all_natures.json") or {}
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


@bp.route("/calc_damage", methods=["POST"])
def calc_damage():
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
        all_moves = load_json("all_moves.json") or {}
        complete_move_data = all_moves.get(move_name, {})
        # Fusionner les données (priorité aux données du payload pour les valeurs déjà présentes)
        move_data = {**complete_move_data, **move_data}
        # Note: move flag enrichment is handled centrally in
        # `calculate_abilities.apply_ability_effects` to avoid duplication.

    # apply weight-based power computation
    try:
        move_data = compute_weight_based_power(move_data, attacker, defender, gen=payload.get("gen", 9))
    except Exception:
        # if anything fails, keep original move_data
        pass

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
