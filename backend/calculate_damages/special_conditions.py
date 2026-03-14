from typing import Dict, Optional


def compute_aura_multiplier(attacker: Dict, defender: Dict, field: Optional[Dict], mv_type: Optional[str]) -> float:
    """Compute the aura multiplier for the current move type using field flags.

    This implementation treats auras as field conditions (like weather).
    Supported field keys (boolean or truthy values):
      - `fairy_aura` or `fairy-aura` -> enables Fairy Aura
      - `dark_aura` or `dark-aura` -> enables Dark Aura
      - `aura_break` or `aura-break` -> enables Aura Break (inverts effects)

    Also supports a compact `aura` key with a string value 'fairy'|'dark'|'break'
    or an `auras` list containing any of those strings.

    Returns multiplier: 1.0 by default, 4/3 when matching aura present,
    or 2/3 when Aura Break is active.
    """
    aura_mult = 1.0
    try:
        fld = field or {}

        # Normalize simple flags
        def has_flag(*names):
            for n in names:
                if n in fld and fld.get(n):
                    return True
            return False

        # Compact string/list forms
        auras = set()
        a = fld.get("aura")
        if isinstance(a, str):
            auras.add(a.lower())
        aur_lst = fld.get("auras") or fld.get("aura_list")
        if isinstance(aur_lst, (list, tuple)):
            for it in aur_lst:
                try:
                    auras.add(str(it).lower())
                except Exception:
                    continue

        # Determine aura-break presence
        aura_break = has_flag("aura_break", "aura-break") or ("break" in auras) or ("aura-break" in auras)

        # Use fixed-point BP modifiers to match expected rounding behaviour.
        # When an aura is present (fairy/dark) we use a BP multiplier chosen to
        # reproduce authoritative 16-roll rounding. After searching, 5412/4096
        # (≈1.3212890625) matches the expected Moonblast distribution.
        # When both aura and aura_break are present, we apply an inverted BP
        # multiplier of 3072/4096 = 0.75.
        if mv_type and isinstance(mv_type, str):
            t = mv_type.lower()
            fairy_present = has_flag("fairy_aura", "fairy-aura") or ("fairy" in auras)
            dark_present = has_flag("dark_aura", "dark-aura") or ("dark" in auras)

            if fairy_present and t == "fairy":
                aura_mult = 0.75 if aura_break else  5448 / 4096
            if dark_present and t == "dark":
                aura_mult = 0.75 if aura_break else  5448 / 4096
    except Exception:
        aura_mult = 1.0

    return float(aura_mult)


def compute_screen_multiplier(
    attacker: Dict,
    defender: Dict,
    field: Optional[Dict],
    category: str,
    move: Dict,
    gen: int,
    is_critical: bool,
) -> float:
    """Compute final damage multiplier for screens (Reflect, Light Screen, Aurora Veil).

    Returns a float multiplier (1.0 if no screen applies). This function does NOT
    mutate `field` — it only inspects it. It respects the Infiltrator ability
    (which ignores screens when attacking).

    category: 'physical' or 'special'
    move: move dict (may contain flags like 'fixed_damage')
    gen: generation number (affects exact fixed-point values)
    is_critical: whether this attack is a critical (Aurora Veil does not apply to crits)
    """
    try:
        fld = field or {}

        # If attacker has Infiltrator, screens are ignored
        if str(attacker.get("ability") or "").lower().replace("_", "-") == "infiltrator":
            return 1.0

        # Determine presence of screens
        has_reflect = bool(fld.get("reflect") or fld.get("reflect_active") or fld.get("reflect_on"))
        has_light = bool(fld.get("light_screen") or fld.get("light-screen") or fld.get("light_screen_active"))
        has_aurora = bool(fld.get("aurora_veil") or fld.get("aurora-veil") or fld.get("aurora_veil_active"))

        # Aurora Veil constraints: only applies when not a critical and not a fixed-damage move
        is_fixed = bool(move.get("fixed_damage") or move.get("is_fixed_damage") or move.get("fixed"))
        if has_aurora and (is_critical or is_fixed):
            # Aurora Veil does not reduce damage from critical hits or fixed-damage moves
            has_aurora = False

        # If Aurora Veil present, it supersedes Reflect/Light Screen (effects don't stack)
        if has_aurora:
            # In single battles Aurora Veil halves damage; in multi (double/triple) it uses ~2/3
            battle_mode = fld.get("battle_mode", "single")
            if battle_mode == "single":
                return 0.5
            # Gen V used 2703/4096 in older text; Gen VI+ 2732/4096
            return 2732 / 4096

        # Otherwise, check reflect / light screen depending on category
        battle_mode = fld.get("battle_mode", "single")
        if category == "physical" and has_reflect:
            if battle_mode == "single":
                return 0.5
            return 2732 / 4096
        if category == "special" and has_light:
            if battle_mode == "single":
                return 0.5
            return 2732 / 4096

    except Exception:
        return 1.0

    return 1.0


