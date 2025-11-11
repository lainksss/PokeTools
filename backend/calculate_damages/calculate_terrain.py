from typing import Dict, Optional, Tuple


def compute_terrain_multiplier(field: Dict, mv_type: Optional[str], move: Dict, attacker: Dict, defender: Dict, gen: int = 9) -> Tuple[float, Dict]:
    """Return (multiplier, effects) for terrain.

    effects includes flags like 'terrain_heal_fraction', 'halve_power', 'prevent_priority'.
    """
    terrain = field.get("terrain")
    if field.get("gravity"):
        terrain = None
    effects = {}
    terrain_mult = 1.0
    if not terrain:
        return terrain_mult, effects

    t = str(terrain).lower()

    if t in ("electric",):
        if mv_type == "electric" and attacker.get("is_grounded", True):
            terrain_mult = 1.3
        effects["name"] = "electric"
        return terrain_mult, effects

    if t in ("grassy", "grassy-terrain", "grassy terrain"):
        # grassy terrain heals grounded mons each turn: 1/16 in Gen9? earlier gens 1/16; we just report a flag
        effects["terrain_heal_fraction"] = 1/16
        if mv_type == "grass" and attacker.get("is_grounded", True):
            terrain_mult = 1.3
        # Halve power of Earthquake, Bulldoze, and Magnitude
        move_name = move.get("name", "").lower()
        if move_name in ("earthquake", "bulldoze", "magnitude"):
            terrain_mult *= 0.5
            effects["halve_power"] = True
        effects["name"] = "grassy"
        return terrain_mult, effects

    if t in ("misty",):
        # misty prevents status and halves Dragon power on grounded targets in Gen9? historically half Dragon
        if mv_type == "dragon" and defender.get("is_grounded", True):
            terrain_mult = 0.5
            effects["halve_power"] = True
        effects["name"] = "misty"
        effects["prevent_status"] = True
        return terrain_mult, effects

    if t in ("psychic",):
        if mv_type == "psychic" and attacker.get("is_grounded", True):
            terrain_mult = 1.3
        effects["name"] = "psychic"
        return terrain_mult, effects

    return terrain_mult, effects
