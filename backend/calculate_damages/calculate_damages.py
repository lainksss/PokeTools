# Damage calculator (Generation V onward) — revised per user spec.

# This module implements the specific formula you requested and returns
# pv_defenseur - damage for each roll (default 16 rolls: 85..100).

# Formula implemented:
# damage = floor( ((2 * level / 5 + 2) * power * (A / D) / 50) * targets * pb * weather * glaiverush * random * stab * burn * other * zmove * terashield )

# Many effects are supported via keys in the `attacker`, `defender`, `move` and `field` dicts.
# See function docstring for the expected keys.

from __future__ import annotations

from typing import Dict, List, Optional, Iterable, Tuple
import math
import json
from pathlib import Path

# Prefer to reuse the smaller modules in this package when available
try:
    from .calculate_weather import compute_weather_mult
    from .calculate_terrain import compute_terrain_multiplier
    from .calculate_types import get_type_breakdown, type_effectiveness
    from .calculate_abilities import apply_ability_effects
    from .calculate_grounded import is_grounded
    from ..items.items import apply_item_stat_modifiers, compute_item_damage_multiplier, get_item
except Exception:
    # If relative imports fail (exec as script), fallback to local defs below
    compute_weather_mult = None  # type: ignore
    compute_terrain_multiplier = None  # type: ignore
    get_type_breakdown = None  # type: ignore
    type_effectiveness = None  # type: ignore
    is_grounded = None  # type: ignore
    # Try to load calculate_abilities.py directly from the same directory as this file.
    apply_ability_effects = None  # type: ignore
    apply_item_stat_modifiers = None
    compute_item_damage_multiplier = None
    get_item = None
    try:
        import importlib.util
        mod_path = Path(__file__).parent / "calculate_abilities.py"
        if mod_path.exists():
            spec = importlib.util.spec_from_file_location("calculate_abilities", str(mod_path))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore
            apply_ability_effects = getattr(mod, "apply_ability_effects", None)
        # Try to load calculate_grounded.py
        grounded_mod_path = Path(__file__).parent / "calculate_grounded.py"
        if grounded_mod_path.exists():
            spec = importlib.util.spec_from_file_location("calculate_grounded", str(grounded_mod_path))
            grounded_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(grounded_mod)  # type: ignore
            is_grounded = getattr(grounded_mod, "is_grounded", None)
        # Try to load items.py from parent/items/items.py
        items_mod_path = Path(__file__).parent.parent / "items" / "items.py"
        if items_mod_path.exists():
            spec = importlib.util.spec_from_file_location("items", str(items_mod_path))
            items_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(items_mod)  # type: ignore
            apply_item_stat_modifiers = getattr(items_mod, "apply_item_stat_modifiers", None)
            compute_item_damage_multiplier = getattr(items_mod, "compute_item_damage_multiplier", None)
            get_item = getattr(items_mod, "get_item", None)
    except Exception:
        apply_ability_effects = None
        is_grounded = None
        apply_item_stat_modifiers = None
        compute_item_damage_multiplier = None
        get_item = None


if get_type_breakdown is None:
    # If import failed (module executed as script), define local fallbacks
    def get_type_breakdown(move_type: str, defender_types: Iterable[str], type_chart: Optional[Dict[str, Dict]] = None) -> Dict[str, float]:
        breakdown: Dict[str, float] = {}
        if not type_chart or not move_type:
            for d in defender_types:
                breakdown[d] = 1.0
            return breakdown
        for d in defender_types:
            info = type_chart.get(d, {})
            if "no_damage_from" in info and move_type in info.get("no_damage_from", []):
                breakdown[d] = 0.0
                continue
            if "double_damage_from" in info and move_type in info.get("double_damage_from", []):
                breakdown[d] = 2.0
                continue
            if "half_damage_from" in info and move_type in info.get("half_damage_from", []):
                breakdown[d] = 0.5
                continue
            if move_type in info.get("immune_to", []):
                breakdown[d] = 0.0
                continue
            if move_type in info.get("weak_to", []):
                breakdown[d] = 2.0
                continue
            if move_type in info.get("resistant_to", []):
                breakdown[d] = 0.5
                continue
            breakdown[d] = 1.0
        return breakdown

    def type_effectiveness(move_type: str, defender_types: Iterable[str], type_chart: Optional[Dict[str, Dict]] = None) -> float:
        breakdown = get_type_breakdown(move_type, defender_types, type_chart)
        total = 1.0
        for d, m in breakdown.items():
            if m == 0.0:
                return 0.0
            total *= m
        return total