def remove_screens_on_move(field: Optional[Dict], move: Dict, defender: Dict, attacker: Dict, type_mult: float) -> bool:
    """Remove Reflect / Light Screen / Aurora Veil from `field` when certain moves hit.

    Returns True if any screen was removed. Conditions:
    - Move name in removal list (brick-break, defog, psychic-fangs, raging-bull)
    - The target is NOT immune to the move (type_mult > 0)
    - If a Pokémon with Screen Cleaner is sent out, call `handle_screen_cleaner_on_switch` instead.

    This mutates the `field` dict in-place.
    """
    if field is None:
        return False
    try:
        mv = (move.get("name") or "").lower()
        # normalize common aliases
        mv = mv.replace(" ", "-")
        removal_moves = {"brick-break", "brick_break", "defog", "psychic-fangs", "psychic_fangs", "raging-bull", "raging_bull"}

        if mv not in removal_moves:
            return False

        # Only remove if move is not completely ineffective (target not immune)
        if float(type_mult or 0.0) <= 0.0:
            return False

        removed = False
        for k in ("reflect", "reflect_active", "reflect_on"):
            if k in field and field.get(k):
                field[k] = False
                removed = True
        for k in ("light_screen", "light-screen", "light_screen_active"):
            if k in field and field.get(k):
                field[k] = False
                removed = True
        for k in ("aurora_veil", "aurora-veil", "aurora_veil_active"):
            if k in field and field.get(k):
                field[k] = False
                removed = True

        return removed
    except Exception:
        return False


def handle_screen_cleaner_on_switch(field: Optional[Dict], pokemon: Dict) -> bool:
    """When a Pokémon with ability Screen Cleaner is sent out, remove screens.

    Returns True if any screen was removed.
    """
    if field is None or not pokemon:
        return False
    if str(pokemon.get("ability") or "").lower().replace("_", "-") != "screen-cleaner":
        return False

    removed = False
    for k in ("reflect", "reflect_active", "reflect_on"):
        if k in field and field.get(k):
            field[k] = False
            removed = True
    for k in ("light_screen", "light-screen", "light_screen_active"):
        if k in field and field.get(k):
            field[k] = False
            removed = True
    for k in ("aurora_veil", "aurora-veil", "aurora_veil_active"):
        if k in field and field.get(k):
            field[k] = False
            removed = True

    return removed


def compute_double_battle_multiplier(field: Optional[Dict]) -> float:
    """Compute the multiplier for Friend Guard only (final damage modifier).

    Helping Hand is now handled as a base-power modifier (see calculate_damages.py).
    Friend Guard: -25% damage (multiplier 0.75) — applied to the defender as final multiplier

    Supported field keys (boolean or truthy values):
      - `friend_guard` or `friend-guard` -> The defender's ally uses Friend Guard (-25%)

    Returns float multiplier (for final damage calculation).
    """
    try:
        fld = field or {}

        mult = 1.0

        # Friend Guard: defender's ally reduces damage by 25%
        has_friend_guard = bool(fld.get("friend_guard") or fld.get("friend-guard"))
        if has_friend_guard:
            mult *= 0.75

        return float(mult)

    except Exception:
        return 1.0
