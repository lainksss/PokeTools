"""
Test Protosynthesis ability — Flutter Mane's signature ability.

Protosynthesis boosts the highest stat (other than HP) by 30%, or 50% for Speed,
when in harsh sunlight or holding Booster Energy.

All tests are in double battles at level 100.
"""

import json
from pathlib import Path

from backend.calculate_damages.calculate_damages import calculate_damage


# Load Pokemon data
POKEMON_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "all_pokemon.json"
with open(POKEMON_DATA_PATH, "r", encoding="utf-8") as f:
    POKEMON_DATA = json.load(f)


def calculate_stat(base: int, iv: int, ev: int, level: int, nature_mult: float = 1.0, is_hp: bool = False) -> int:
    """Calculate a stat using the standard Pokemon formula."""
    if is_hp:
        return int((2 * base + iv + ev // 4) * level / 100) + level + 10
    else:
        base_stat = int((2 * base + iv + ev // 4) * level / 100) + 5
        return int(base_stat * nature_mult)


def get_pokemon_stats(species: str, level: int, evs: dict, ivs: dict = None, natures: dict = None, ability: str = None, item: str = None):
    """Retrieve and calculate Pokemon stats from the JSON file."""
    if ivs is None:
        ivs = {"hp": 31, "attack": 31, "defense": 31, "special-attack": 31, "special-defense": 31, "speed": 31}
    
    if natures is None:
        natures = {"hp": 1.0, "attack": 1.0, "defense": 1.0, "special-attack": 1.0, "special-defense": 1.0, "speed": 1.0}
    
    pokemon = POKEMON_DATA[species]
    base_stats = pokemon["base_stats"]
    
    stats = {
        "species": species,
        "level": level,
        "types": pokemon["types"],
        "hp": calculate_stat(base_stats["hp"], ivs.get("hp", 31), evs.get("hp", 0), level, is_hp=True),
        "attack": calculate_stat(base_stats["attack"], ivs.get("attack", 31), evs.get("attack", 0), level, natures.get("attack", 1.0)),
        "defense": calculate_stat(base_stats["defense"], ivs.get("defense", 31), evs.get("defense", 0), level, natures.get("defense", 1.0)),
        "special_attack": calculate_stat(base_stats["special-attack"], ivs.get("special-attack", 31), evs.get("special-attack", 0), level, natures.get("special-attack", 1.0)),
        "special_defense": calculate_stat(base_stats["special-defense"], ivs.get("special-defense", 31), evs.get("special-defense", 0), level, natures.get("special-defense", 1.0)),
        "speed": calculate_stat(base_stats["speed"], ivs.get("speed", 31), evs.get("speed", 0), level, natures.get("speed", 1.0)),
        "ability": ability,
        "item": item,
        "is_terastallized": False,
    }
    
    return stats


def test_protosynthesis_flutter_mane_dazzling_gleam_with_harsh_sunlight():
    """4 SpA Protosynthesis Flutter Mane Dazzling Gleam vs. 0 HP / 0 SpD Bulbasaur (harsh sunlight, doubles, 2-target move)
    Expected: (77, 78, 79, 80, 81, 81, 83, 84, 84, 85, 86, 87, 88, 89, 90, 91)
    """
    print("\n" + "="*80)
    print("TEST 1: 4 SpA Protosynthesis Flutter Mane Dazzling Gleam vs. 0 HP / 0 SpD Bulbasaur")
    print("        (harsh sunlight, doubles, 2-target move)")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="flutter-mane",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 4, "special-defense": 0, "speed": 0},
        ability="protosynthesis"
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}
    )
    
    move = {
        "name": "dazzling-gleam",
        "power": 80,
        "type": "fairy",
        "damage_class": "special",
        "targets": 2
    }
    
    field = {
        "weather": "harsh-sunlight",
        "battle_mode": "double"
    }
    
    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        field=field,
        level=100,
        random_range=range(85, 101),
        debug=False,
    )
    
    expected = (77, 78, 79, 80, 81, 81, 83, 84, 84, 85, 86, 87, 88, 89, 90, 91)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    
    assert actual == expected, f"Mismatch: expected {expected}, got {actual}"


