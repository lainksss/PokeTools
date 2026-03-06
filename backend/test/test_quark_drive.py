"""
Test Quark Drive ability — Iron Bundle's signature ability.

Quark Drive boosts the highest stat by 30% (or 50% for Speed) when Electric Terrain is active
or the Pokémon is holding Booster Energy.

Test cases provided by user with exact expected damage rolls:
- With Electric Terrain: 252 SpA Icy Wind (2-target, doubles): 240-284
- With Electric Terrain: 252 SpA Volt Switch (1-target, doubles): 88-104
- With Electric Terrain: 0 Atk Volt Tackle defense test (1-target, doubles): 104-124
- Without terrain: 0 SpA Icy Wind baseline (2-target, doubles): 152-182
- Without terrain: 0 SpA Volt Switch baseline (1-target, doubles): 43-51
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


def test_quark_drive_icy_wind_with_electric_terrain():
    """252 SpA Quark Drive Iron Bundle Icy Wind (2-target) vs. 0 HP / 0 SpD Bulbasaur in Electric Terrain: 240-284"""
    print("\n" + "="*80)
    print("TEST 1: 252 SpA Quark Drive Iron Bundle Icy Wind vs. 0 HP / 0 SpD Bulbasaur in Electric Terrain")
    print("Doubles, Level 100, Icy Wind has 2 targets (multi-target move)")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="iron-bundle",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 252, "special-defense": 0, "speed": 0},
        ability="quark-drive"
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}
    )
    
    move = {
        "name": "icy-wind",
        "power": 55,
        "type": "ice",
        "damage_class": "special",
        "targets": 2,  # Icy Wind hits both opponents in doubles
    }
    
    field = {
        "terrain": "electric-terrain",
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
    
    # Expected rolls from user: (240, 242, 246, 248, 252, 254, 258, 260, 264, 266, 270, 272, 276, 278, 282, 284)
    expected = (240, 242, 246, 248, 252, 254, 258, 260, 264, 266, 270, 272, 276, 278, 282, 284)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Range: {min(actual) if actual else 0}-{max(actual) if actual else 0}")
    
    assert actual == expected, f"Expected {expected}, got {actual}"


def test_quark_drive_volt_switch_with_electric_terrain():
    """252 SpA Quark Drive Iron Bundle Volt Switch (1-target) vs. 0 HP / 0 SpD Bulbasaur in Electric Terrain: 88-104"""
    print("\n" + "="*80)
    print("TEST 2: 252 SpA Quark Drive Iron Bundle Volt Switch vs. 0 HP / 0 SpD Bulbasaur in Electric Terrain")
    print("Doubles, Level 100, Volt Switch has 1 target (single-target move)")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="iron-bundle",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 252, "special-defense": 0, "speed": 0},
        ability="quark-drive"
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
        "targets": 1,  # Volt Switch is single-target
    }
    
    field = {
        "terrain": "electric-terrain",
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
    
    # Expected rolls from user: (88, 89, 90, 91, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104)
    expected = (88, 89, 90, 91, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Range: {min(actual) if actual else 0}-{max(actual) if actual else 0}")
    
    assert actual == expected, f"Expected {expected}, got {actual}"


def test_quark_drive_spark_defense_with_electric_terrain():
    """0 Atk Iron Bundle Spark vs. 0 HP / 252 Def Quark Drive Iron Bundle in Electric Terrain: 56-68"""
    print("\n" + "="*80)
    print("TEST 3: 0 Atk Iron Bundle Spark vs. 0 HP / 252 Def Quark Drive Iron Bundle in Electric Terrain")
    print("Doubles, Level 100, Spark has 1 target (single-target move), attacker NO Quark Drive, defender WITH Quark Drive")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="iron-bundle",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        ability=None
    )
    
    defender = get_pokemon_stats(
        species="iron-bundle",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 252, "special-attack": 0, "special-defense": 0, "speed": 0},
        ability="quark-drive"
    )
    
    move = {
        "name": "spark",
        "power": 65,
        "type": "electric",
        "damage_class": "physical",
        "targets": 1,  # Spark is single-target
    }
    
    field = {
        "terrain": "electric-terrain",
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
    
    # Expected rolls from user: (56, 58, 58, 58, 60, 60, 60, 62, 62, 62, 64, 64, 64, 66, 66, 68)
    expected = (56, 58, 58, 58, 60, 60, 60, 62, 62, 62, 64, 64, 64, 66, 66, 68)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Range: {min(actual) if actual else 0}-{max(actual) if actual else 0}")
    
    assert actual == expected, f"Expected {expected}, got {actual}"


def test_quark_drive_icy_wind_baseline_without_terrain():
    """0 SpA Iron Bundle Icy Wind (2-target) vs. 0 HP / 0 SpD Bulbasaur (NO Electric Terrain): 152-182"""
    print("\n" + "="*80)
    print("TEST 4: 0 SpA Iron Bundle Icy Wind vs. 0 HP / 0 SpD Bulbasaur (NO Electric Terrain)")
    print("Doubles, Level 100, Icy Wind has 2 targets (multi-target move), NO ability")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="iron-bundle",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        ability=None
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}
    )
    
    move = {
        "name": "icy-wind",
        "power": 55,
        "type": "ice",
        "damage_class": "special",
        "targets": 2,  # Icy Wind hits both opponents in doubles
    }
    
    field = {
        "terrain": None,  # No terrain active
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
    
    # Expected rolls from user: (152, 156, 158, 158, 162, 162, 164, 168, 168, 170, 170, 174, 176, 176, 180, 182)
    expected = (152, 156, 158, 158, 162, 162, 164, 168, 168, 170, 170, 174, 176, 176, 180, 182)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Range: {min(actual) if actual else 0}-{max(actual) if actual else 0}")
    
    assert actual == expected, f"Expected {expected}, got {actual}"


def test_quark_drive_volt_switch_baseline_without_terrain():
    """0 SpA Iron Bundle Volt Switch (1-target) vs. 0 HP / 0 SpD Bulbasaur (NO Electric Terrain): 43-51"""
    print("\n" + "="*80)
    print("TEST 5: 0 SpA Iron Bundle Volt Switch vs. 0 HP / 0 SpD Bulbasaur (NO Electric Terrain)")
    print("Doubles, Level 100, Volt Switch has 1 target (single-target move), NO ability")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="iron-bundle",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        ability=None
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
        "targets": 1,  # Volt Switch is single-target
    }
    
    field = {
        "terrain": None,  # No terrain active
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
    
    # Expected rolls from user: (43, 43, 44, 44, 45, 45, 46, 46, 47, 47, 48, 48, 49, 49, 50, 51)
    expected = (43, 43, 44, 44, 45, 45, 46, 46, 47, 47, 48, 48, 49, 49, 50, 51)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Range: {min(actual) if actual else 0}-{max(actual) if actual else 0}")
    
    assert actual == expected, f"Expected {expected}, got {actual}"
