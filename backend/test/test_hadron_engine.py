"""
Test Hadron Engine ability — Miraidon's signature ability.

Hadron Engine boosts Sp. Atk by ~33% (factor 5461/4096) when Electric Terrain is active.

Test cases provided by user with expected damage rolls:
- With Electric Terrain: Volt Switch 120-141
- With Electric Terrain: Draco Meteor 343-405
- Without terrain: Volt Switch 69-82
"""

import json
from pathlib import Path

from calculate_damages.calculate_damages import calculate_damage


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


def get_pokemon_stats(species: str, level: int, evs: dict, ivs: dict = None, natures: dict = None, ability: str = None):
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
        "item": None,
        "is_terastallized": False,
    }
    
    return stats


def test_hadron_engine_volt_switch_with_terrain():
    """0 SpA Hadron Engine Miraidon Volt Switch vs. 0 HP / 0 SpD Bulbasaur in Electric Terrain: 120-141"""
    print("\n" + "="*80)
    print("TEST: 0 SpA Hadron Engine Miraidon Volt Switch vs. 0 HP / 0 SpD Bulbasaur in Electric Terrain")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="miraidon",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        ability="hadron-engine"
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}
    )
    
    move = {
        "name": "volt-switch",
        "power": 70,
        "type": "electric",
        "damage_class": "special",
    }
    
    field = {
        "terrain": "electric",
        "battle_mode": "singles"
    }
    
    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        field=field,
        level=100,
        random_range=range(85, 101),
        debug=True,
    )
    
    # Expected rolls from user: (120, 121, 123, 124, 126, 127, 128, 129, 131, 132, 134, 135, 137, 138, 140, 141)
    expected = (120, 121, 123, 124, 126, 127, 128, 129, 131, 132, 134, 135, 137, 138, 140, 141)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Range: {min(actual) if actual else 0}-{max(actual) if actual else 0}")
    
    assert actual == expected


def test_hadron_engine_draco_meteor_with_terrain():
    """0 SpA Hadron Engine Miraidon Draco Meteor vs. 0 HP / 0 SpD Bulbasaur in Electric Terrain: 343-405"""
    print("\n" + "="*80)
    print("TEST: 0 SpA Hadron Engine Miraidon Draco Meteor vs. 0 HP / 0 SpD Bulbasaur in Electric Terrain")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="miraidon",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        ability="hadron-engine"
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}
    )
    
    move = {
        "name": "draco-meteor",
        "power": 130,
        "type": "dragon",
        "damage_class": "special",
    }
    
    field = {
        "terrain": "electric",
        "battle_mode": "singles"
    }
    
    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        field=field,
        level=100,
        random_range=range(85, 101),
        debug=True,
    )
    
    # Expected rolls from user: (343, 348, 351, 355, 360, 364, 367, 372, 376, 379, 384, 388, 391, 396, 400, 405)
    expected = (343, 348, 351, 355, 360, 364, 367, 372, 376, 379, 384, 388, 391, 396, 400, 405)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Range: {min(actual) if actual else 0}-{max(actual) if actual else 0}")
    
    assert actual == expected


def test_hadron_engine_volt_switch_without_terrain():
    """0 SpA Miraidon Volt Switch vs. 0 HP / 0 SpD Bulbasaur (WITHOUT Electric Terrain): 69-82"""
    print("\n" + "="*80)
    print("TEST: 0 SpA Miraidon Volt Switch vs. 0 HP / 0 SpD Bulbasaur (NO Electric Terrain)")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="miraidon",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        ability="hadron-engine"
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}
    )
    
    move = {
        "name": "volt-switch",
        "power": 70,
        "type": "electric",
        "damage_class": "special",
    }
    
    field = {
        "terrain": None,  # No terrain active
        "battle_mode": "singles"
    }
    
    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        field=field,
        level=100,
        random_range=range(85, 101),
        debug=True,
    )
    
    # Expected rolls from user: (69, 70, 71, 72, 72, 74, 75, 75, 76, 77, 78, 78, 79, 80, 81, 82)
    expected = (69, 70, 71, 72, 72, 74, 75, 75, 76, 77, 78, 78, 79, 80, 81, 82)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Range: {min(actual) if actual else 0}-{max(actual) if actual else 0}")
    
    assert actual == expected

