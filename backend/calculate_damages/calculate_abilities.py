from typing import Dict, Tuple, Optional


def apply_ability_effects(
    attacker: Dict,
    defender: Dict,
    move: Dict,
    field: Dict,
    multipliers: Dict[str, float],
    A: float,
    D: float,
    type_mult: float,
    gen: int = 9,
) -> Tuple[Dict[str, float], float, float, float, Dict]:
    """Apply common ability effects that change damage/stat multipliers.

    Returns (multipliers, A, D, type_mult, effects_dict).

    This function applies a conservative, well-scoped subset of abilities that
    directly change damage output or type immunities. It is intentionally
    additive: it mutates multipliers via multiplicative updates.
    """
    effects: Dict = {}
    # Normalize ability strings to canonical slug form (lowercase, hyphens)
    def norm_ability(x: Optional[str]) -> str:
        if not x:
            return ""
        s = str(x).lower()
        s = s.replace(" ", "-").replace("_", "-")
        return s

    atk_ability = norm_ability(attacker.get("ability") if attacker else None)
    def_ability = norm_ability(defender.get("ability") if defender else None)
    mv_name = (move.get("name") or "").lower()
    mv_type = move.get("type")
    category = move.get("damage_class", "physical")

    # Helper to multiply a named multiplier
    def mul(k: str, v: float):
        multipliers[k] = float(multipliers.get(k, 1.0)) * float(v)

    # --- Attacker-side abilities ---
    # Huge Power / Pure Power: double Attack (physical) stat
    if atk_ability in ("huge-power", "pure-power") and category == "physical":
        A = float(A) * 2.0
        effects["huge_power"] = True

    # Tough Claws: +30% on contact moves
    if atk_ability == "tough-claws" and move.get("makes_contact"):
        mul("other_mult", 1.3)
        effects["tough_claws"] = True

    # Sheer Force: +30% to moves with secondary effects
    if atk_ability == "sheer-force" and move.get("has_secondary"):
        mul("other_mult", 1.3)
        effects["sheer_force"] = True

    # Reckless: +20% to recoil moves
    if atk_ability == "reckless" and move.get("recoil"):
        mul("other_mult", 1.2)
        effects["reckless"] = True

    # Iron Fist: +20% to punching moves
    if atk_ability == "iron-fist" and move.get("is_punch"):
        mul("other_mult", 1.2)
        effects["iron_fist"] = True

    # Strong Jaw: +50% to biting moves
    if atk_ability == "strong-jaw" and move.get("is_bite"):
        mul("other_mult", 1.5)
        effects["strong_jaw"] = True

    # Technician: boosts moves with power <= 60 by 1.5
    try:
        power = int(move.get("power") or 0)
    except Exception:
        power = 0
    if atk_ability == "technician" and power <= 60 and power > 0:
        mul("other_mult", 1.5)
        effects["technician"] = True

    # Sniper: increase critical multiplier (handled by overriding crit_mult later)
    if atk_ability == "sniper":
        # Caller will check this flag and adjust crit multiplier to 3x when applicable
        effects["sniper"] = True

    # Guts: increase Attack by 50% while having a status for physical moves
    if atk_ability == "guts" and attacker.get("status") and category == "physical":
        A = float(A) * 1.5
        effects["guts"] = True

    # Aerilate / Pixilate / Refrigerate / Galvanize: treat Normal moves as other type + 20%
    mapping = {
        "aerilate": "flying",
        "pixilate": "fairy",
        "refrigerate": "ice",
        "galvanize": "electric",
    }
    if atk_ability in mapping and mv_type == "normal":
        new_type = mapping[atk_ability]
        move["type"] = new_type
        mul("other_mult", 1.2)
        # recompute STAB will happen in calling code if needed
        effects[atk_ability] = new_type

    # Protean / Libero: change user's type to move's type (we mark it; compute_stab already respects is_terastallized/orig_types logic)
    if atk_ability in ("protean", "libero") and mv_type:
        # Caller may choose to update attacker's 'types' or rely on effects
        effects[atk_ability] = mv_type

    # Type-specific boosts when at low HP (Blaze, Torrent, Overgrow, Swarm)
    if attacker.get("hp") is not None and attacker.get("max_hp"):
        hp = float(attacker.get("hp"))
        max_hp = float(attacker.get("max_hp"))
        if max_hp > 0 and hp <= max_hp / 3.0:
            at = atk_ability
            if at == "blaze" and mv_type == "fire":
                mul("other_mult", 1.5)
                effects["blaze"] = True
            if at == "torrent" and mv_type == "water":
                mul("other_mult", 1.5)
                effects["torrent"] = True
            if at == "overgrow" and mv_type == "grass":
                mul("other_mult", 1.5)
                effects["overgrow"] = True
            if at == "swarm" and mv_type == "bug":
                mul("other_mult", 1.5)
                effects["swarm"] = True

    # Abilities that boost specific types (Steelworker, Battle Bond ignored)
    if atk_ability == "steelworker" and mv_type == "steel":
        mul("other_mult", 1.5)
        effects["steelworker"] = True
    if atk_ability == "victorystar":
        # implemented elsewhere if needed (accuracy)
        effects["victorystar"] = True

    # --- Defender-side abilities that change type effectiveness ---
    # Levitate: immunity to Ground
    if def_ability == "levitate" and mv_type == "ground":
        type_mult = 0.0
        effects["immune"] = "levitate"

    # Water Absorb / Volt Absorb / Dry Skin / Flash Fire (simplified): absorb and immune
    if def_ability in ("water-absorb", "volt-absorb", "dry-skin"):
        if (def_ability == "water-absorb" and mv_type == "water") or (
            def_ability == "volt-absorb" and mv_type == "electric"
        ) or (def_ability == "dry-skin" and mv_type == "water"):
            type_mult = 0.0
            effects["absorbed"] = def_ability
    if def_ability == "flash-fire" and mv_type == "fire":
        type_mult = 0.0
        effects["absorbed"] = "flash-fire"

    # Solid Rock / Filter / Prism Armor reduce super-effective damage by 25%
    if def_ability in ("solid-rock", "filter", "prism-armor") and type_mult > 1.0:
        type_mult = float(type_mult) * 0.75
        effects[def_ability] = True

    # Tera Shell: when defender is at full HP, mark for special handling
    # (will force type effectiveness to 0.5x in calculate_damages.py)
    if def_ability == "tera-shell":
        if defender.get("hp") is not None and defender.get("max_hp"):
            hp = float(defender.get("hp"))
            max_hp = float(defender.get("max_hp"))
            if hp >= max_hp:  # Full HP
                effects["tera_shell_active"] = True

    # Multiscale: when defender is at full HP, halve damage taken
    if def_ability == "multiscale":
        if defender.get("hp") is not None and defender.get("max_hp"):
            hp = float(defender.get("hp"))
            max_hp = float(defender.get("max_hp"))
            if hp >= max_hp:  # Full HP
                mul("other_mult", 0.5)
                effects["multiscale"] = True

    # Shadow Shield: when defender is at full HP, halve damage taken
    if def_ability == "shadow-shield":
        if defender.get("hp") is not None and defender.get("max_hp"):
            hp = float(defender.get("hp"))
            max_hp = float(defender.get("max_hp"))
            if hp >= max_hp:  # Full HP
                mul("other_mult", 0.5)
                effects["shadow_shield"] = True

    # Thick Fat: halve damage from Fire and Ice type moves
    if def_ability == "thick-fat":
        if mv_type in ("fire", "ice"):
            mul("other_mult", 0.5)
            effects["thick_fat"] = True

    # Neuroforce / Beast Boost etc increase damage in particular circumstances (not implemented here)

    return multipliers, A, D, type_mult, effects