# --- Small helpers to keep calculate_damage concise ---
def load_type_chart_if_missing(type_chart: Optional[Dict[str, Dict]]) -> Optional[Dict[str, Dict]]:
    if type_chart is not None:
        return type_chart
    try:
        root = Path(__file__).resolve().parents[2]
        types_path = root / "data" / "all_types.json"
        if types_path.exists():
            with open(types_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        return None
    return None


def compute_effective_stat(pkm: Dict, key: str, stages_key: str, is_attack: bool, crit_ignore: bool) -> float:
    # Extracted from calculate_damage: supports several key name variants and stages
    # Look for the base stat value
    alt_keys = [key, key + "_base", key.replace("_", "-"), key.replace("_", " ")]
    base_val = None
    for k in alt_keys:
        if k in pkm and isinstance(pkm[k], (int, float)):
            base_val = pkm[k]
            break
    base = float(base_val or 0)
    
    # Look for stages/boosts
    stages = None
    stages_container = pkm.get("stages", {})
    if isinstance(stages_container, dict):
        for sk in (stages_key, stages_key.replace("_", "-"), stages_key.replace("_", " ")):
            if sk in stages_container:
                stages = stages_container.get(sk)
                break
    if stages is None:
        stages = 0
    
    # Apply critical hit logic (ignore negative offensive boosts and positive defensive boosts)
    if crit_ignore:
        if is_attack and stages < 0:
            stages = 0
        if (not is_attack) and stages > 0:
            stages = 0
    
    # Apply boost multiplier
    if stages >= 0:
        mult = (2.0 + stages) / 2.0
    else:
        mult = 2.0 / (2.0 - stages)
    
    return base * mult


def compute_stat_with_stages_only(pkm: Dict, key: str, stages_key: str) -> float:
    """Calculate stat with only base stat and stage modifiers (for Tera Blast category determination).
    
    Ignores Abilities, items, and other effects - only considers stat stages.
    """
    # Look for the base stat value
    alt_keys = [key, key + "_base", key.replace("_", "-"), key.replace("_", " ")]
    base_val = None
    for k in alt_keys:
        if k in pkm and isinstance(pkm[k], (int, float)):
            base_val = pkm[k]
            break
    base = float(base_val or 0)
    
    # Look for stages/boosts
    stages = 0
    stages_container = pkm.get("stages", {})
    if isinstance(stages_container, dict):
        for sk in (stages_key, stages_key.replace("_", "-"), stages_key.replace("_", " ")):
            if sk in stages_container:
                stages = stages_container.get(sk, 0)
                break
    
    # Apply boost multiplier (stages only, no other modifiers)
    if stages >= 0:
        mult = (2.0 + stages) / 2.0
    else:
        mult = 2.0 / (2.0 - stages)
    
    return base * mult


def determine_crit_effective(attacker: Dict, defender: Dict, is_critical: bool, move: Dict) -> bool:
    crit_effective = is_critical
    if defender.get("ability") in ("battle-armor", "shell-armor") or defender.get("lucky_chant"):
        crit_effective = False
    always_crit = {"storm-throw", "frost-breath", "zippy-zap", "surging-strikes", "wicked-blow", "flower-trick"}
    if move.get("name") in always_crit or move.get("always_crit"):
        crit_effective = True
    if attacker.get("ability") == "merciless" and defender.get("status") == "poisoned":
        crit_effective = True
    if attacker.get("laser_focus"):
        crit_effective = True
    return crit_effective


def compute_targets_and_pb(move: Dict, field: Dict, gen: int) -> Tuple[float, float]:
    targets = 1.0
    
    # En mode double, les attaques qui touchent plusieurs adversaires ont une réduction de puissance
    battle_mode = field.get("battle_mode", "single")
    move_targets = move.get("targets", 1)
    
    # Réduction de puissance seulement si :
    # - On est en mode double (2 adversaires sur le terrain)
    # - ET l'attaque touche plusieurs cibles (targets >= 2)
    if battle_mode == "double" and move_targets >= 2:
        targets = 0.75
    elif battle_mode == "single":
        # En mode single, pas de réduction même si l'attaque est multi-target
        targets = 1.0
    elif field.get("battle_royale") and move_targets > 1:
        # Battle Royale : 4 Pokémon sur le terrain
        targets = 0.5
    
    if move.get("parental_bond_second", False):
        pb = 0.25 if gen != 6 else 0.5
    else:
        pb = 1.0
    return targets, pb


def pokeRound(x: float) -> int:
    """Round to nearest integer, ties at .5 round down (Pokémon Gen V+ rounding).
    
    This is the standard rounding used in Pokémon damage calculation.
    For values ending in exactly .5, round DOWN (truncate).
    Examples:
    - 1.4 -> 1
    - 1.5 -> 1  (tie rounds down)
    - 1.6 -> 2
    - 2.5 -> 2  (tie rounds down)
    """
    # Check if it's exactly .5 (within floating point precision)
    if abs(x - math.floor(x) - 0.5) < 1e-9:
        return int(math.floor(x))
    # Otherwise round normally (.5+ goes up)
    return int(math.floor(x + 0.5))


def OF32(n: int) -> int:
    """Overflow to 32-bit signed integer range."""
    n = int(n)
    if n > 2147483647:
        return n - 4294967296
    if n < -2147483648:
        return n + 4294967296
    return n


def OF16(n: int) -> int:
    """Overflow to 16-bit unsigned integer range."""
    n = int(n)
    return n & 0xFFFF


def chainMods(mods: List[int], N: int = 41, M: int = 2097152) -> int:
    """Chain modifiers using fixed-point 4096 arithmetic (Smogon style).
    
    mods: list of modifier values (e.g., [4096, 6144, 5324])
    N: number of initial modifiers that get chained
    M: denominator for final division (2097152 for BP mods, 131072 for final mods)
    
    Returns: chained modifier value (as integer, base 4096)
    """
    if not mods:
        return 4096
    
    result = 4096
    for mod in mods[:N] if len(mods) > N else mods:
        result = result * mod + 2048
        result = int(result / 4096)
    
    return result


if compute_weather_mult is None:
    # fallback local implementation when import not available
    def compute_weather_mult(field: Dict, mv_type: Optional[str], move: Dict) -> Tuple[float, Dict]:
        weather = field.get("weather")
        if field.get("cloud_nine") or field.get("air_lock") or any(p.get("ability") in ("cloud-nine", "air-lock") for p in field.get("pokemon", [])):
            weather = None
        effects = {}
        weather_mult = 1.0
        if not weather:
            return weather_mult, effects
        w = str(weather).lower()
        if w in ("harsh-sunlight", "harsh_sunlight", "harsh sun", "strong-sun", "strong_sun", "sunny-day-strong", "sunny-day"):
            if mv_type == "fire":
                weather_mult = 1.5
            if mv_type == "water":
                weather_mult = 0.5
            effects["prevent_freeze"] = True
            effects["name"] = "harsh-sunlight"
            return weather_mult, effects
        if w in ("sun", "sunny", "sunny-day", "sunny day"):
            if mv_type == "fire" or move.get("name") == "hydro-steam":
                weather_mult = 1.5
            if mv_type == "water" and move.get("name") != "hydro-steam":
                weather_mult = 0.5
            effects["name"] = "sun"
            return weather_mult, effects
        if w in ("rain", "rainy"):
            if mv_type == "water":
                weather_mult = 1.5
            if mv_type == "fire":
                weather_mult = 0.5
            effects["name"] = "rain"
            return weather_mult, effects
        if w in ("sandstorm", "sand-storm"):
            effects["name"] = "sandstorm"
            effects["sandstorm_spdef_boost"] = True
            return weather_mult, effects
        if w in ("hail",):
            effects["name"] = "hail"
            effects["hail_end_of_turn_damage"] = True
            return weather_mult, effects
        if w in ("snow",):
            effects["name"] = "snow"
            effects["snow_def_boost"] = True
            return weather_mult, effects
        return weather_mult, effects


def compute_glaive_rush(defender: Dict) -> float:
    return 2.0 if defender.get("used_glaive_rush_prev_turn") else 1.0


def compute_crit_mult(gen: int, crit_effective: bool) -> float:
    if crit_effective:
        return 2.0 if gen == 5 else 1.5
    return 1.0


def compute_rand_list(random_range: Optional[Iterable[int]], field: Dict) -> List[int]:
    rl = list(random_range or range(85, 101))
    if field.get("pokestar"):
        rl = [100]
    return rl


def compute_stab(att: Dict, mv: Dict, move_type_override: Optional[str] = None) -> float:
    mv_t = move_type_override if move_type_override else mv.get("type")
    if not mv_t:
        return 1.0
    att_types = att.get("types", [])
    adaptability = att.get("ability") == "adaptability"
    is_tera = att.get("is_terastallized", False)
    tera_type = att.get("tera_type")
    orig_types = att.get("orig_types", att_types)
    
    if is_tera and tera_type:
        # Vérifie si l'attaque correspond au type d'origine
        in_orig = mv_t in orig_types
        # Vérifie si l'attaque correspond au type Tera
        is_tera_type = mv_t == tera_type
        
        if in_orig and is_tera_type:
            # Double STAB : type d'origine ET type Tera identiques
            return 2.25 if adaptability else 2.0
        elif in_orig or is_tera_type:
            # STAB simple : type d'origine OU type Tera
            return 2.0 if adaptability else 1.5
        else:
            # Pas de STAB
            return 1.0
    else:
        # Sans Tera : STAB classique
        if mv_t in att_types:
            return 2.0 if adaptability else 1.5
        return 1.0


def compute_burn_mult(attacker: Dict, category: str, move: Dict, gen: int) -> float:
    burn_mult = 1.0
    if attacker.get("status") == "burn" and category == "physical" and attacker.get("ability") != "guts":
        if not (gen >= 6 and move.get("name") == "facade"):
            burn_mult = 0.5
    return burn_mult


def compute_other_z_terashield(attacker: Dict, defender: Dict, field: Dict) -> Tuple[float, float, float]:
    other_mult = attacker.get("other_multiplier", 1.0) * defender.get("other_multiplier", 1.0)
    zmove_mult = attacker.get("zmove_multiplier", 1.0)
    terashield_mult = defender.get("terashield_multiplier", field.get("terashield_multiplier", 1.0)) or 1.0
    return other_mult, zmove_mult, terashield_mult


if compute_terrain_multiplier is None:
    def compute_terrain_multiplier(fld: Dict, mv_type: Optional[str], move: Dict, attacker: Dict, defender: Dict, gen: int) -> Tuple[float, Dict]:
        effects: Dict = {}
        if not mv_type:
            return 1.0, effects
        if not fld:
            return 1.0, effects
        tm = fld.get("terrain_multipliers") or {}
        if mv_type in tm:
            return float(tm.get(mv_type) or 1.0), effects
        if mv_type.lower() in tm:
            return float(tm.get(mv_type.lower()) or 1.0), effects
        terrain_name = (fld.get("terrain") or "").lower()
        grounded_attacker = attacker.get("is_grounded", True)
        grounded_defender = defender.get("is_grounded", True)
        if terrain_name in ("electric", "electric_terrain", "electric terrain"):
            if mv_type == "electric" and grounded_attacker:
                return (1.3 if gen >= 8 else 1.5), {"prevent_sleep": True, "name": "electric"}
            return 1.0, {"prevent_sleep": True, "name": "electric"}
        if terrain_name in ("grassy", "grassy_terrain", "grassy terrain"):
            effects["terrain_heal_fraction"] = 1 / 16.0
            if mv_type == "grass" and grounded_attacker:
                return (1.3 if gen >= 8 else 1.5), effects | {"name": "grassy"}
            if move.get("name") in ("bulldoze", "earthquake", "magnitude"):
                effects["halve_power"] = True
            return 1.0, effects | {"name": "grassy"}
        if terrain_name in ("misty", "misty_terrain", "misty terrain"):
            if mv_type == "dragon" and grounded_defender:
                return 0.5, {"prevent_status": True, "name": "misty", "halve_dragon": True}
            return 1.0, {"prevent_status": True, "name": "misty"}
        if terrain_name in ("psychic", "psychic_terrain", "psychic terrain"):
            if mv_type == "psychic" and grounded_attacker:
                return (1.3 if gen >= 8 else 1.5), {"prevent_priority": True, "name": "psychic"}
            return 1.0, {"prevent_priority": True, "name": "psychic"}
        return 1.0, effects


def compute_base(level: int, power: int, A: float, D: float) -> int:
    numerator = (2 * level) // 5 + 2
    # Use floor for A and D to handle stat boosts correctly
    A_floor = int(math.floor(A))
    D_floor = int(math.floor(D)) if D > 0 else 1
    base1 = int(numerator) * int(power) * A_floor
    base2 = base1 // D_floor
    base = base2 // 50 + 2
    return int(base)


def compute_damage_rolls(
    base: int,
    rand_list: Iterable[int],
    multipliers: Dict[str, float],
    defender_hp: Optional[int],
    terrain_effects: Optional[Dict] = None,
) -> Tuple[List[int], List[Optional[int]]]:
    """Calculate damage for each random roll following Smogon's exact formula.
    
    Based on @smogon/calc Gen 5-9 mechanics:
    - Spread modifier (targets) applied as pokeRound(OF32(baseDamage * 3072) / 4096)
    - Weather modifier applied as pokeRound(OF32(baseDamage * 6144) / 4096)
    - Critical hits applied as Math.floor(OF32(baseDamage * 1.5))
    - Random factor: (baseDamage * random) / 100
    - STAB, Type effectiveness, Burn applied with Math.floor per step
    - Final modifiers (screens, abilities, items) chained with chainMods
    """
    damage_all: List[int] = []
    remaining_hp_all: List[Optional[int]] = []
    
    for r in rand_list:
        baseDamage = int(base)
        
        # Spread modifier (targets)
        if multipliers.get("targets", 1.0) != 1.0:
            baseDamage = pokeRound(OF32(baseDamage * 3072) / 4096)
        
        # Parental Bond (second hit)
        if multipliers.get("pb", 1.0) != 1.0:
            pb_val = multipliers.get("pb", 1.0)
            if pb_val == 0.25:  # Gen 7+
                baseDamage = pokeRound(OF32(baseDamage * 1024) / 4096)
            elif pb_val == 0.5:  # Gen 6
                baseDamage = pokeRound(OF32(baseDamage * 2048) / 4096)
        
        # Weather modifier
        weather = multipliers.get("weather_mult", 1.0)
        if weather == 1.5:
            baseDamage = pokeRound(OF32(baseDamage * 6144) / 4096)
        elif weather == 0.5:
            baseDamage = pokeRound(OF32(baseDamage * 2048) / 4096)
        
        # Glaive Rush (×2)
        if multipliers.get("glaive_rush", 1.0) == 2.0:
            baseDamage = baseDamage * 2
        
        # Critical hit
        crit = multipliers.get("crit_mult", 1.0)
        if crit == 1.5:
            baseDamage = math.floor(OF32(baseDamage * 1.5))
        elif crit == 2.0:
            baseDamage = baseDamage * 2
        
        # Random factor
        damage = math.floor((baseDamage * r) / 100)
        
        # STAB
        stab = multipliers.get("stab", 1.0)
        if stab == 1.5:
            damage = math.floor(damage * 1.5)
        elif stab == 2.0:
            damage = damage * 2
        elif stab == 2.25:
            damage = math.floor(damage * 2.25)
        
        # Type effectiveness (applied per type)
        type_mult = multipliers.get("type_mult", 1.0)
        damage = math.floor(damage * type_mult)
        
        # Misty Terrain Dragon halving is now applied as BP modifier (before base calculation),
        # not as a final damage modifier here
        
        # Burn
        burn = multipliers.get("burn_mult", 1.0)
        if burn == 0.5:
            damage = math.floor(damage * 0.5)
        
        # Final modifiers (screens, abilities, items) - chained
        final_mods = []
        
        # Screens (Reflect/Light Screen/Aurora Veil)
        # Note: These would come from field state, not implemented here yet
        
        # Abilities and items go into final_mods
        # Life Orb, Expert Belt, etc.
        item_mult = multipliers.get("item_mult", 1.0)
        if item_mult != 1.0:
            # Life Orb is 5324/4096
            final_mods.append(int(item_mult * 4096))
        
        # Terrain multiplier is now applied to base power, not as final mod
        # (removed from here per Smogon's implementation)
        
        # Other modifiers
        other = multipliers.get("other_mult", 1.0)
        if other != 1.0:
            final_mods.append(int(other * 4096))
        
        # Apply chained final modifiers
        if final_mods:
            finalMod = chainMods(final_mods, len(final_mods), 131072)
            damage = pokeRound((damage * finalMod) / 4096)
        
        dmg = max(1, int(damage))
        damage_all.append(dmg)
        if defender_hp is not None:
            remaining_hp_all.append(max(0, int(defender_hp) - dmg))
        else:
            remaining_hp_all.append(None)
    return damage_all, remaining_hp_all



def calculate_damage(
    move: Dict,
    attacker: Dict,
    defender: Dict,
    *,
    level: int = 50,
    type_chart: Optional[Dict[str, Dict]] = None,
    field: Optional[Dict] = None,
    defender_hp: Optional[int] = None,
    is_critical: bool = False,
    random_range: Optional[Iterable[int]] = None,
    gen: int = 9,
    debug: bool = False,
) -> Dict:
    """Calculate damages per user's requested formula and return remaining HP per roll.

    Expected keys (non-exhaustive):
    - move: {"power": int, "type": str, "damage_class": "physical"|"special", "targets": int, "name": str, "parental_bond_second": bool}
    - attacker: {"attack": int, "defense": int, "special_attack": int, "special_defense": int, "types": [str], "ability": str, "status": str, "is_terastallized": bool, "tera_type": str, "orig_types": [str], "stages": {stat: stage}, ...}
    - defender: {"defense": int, "special_defense": int, "types": [str], "ability": str, "hp": int, "used_glaive_rush_prev_turn": bool, ...}
    - field: {"weather": "rain"|"sun"|None, "cloud_nine": bool, "air_lock": bool, "battle_royale": bool, "pokestar": bool, ...}

    Return structure contains:
    - damage_all: list of damage ints for each roll (same order as random_range)
    - remaining_hp_all: list of defender_hp - damage for each roll (None if defender_hp unknown)
    - ko_count, ko_chance when defender_hp known
    - base_val (pre-floor float) and multipliers info if debug
    """
    # normalize inputs
    if random_range is None:
        random_range = range(85, 101)
    if field is None:
        field = {}
    # tolerate shorthand field values (user may pass a string or a single-value set/list)
    if not isinstance(field, dict):
        if isinstance(field, str):
            field = {"weather": field}
        else:
            try:
                it = iter(field)
                first = next(it)
                if isinstance(first, str):
                    field = {"weather": first}
                else:
                    field = {}
            except Exception:
                field = {}

    # try load type chart if not provided
    type_chart = load_type_chart_if_missing(type_chart)

    dbg: List[str] = []

    power = move.get("power") or 0
    if power == 0 or move.get("damage_class") == "status":
        return {"damage_all": [], "remaining_hp_all": [], "debug": dbg}

    # Determine critical applicability
    crit_effective = determine_crit_effective(attacker, defender, is_critical, move)

    # Compute offensive/defensive stats
    category = move.get("damage_class", "physical")
    mv_name = (move.get("name") or "").lower()
    
    # Tera Blast : change de type, de catégorie et de puissance selon la téracristallisation
    move_type = move.get("type")
    is_tera_blast = move.get("name") == "tera-blast"
    tera_blast_is_stellar = False
    
    if is_tera_blast and attacker.get("is_terastallized"):
        # Prend le type Tera
        tera_type = attacker.get("tera_type")
        if tera_type:
            move_type = tera_type
            
            # Cas spécial : Stellar type
            if tera_type == "stellar":
                tera_blast_is_stellar = True
                # La puissance passe à 100 au lieu de 80
                power = 100
        
        # Choisir la catégorie (physique vs spéciale) basé UNIQUEMENT sur les stats de base + stages
        # Ignore les talents (Huge Power), objets (Choice Band), etc.
        atk_with_stages = compute_stat_with_stages_only(attacker, "attack", "attack")
        spa_with_stages = compute_stat_with_stages_only(attacker, "special_attack", "special_attack")
        
        if atk_with_stages > spa_with_stages:
            category = "physical"
        else:
            category = "special"
    
    # Apply held item stat modifiers BEFORE computing effective stats so that
    # items like Choice Band or Thick Club affect the computed A/D values.
    # Also get modified power from items like Muscle Band and type-boost items (Plates).
    if 'apply_item_stat_modifiers' in globals() and apply_item_stat_modifiers:
        try:
            attacker, defender, power = apply_item_stat_modifiers(attacker, defender, move)
        except Exception as e:
            pass

    # Special-case: Ball'Météo (Weather Ball variant requested by user)
    # Behaviour: base 50 special Normal. If any weather is active (and not neutralized
    # by Cloud Nine/Air Lock), its power is doubled and its type changes depending on
    # the weather:
    #  - Sun / harsh sunlight -> Fire
    #  - Rain -> Water
    #  - Hail / Snow -> Ice
    #  - Sandstorm -> Rock
    #  - Fog -> remains Normal (but still doubled power)
    try:
        mv_name_raw = move.get("name") or ""
        # normalize: lowercase, remove non-alphanum
        mv_name_norm = "".join(ch for ch in mv_name_raw.lower() if ch.isalnum())
        # match common variants: "weather-ball", "ball-meteo", "ball'météo", etc.
        if (
            mv_name_norm in ("ballmeteo", "ballmete", "weatherball")
            or ("ball" in mv_name_norm and "meteo" in mv_name_norm)
            or "weather" in mv_name_norm
        ):
            # enforce special category and ensure default base power is 50 if not provided
            move.setdefault("damage_class", "special")
            # Use provided power as baseline if given, otherwise 50
            if not move.get("power"):
                power = 50
            # Determine if weather is active (respect Cloud Nine / Air Lock abilities)
            weather_field = field.get("weather") if isinstance(field, dict) else None
            if field.get("cloud_nine") or field.get("air_lock") or any(p.get("ability") in ("cloud-nine", "air-lock") for p in field.get("pokemon", [])):
                weather_field = None
            if weather_field:
                w = str(weather_field).lower()
                # double power
                power = int(math.floor(power * 2))
                # map weather to move type
                if any(x in w for x in ("harsh", "sun", "sunny", "strong")):
                    move_type = "fire"
                elif "rain" in w:
                    move_type = "water"
                elif "hail" in w or "snow" in w:
                    move_type = "ice"
                elif "sand" in w:
                    move_type = "rock"
                elif "fog" in w:
                    move_type = "normal"
                else:
                    move_type = move.get("type") or "normal"
                # update move dict so downstream logic observes the changes
                move["type"] = move_type
                move["power"] = power
    except Exception:
        # Defensive: never let this break damage calculation
        pass

    if category == "physical":
        # Special-case: Body Press (fr: Big Splash) uses the attacker's DEFENSE as its
        # attacking stat instead of ATTACK.
        if mv_name in ("body-press", "body press", "bodypress"):
            A = compute_effective_stat(attacker, "defense", "defense", True, crit_effective)
        else:
            A = compute_effective_stat(attacker, "attack", "attack", True, crit_effective)
        D = compute_effective_stat(defender, "defense", "defense", False, crit_effective)
    else:
        A = compute_effective_stat(attacker, "special_attack", "special_attack", True, crit_effective)
        D = compute_effective_stat(defender, "special_defense", "special_defense", False, crit_effective)
    if D == 0:
        D = 1.0

    # --- Ability adjustments must run before base is computed so that
    # abilities that change raw stats (Huge/Pure Power, Guts, etc.) affect base.
    ability_effects = {}
    ability_multipliers = {}
    ability_type_mult = 1.0  # Pour stocker le type_mult modifié par les talents
    if 'apply_ability_effects' in globals() and apply_ability_effects:
        try:
            # Pass a temporary multipliers dict; we'll merge its results later.
            ability_multipliers, A, D, ability_type_mult, ability_effects = apply_ability_effects(
                attacker, defender, move, field, {}, A, D, 1.0, gen
            )
        except Exception:
            ability_effects = {}
            ability_multipliers = {}
            ability_type_mult = 1.0
        # If ability handlers modified the move (e.g. Technician increases base power),
        # refresh the local `power` variable from the move dict so downstream code
        # uses the updated base power.
        try:
            power = int(move.get("power") or power)
        except Exception:
            pass

    # simple multipliers
    targets, pb = compute_targets_and_pb(move, field, gen)
    weather_mult, weather_effects = compute_weather_mult(field, move_type, move)
    glaive_rush = compute_glaive_rush(defender)
    crit_mult = compute_crit_mult(gen, crit_effective)
    rand_list = compute_rand_list(random_range, field)

    # STAB / type / burn / others
    stab = compute_stab(attacker, move, move_type_override=move_type if is_tera_blast else None)
    mv_type = move_type
    type_mult = type_effectiveness(mv_type, defender.get("types", []), type_chart)
    
    # Tera Blast Stellar : super efficace contre Pokémon téracristallisés, neutre sinon
    if tera_blast_is_stellar:
        if defender.get("is_terastallized"):
            type_mult = 2.0  # Super efficace contre cibles téracristallisées
        else:
            type_mult = 1.0  # Neutre contre cibles non téracristallisées
    
    # Ring Target
    if defender.get("ring_target") and type_mult == 0.0:
        type_mult = 1.0
    # Scrappy
    if attacker.get("ability") == "scrappy" and mv_type in ("normal", "fighting") and "ghost" in (defender.get("types") or []):
        type_mult = 1.0
    # Freeze-Dry
    if move.get("name") == "freeze-dry" and "water" in (defender.get("types") or []):
        type_mult = max(type_mult, 2.0)
    # Flying Press (both type and flying)
    if move.get("name") == "flying-press":
        type_mult = type_mult * type_effectiveness("flying", defender.get("types", []), type_chart)
    
    # Tera Shell: Force all damaging moves to be not very effective when at full HP
    if ability_effects.get("tera_shell_active") and type_mult > 0:
        type_mult = 0.5
    
    # Apply ability type mult modifications (Levitate immunity, etc.)
    # If ability returned 0.0 (immunity), override type_mult
    if ability_type_mult == 0.0:
        type_mult = 0.0

    burn_mult = compute_burn_mult(attacker, category, move, gen)
    other_mult, zmove_mult, terashield_mult = compute_other_z_terashield(attacker, defender, field)

    # Compute grounded status for attacker and defender (if not explicitly set)
    if "is_grounded" not in attacker and is_grounded is not None:
        attacker["is_grounded"] = is_grounded(attacker, field)
    if "is_grounded" not in defender and is_grounded is not None:
        defender["is_grounded"] = is_grounded(defender, field)

    terrain_mult, terrain_effects = compute_terrain_multiplier(field, mv_type, move, attacker, defender, gen)

    # Apply weather stat modifications (sandstorm increases Rock Sp. Def, snow increases Ice Def)
    if weather_effects.get("sandstorm_spdef_boost"):
        if "rock" in (defender.get("types") or []) and category == "special":
            D = float(D) * 1.5
    if weather_effects.get("snow_def_boost"):
        if "ice" in (defender.get("types") or []) and category == "physical":
            D = float(D) * 1.5

    # If grassy terrain halves certain move powers, adjust power before base
    if terrain_effects.get("halve_power") and terrain_effects.get("name") != "misty":
        # Grassy Terrain halves Earthquake/Bulldoze/Magnitude (BP modifier)
        power = int(math.floor(power * 0.5))
    
    # Misty Terrain Dragon halving: apply as BP modifier (0.5x power)
    if terrain_effects.get("halve_dragon"):
        power = OF16(max(1, pokeRound((power * 2048) / 4096)))
    
    # Apply terrain multiplier as base power modifier (Smogon Gen 7+)
    # Terrain boosts (Electric/Grassy/Psychic) are BP mods (NOT Misty, handled above)
    if terrain_mult != 1.0 and terrain_effects.get("name") != "misty":
        # Use chainMods for terrain boost like Smogon does
        # terrainMultiplier = gen.num > 7 ? 5325 : 6144
        terrain_bp_mod = 5325 if gen >= 8 else 6144  # 1.3x for Gen 8+, 1.5x for Gen 6-7
        power = OF16(max(1, pokeRound((power * terrain_bp_mod) / 4096)))

    base = compute_base(level, power, A, D)

    multipliers = {
        "targets": targets,
        "pb": pb,
        "weather_mult": weather_mult,
        "glaive_rush": glaive_rush,
        "stab": stab,
        "burn_mult": burn_mult,
        "terrain_mult": terrain_mult,
        "other_mult": other_mult,
        "zmove_mult": zmove_mult,
        "terashield_mult": terashield_mult,
        "type_mult": type_mult,
        "crit_mult": crit_mult,
    }
    # Merge any multipliers returned by the early ability pass
    # (e.g. Sheer Force, Tough Claws set other_mult)
    if isinstance(ability_multipliers, dict):
        for k, v in ability_multipliers.items():
            multipliers[k] = float(multipliers.get(k, 1.0)) * float(v)
    # Compute item damage multiplier (post-random multipliers like Expert Belt, Life Orb, etc.)
    try:
        if 'compute_item_damage_multiplier' in globals() and compute_item_damage_multiplier:
            item_mult, other_item_mult, item_effects = compute_item_damage_multiplier(
                attacker.get('item'),
                defender.get('item'),
                move,
                attacker,
                defender,
                type_mult,
                category,
                attacker.get('consumed_items', []),
                defender.get('consumed_items', []),
            )
            multipliers['item_mult'] = float(multipliers.get('item_mult', 1.0)) * float(item_mult)
            multipliers['other_mult'] = float(multipliers.get('other_mult', 1.0)) * float(other_item_mult)
            # Merge item effects into ability_effects for debug/consumers
            if item_effects:
                if isinstance(ability_effects, dict):
                    ability_effects.update(item_effects)
                else:
                    ability_effects = item_effects
    except Exception:
        # ignore item computation errors
        pass
    # If sniper was flagged earlier, keep that in ability_effects for debug
    if attacker.get("ability") and str(attacker.get("ability")).lower().replace("_", "-").replace(" ", "-") == "sniper":
        ability_effects.setdefault("sniper", True)

    damage_all, remaining_hp_all = compute_damage_rolls(base, rand_list, multipliers, defender_hp if defender_hp is not None else defender.get("hp"), terrain_effects)

    result = {"damage_all": damage_all, "remaining_hp_all": remaining_hp_all, "base_val": base}
    # Merge weather and terrain effect flags for consumers
    combined_effects: Dict = {}
    if isinstance(weather_effects, dict):
        combined_effects.update(weather_effects)
    if isinstance(terrain_effects, dict):
        combined_effects.update(terrain_effects)
    # ability effects (may have been set above)
    if isinstance(ability_effects, dict):
        combined_effects.update(ability_effects)
    if combined_effects:
        result["effects"] = combined_effects
    hp_val = defender_hp if defender_hp is not None else defender.get("hp")
    if hp_val is not None:
        ko_count = sum(1 for d in damage_all if d >= hp_val)
        result.update({"defender_hp": hp_val, "ko_count": ko_count, "ko_chance": ko_count / len(damage_all) * 100.0})

    if debug:
        result["debug"] = {
            "power": power,
            "base": base,
            "A": A,
            "D": D,
            "type_mult": type_mult,
            "stab": stab,
            "crit_mult": crit_mult,
            "weather_mult": weather_mult,
            "burn_mult": burn_mult,
            "terrain_mult": terrain_mult,
            "targets": targets,
            "pb": pb,
            "multipliers": multipliers,
            "effects": combined_effects,
            "ability_effects": ability_effects,
        }

    return result


if __name__ == "__main__":
    # quick demo using the user's example (attacker == defender)
    move = {"name": "ice_move", "power": 110, "type": "ice", "damage_class": "physical", "targets": 1}
    #Abomasnow 
    attacker = {
        "hp": 197,
        "attack": 87,
        "defense": 95,
        "special_attack": 154,
        "special_defense": 105,
        "speed": 85,
        "types": ["ice", "grass"],
        "ability": None,
        "status": None,
    }
    defender = dict(attacker)

    # call with minimal required arguments only (function will auto-load type chart and read defender HP)
    out = calculate_damage(move, attacker, defender, field={"weather": "snow"})

    def pretty_print_result(res: Dict, mv: Dict, atk: Dict, defn: Dict) -> None:
        print("\n" + "=" * 60)
        print("Damage simulation — summary")
        print("=" * 60)
        print(f"Move: {mv.get('name')} | Type: {mv.get('type')} | Power: {mv.get('power')} | Category: {mv.get('damage_class')}")
        print(f"Attacker types: {atk.get('types')} | Defender types: {defn.get('types')}")
        base = res.get('base_val') or res.get('base') or 0.0
        print(f"Base (pre-multipliers/random): {base:.4f}")
        dbg = res.get('debug') or {}
        if dbg:
            print(f"A: {dbg.get('A')}  D: {dbg.get('D')}  STAB: {dbg.get('stab')}  Type mult: {dbg.get('type_mult')}")
        print("\nRoll%  Damage   Remaining HP")
        print("----  -------  -------------")
        rolls = list(range(85, 101))
        for r, dmg, rem in zip(rolls, res.get('damage_all', []), res.get('remaining_hp_all', [])):
            rem_str = str(rem) if rem is not None else "?"
            print(f"{r:3d}%   {dmg:6d}   {rem_str:13}")

        dmg_all = res.get('damage_all', [])
        if dmg_all:
            print("\nSummary:")
            print(f"  Min damage: {min(dmg_all)}")
            print(f"  Max damage: {max(dmg_all)}")
        if 'ko_chance' in res:
            print(f"  KO chance: {res.get('ko_chance'):.1f}% ({res.get('ko_count')}/{len(dmg_all)})")
        print("=" * 60 + "\n")

    # Uncomment to test:
    # pretty_print_result(out, move, attacker, defender)

