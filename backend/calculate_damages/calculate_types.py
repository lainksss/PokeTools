from typing import Dict, Iterable, Optional


def get_type_breakdown(move_type: str, defender_types: Iterable[str], type_chart: Optional[Dict[str, Dict]] = None) -> Dict[str, float]:
    """Return a breakdown mapping each defender type to its multiplier against move_type.

    The returned dict maps defender_type -> multiplier (2.0, 0.5, 0.0 or 1.0).
    This centralises special-case checks; callers may apply additional field-specific rules.
    """
    breakdown: Dict[str, float] = {}
    if not type_chart or not move_type:
        for d in defender_types:
            breakdown[d] = 1.0
        return breakdown

    for d in defender_types:
        info = type_chart.get(d, {})
        # Prefer canonical PokeAPI-style fields if present
        if "no_damage_from" in info and move_type in info.get("no_damage_from", []):
            breakdown[d] = 0.0
            continue
        if "double_damage_from" in info and move_type in info.get("double_damage_from", []):
            breakdown[d] = 2.0
            continue
        if "half_damage_from" in info and move_type in info.get("half_damage_from", []):
            breakdown[d] = 0.5
            continue
        # Fallback to repo-specific keys
        if move_type in info.get("immune_to", []):
            breakdown[d] = 0.0
            continue
        if move_type in info.get("weak_to", []):
            breakdown[d] = 2.0
            continue
        if move_type in info.get("resistant_to", []):
            breakdown[d] = 0.5
            continue
        # Default neutral
        breakdown[d] = 1.0

    return breakdown


def type_effectiveness(move_type: str, defender_types: Iterable[str], type_chart: Optional[Dict[str, Dict]] = None) -> float:
    """Return the combined type effectiveness multiplier for a move against defender types.

    Multiplier is the product of per-type multipliers (so dual types naturally combine).
    If any per-type multiplier is 0.0 the function returns 0.0 immediately.
    """
    breakdown = get_type_breakdown(move_type, defender_types, type_chart)
    total = 1.0
    for d, m in breakdown.items():
        if m == 0.0:
            return 0.0
        total *= m
    return total