def test_protosynthesis_flutter_mane_shadow_ball_with_harsh_sunlight():
    """4 SpA Protosynthesis Flutter Mane Shadow Ball vs. 0 HP / 0 SpD Bulbasaur (harsh sunlight, doubles)
    Expected: (207, 210, 211, 214, 217, 219, 222, 223, 226, 229, 231, 234, 237, 238, 241, 244)
    """
    print("\n" + "="*80)
    print("TEST 2: 4 SpA Protosynthesis Flutter Mane Shadow Ball vs. 0 HP / 0 SpD Bulbasaur")
    print("        (harsh sunlight, doubles)")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="flutter-mane",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 4, "special-defense": 0, "speed": 0},
        ability="protosynthesis"
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}
    )
    
    move = {
        "name": "shadow-ball",
        "power": 80,
        "type": "ghost",
        "damage_class": "special",
        "targets": 1
    }
    
    field = {
        "weather": "harsh-sunlight",
        "battle_mode": "double"
    }
    
    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        field=field,
        level=100,
        random_range=range(85, 101),
        debug=False,
    )
    
    expected = (207, 210, 211, 214, 217, 219, 222, 223, 226, 229, 231, 234, 237, 238, 241, 244)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    
    assert actual == expected, f"Mismatch: expected {expected}, got {actual}"


def test_flutter_mane_shadow_ball_without_protosynthesis():
    """4 SpA Flutter Mane Shadow Ball vs. 0 HP / 0 SpD Bulbasaur (baseline, doubles, no Protosynthesis)
    Expected: (160, 162, 163, 165, 168, 169, 171, 172, 175, 177, 178, 180, 183, 184, 186, 189)
    """
    print("\n" + "="*80)
    print("TEST 3: 4 SpA Flutter Mane Shadow Ball vs. 0 HP / 0 SpD Bulbasaur")
    print("        (baseline, doubles, NO Protosynthesis)")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="flutter-mane",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 4, "special-defense": 0, "speed": 0},
        ability=None
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}
    )
    
    move = {
        "name": "shadow-ball",
        "power": 80,
        "type": "ghost",
        "damage_class": "special",
        "targets": 1
    }
    
    field = {
        "weather": None,
        "battle_mode": "double"
    }
    
    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        field=field,
        level=100,
        random_range=range(85, 101),
        debug=False,
    )
    
    expected = (160, 162, 163, 165, 168, 169, 171, 172, 175, 177, 178, 180, 183, 184, 186, 189)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    
    assert actual == expected, f"Mismatch: expected {expected}, got {actual}"


def test_flutter_mane_dazzling_gleam_without_protosynthesis():
    """4 SpA Flutter Mane Dazzling Gleam vs. 0 HP / 0 SpD Bulbasaur (baseline, doubles, 2-target, no Protosynthesis)
    Expected: (59, 60, 60, 61, 62, 63, 63, 64, 65, 66, 66, 67, 68, 69, 69, 70)
    """
    print("\n" + "="*80)
    print("TEST 4: 4 SpA Flutter Mane Dazzling Gleam vs. 0 HP / 0 SpD Bulbasaur")
    print("        (baseline, doubles, 2-target move, NO Protosynthesis)")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="flutter-mane",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 4, "special-defense": 0, "speed": 0},
        ability=None
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}
    )
    
    move = {
        "name": "dazzling-gleam",
        "power": 80,
        "type": "fairy",
        "damage_class": "special",
        "targets": 2
    }
    
    field = {
        "weather": None,
        "battle_mode": "double"
    }
    
    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        field=field,
        level=100,
        random_range=range(85, 101),
        debug=False,
    )
    
    expected = (59, 60, 60, 61, 62, 63, 63, 64, 65, 66, 66, 67, 68, 69, 69, 70)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    
    assert actual == expected, f"Mismatch: expected {expected}, got {actual}"


def test_protosynthesis_flutter_mane_shadow_ball_vs_flutter_mane():
    """4 SpA Protosynthesis Flutter Mane Shadow Ball vs. 0 HP / 4 SpD Flutter Mane (harsh sunlight, doubles)
    Expected: (224, 228, 230, 234, 236, 240, 240, 242, 246, 248, 252, 254, 258, 260, 264, 266)
    """
    print("\n" + "="*80)
    print("TEST 5: 4 SpA Protosynthesis Flutter Mane Shadow Ball vs. 0 HP / 4 SpD Flutter Mane")
    print("        (harsh sunlight, doubles)")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="flutter-mane",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 4, "special-defense": 0, "speed": 0},
        ability="protosynthesis"
    )
    
    defender = get_pokemon_stats(
        species="flutter-mane",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 4, "speed": 0}
    )
    
    move = {
        "name": "shadow-ball",
        "power": 80,
        "type": "ghost",
        "damage_class": "special",
        "targets": 1
    }
    
    field = {
        "weather": "harsh-sunlight",
        "battle_mode": "double"
    }
    
    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        field=field,
        level=100,
        random_range=range(85, 101),
        debug=False,
    )
    
    expected = (224, 228, 230, 234, 236, 240, 240, 242, 246, 248, 252, 254, 258, 260, 264, 266)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    
    assert actual == expected, f"Mismatch: expected {expected}, got {actual}"
