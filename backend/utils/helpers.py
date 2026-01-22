"""Helper functions for PokeTools API."""

from utils.data_loader import load_json


def build_actor_from_payload(p):
    """Build a minimal attacker/defender dict expected by calculate_damage.

    p: payload from frontend (keys: pokemon_id, base_stats, evs, nature, ability, move, is_terastallized, tera_type)
    """
    from calculate_statistics.calculate_statistics import calc_all_stats
    
    base_stats = p.get("base_stats") or {}
    evs = p.get("evs") or {}
    
    # Convertir nature en multiplicateurs
    nature_name = p.get("nature")
    natures_map = {}
    if nature_name:
        all_natures = load_json("all_natures.json") or {}
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

    # Gérer la téracristallisation pour les types
    original_types = p.get("types", [])
    is_terastallized = p.get("is_terastallized", False)
    tera_type = p.get("tera_type")
    
    # Si téracristallisé, les types défensifs deviennent UNIQUEMENT le type Tera
    if is_terastallized and tera_type:
        defensive_types = [tera_type]
    else:
        defensive_types = original_types

    actor = {
        "attack": stats.get("attack"),
        "defense": stats.get("defense"),
        "special_attack": stats.get("special_attack"),
        "special_defense": stats.get("special_defense"),
        "speed": stats.get("speed"),
        "hp": stats.get("hp"),
        "max_hp": stats.get("hp"),
        "types": defensive_types,  # Types défensifs (changent avec Tera)
        "ability": p.get("ability"),
        "status": p.get("status"),
        "stages": p.get("stages", {}),
        "is_terastallized": is_terastallized,
        "tera_type": tera_type,
        "orig_types": original_types,  # Types d'origine (pour le STAB)
    }
    # Include held item if provided
    if p.get("item"):
        actor["item"] = p.get("item")

    # Try to determine species slug and evolution info from data files when possible
    try:
        all_pok = load_json("all_pokemon.json") or {}
        evo = load_json("pokemon_evolution.json") or {}
        # p may provide pokemon_id
        poke_id = p.get("pokemon_id") or p.get("id") or None
        if poke_id is not None:
            for slug, dd in all_pok.items():
                if dd and dd.get("id") == poke_id:
                    actor["species"] = slug
                    break
        # can_evolve info
        if actor.get("species"):
            evo_info = evo.get(actor["species"], {})
            actor["can_evolve"] = bool(evo_info.get("can_evolve", False))
        # Determine weight_kg: prefer explicit payload override, else lookup from data file
        try:
            # payload can provide a current weight (e.g. after Autotomize/Minimize)
            if p.get("weight_kg") is not None:
                actor["weight_kg"] = float(p.get("weight_kg"))
            else:
                weights = load_json("all_pokemon_weight_height.json") or {}
                # Try by poke_id first
                if poke_id is not None and str(poke_id) in weights:
                    actor["weight_kg"] = float(weights.get(str(poke_id), {}).get("weight_kg", 0.0))
                else:
                    # Try by species slug -> lookup id
                    sp = actor.get("species")
                    if sp and sp in all_pok:
                        sp_id = all_pok.get(sp, {}).get("id")
                        if sp_id and str(sp_id) in weights:
                            actor["weight_kg"] = float(weights.get(str(sp_id), {}).get("weight_kg", 0.0))
        except Exception:
            # ignore weight lookup errors
            pass
    except Exception:
        # ignore any errors; these fields are optional
        pass
    # Include consumed items list if provided (used for one-use items like gems/berries)
    consumed = p.get("consumed_items") or p.get("consumed")
    if consumed:
        try:
            actor["consumed_items"] = list(consumed)
        except Exception:
            actor["consumed_items"] = []
    return actor


def compute_weight_based_power(move, attacker, defender, gen=9):
    """Return a copy of move with power set when it depends on weight.

    Rules implemented (from data/all_pokemon_weight_moves.json):
    - low-kick / grass-knot: target-weight thresholds -> {20,40,60,80,100,120}
    - heavy-slam / heat-crash: ratio user_weight/target_weight thresholds -> {40,60,80,100,120}

    The function prefers actor['weight_kg'] if present. If target weight is missing
    or zero, heavy-slam/heat-crash will return max power 120 to avoid division by zero.
    """
    name = move.get("name")
    if not name:
        return move

    name = name.lower()

    # Helper to read weight from actor dict (already set in build_actor_from_payload or overridden)
    def _actor_weight(a):
        try:
            w = a.get("weight_kg")
            if w is None:
                return None
            return float(w)
        except Exception:
            return None

    # Low Kick / Grass Knot: use defender weight
    if name in ("low-kick", "grass-knot"):
        tgt_w = _actor_weight(defender)
        if tgt_w is None:
            return move
        # thresholds in kg
        if tgt_w <= 10:
            power = 20
        elif tgt_w <= 25:
            power = 40
        elif tgt_w <= 50:
            power = 60
        elif tgt_w <= 100:
            power = 80
        elif tgt_w <= 200:
            power = 100
        else:
            power = 120
        new = dict(move)
        new["power"] = power
        return new

    # Heavy Slam / Heat Crash: compare attacker weight to defender weight
    if name in ("heavy-slam", "heat-crash"):
        atk_w = _actor_weight(attacker)
        tgt_w = _actor_weight(defender)
        if tgt_w is None or tgt_w <= 0 or atk_w is None:
            # If missing or zero target weight, conservative: return max power
            new = dict(move)
            new["power"] = 120
            return new
        ratio = atk_w / tgt_w
        if ratio <= 2:
            power = 40
        elif ratio <= 3:
            power = 60
        elif ratio <= 4:
            power = 80
        elif ratio <= 5:
            power = 100
        else:
            power = 120
        new = dict(move)
        new["power"] = power
        return new

    return move
