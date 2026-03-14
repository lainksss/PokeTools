"""Tests for Zamazenta-Crowned interactions (dauntless-shield).

Pattern and helpers mirror backend/test/test_calcs.py
"""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from calculate_damages.calculate_damages import calculate_damage


# Load Pokemon data
POKEMON_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "all_pokemon.json"
with open(POKEMON_DATA_PATH, "r", encoding="utf-8") as f:
    POKEMON_DATA = json.load(f)


def calculate_stat(base: int, iv: int, ev: int, level: int, nature_mult: float = 1.0, is_hp: bool = False) -> int:
    if is_hp:
        return int((2 * base + iv + ev // 4) * level / 100) + level + 10
    else:
        base_stat = int((2 * base + iv + ev // 4) * level / 100) + 5
        return int(base_stat * nature_mult)


def get_pokemon_stats(species: str, level: int, evs: dict, ivs: dict = None, natures: dict = None, item: str = None):
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
        "ability": None,
        "item": item,
        "is_terastallized": False,
    }
    return stats


def test_leaf_storm_vs_zamazenta_crowned():
    print("\n" + "="*80)
    print("TEST: 0 SpA Venusaur Leaf Storm vs. 0 HP / 0 SpD Zamazenta-Crowned")
    print("="*80)
    attacker = get_pokemon_stats(
        species="venusaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    defender = get_pokemon_stats(
        species="zamazenta-crowned",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    defender["ability"] = "dauntless-shield"

    move = {"name": "leaf-storm", "power": 130, "type": "grass", "damage_class": "special"}

    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        random_range=range(85, 101),
        debug=True,
    )

    expected = (27, 27, 28, 28, 29, 29, 30, 30, 30, 30, 30, 31, 31, 32, 32, 33)
    actual = tuple(result['damage_all'])
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    assert actual == expected


def test_leaf_blade_vs_zamazenta_crowned_defplus1():
    print("\n" + "="*80)
    print("TEST: 0 Atk Venusaur Leaf Blade vs. +1 0 HP / 0 Def Zamazenta-Crowned")
    print("="*80)
    attacker = get_pokemon_stats(
        species="venusaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    defender = get_pokemon_stats(
        species="zamazenta-crowned",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    defender["ability"] = "dauntless-shield"

    move = {"name": "leaf-blade", "power": 90, "type": "grass", "damage_class": "physical"}

    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        random_range=range(85, 101),
        debug=True,
    )

    expected = (11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13)
    actual = tuple(result['damage_all'])
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    assert actual == expected


if __name__ == "__main__":
    tests = [
        ("Leaf Storm vs Zamazenta-Crowned", test_leaf_storm_vs_zamazenta_crowned),
        ("Leaf Blade vs Zamazenta-Crowned +1 Def", test_leaf_blade_vs_zamazenta_crowned_defplus1),
    ]

    passed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS - {name}")
            passed += 1
        except AssertionError:
            print(f"FAIL - {name}")

    print(f"\nTotal: {passed}/{len(tests)} tests passed")
