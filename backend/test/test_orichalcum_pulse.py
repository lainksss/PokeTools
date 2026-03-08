"""
Test Orichalcum Pulse ability — Koraidon's signature ability.

Orichalcum Pulse summons harsh sunlight and boosts Attack by ~33% (factor 5461/4096) when in harsh sunlight.

Test cases provided by user with expected damage rolls:
- Close Combat without ability: 147-174
- Close Combat with Orichalcum Pulse in sun: 195-231
- Fire Punch without ability: 246-290
- Fire Punch with Orichalcum Pulse in sun: 490-578
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


def test_orichalcum_pulse_close_combat_with_sun():
    """0 Atk Orichalcum Pulse Koraidon Close Combat vs. 0 HP / 0 Def Bulbasaur in Sun: 195-231"""
    print("\n" + "="*80)
    print("TEST: 0 Atk Orichalcum Pulse Koraidon Close Combat vs. 0 HP / 0 Def Bulbasaur in Sun")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="koraidon",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        ability="orichalcum-pulse"
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}
    )
    
    move = {
        "name": "close-combat",
        "power": 120,
        "type": "fighting",
        "damage_class": "physical",
    }
    
    field = {
        "weather": "harsh-sunlight",
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
    
    # Expected rolls from user: (195, 198, 200, 203, 205, 207, 210, 212, 214, 216, 219, 221, 223, 225, 228, 231)
    expected = (195, 198, 200, 203, 205, 207, 210, 212, 214, 216, 219, 221, 223, 225, 228, 231)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Range: {min(actual) if actual else 0}-{max(actual) if actual else 0}")
    
    assert actual == expected


def test_orichalcum_pulse_fire_punch_with_sun():
    """0 Atk Orichalcum Pulse Koraidon Fire Punch vs. 0 HP / 0 Def Bulbasaur in Sun: 490-578"""
    print("\n" + "="*80)
    print("TEST: 0 Atk Orichalcum Pulse Koraidon Fire Punch vs. 0 HP / 0 Def Bulbasaur in Sun")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="koraidon",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        ability="orichalcum-pulse"
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}
    )
    
    move = {
        "name": "fire-punch",
        "power": 75,
        "type": "fire",
        "damage_class": "physical",
    }
    
    field = {
        "weather": "harsh-sunlight",
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
    
    # Expected rolls from user: (490, 496, 502, 508, 514, 520, 524, 530, 536, 542, 548, 554, 560, 566, 572, 578)
    expected = (490, 496, 502, 508, 514, 520, 524, 530, 536, 542, 548, 554, 560, 566, 572, 578)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Range: {min(actual) if actual else 0}-{max(actual) if actual else 0}")
    
    assert actual == expected


def test_close_combat_without_ability():
    """0 Atk Koraidon Close Combat vs. 0 HP / 0 Def Bulbasaur (without ability/sun): 147-174"""
    print("\n" + "="*80)
    print("TEST: 0 Atk Koraidon Close Combat vs. 0 HP / 0 Def Bulbasaur (NO Orichalcum Pulse)")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="koraidon",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        ability=None  # No ability
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}
    )
    
    move = {
        "name": "close-combat",
        "power": 120,
        "type": "fighting",
        "damage_class": "physical",
    }
    
    field = {
        "weather": None,
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
    
    # Expected rolls from user: (147, 149, 150, 153, 154, 156, 158, 159, 161, 163, 165, 166, 168, 170, 171, 174)
    expected = (147, 149, 150, 153, 154, 156, 158, 159, 161, 163, 165, 166, 168, 170, 171, 174)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Range: {min(actual) if actual else 0}-{max(actual) if actual else 0}")
    
    assert actual == expected


def test_fire_punch_without_ability():
    """0 Atk Koraidon Fire Punch vs. 0 HP / 0 Def Bulbasaur (without ability/sun): 246-290"""
    print("\n" + "="*80)
    print("TEST: 0 Atk Koraidon Fire Punch vs. 0 HP / 0 Def Bulbasaur (NO Orichalcum Pulse)")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="koraidon",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        ability=None  # No ability
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}
    )
    
    move = {
        "name": "fire-punch",
        "power": 75,
        "type": "fire",
        "damage_class": "physical",
    }
    
    field = {
        "weather": None,
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
    
    # Expected rolls from user: (246, 248, 252, 254, 258, 260, 262, 266, 268, 272, 274, 278, 280, 284, 286, 290)
    expected = (246, 248, 252, 254, 258, 260, 262, 266, 268, 272, 274, 278, 280, 284, 286, 290)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Range: {min(actual) if actual else 0}-{max(actual) if actual else 0}")
    
    assert actual == expected
