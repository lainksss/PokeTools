"""Tests for Marvel Scale interactions with Milotic (burned and not burned).

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


def test_vine_whip_vs_marvel_milotic_burned():
    print("\n" + "="*80)
    print("TEST: 0 Atk Bulbasaur Vine Whip vs. 0 HP / 0 Def Marvel Scale Milotic (burned)")
    print("="*80)
    attacker = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    defender = get_pokemon_stats(
        species="milotic",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    defender["ability"] = "marvel-scale"
    defender["status"] = "brn"

    move = {"name": "vine-whip", "power": 45, "type": "grass", "damage_class": "physical"}

    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        random_range=range(85, 101),
        debug=True,
    )

    expected = (26, 26, 26, 26, 26, 26, 30, 30, 30, 30, 30, 30, 30, 30, 30, 32)
    actual = tuple(result['damage_all'])
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    assert actual == expected


def test_leaf_storm_spa_vs_milotic_burned():
    print("\n" + "="*80)
    print("TEST: 0 SpA Bulbasaur Leaf Storm vs. 0 HP / 0 SpD Milotic (burned)")
    print("="*80)
    attacker = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    attacker["special_attack"] = attacker["special_attack"]  # 0 SpA case

    defender = get_pokemon_stats(
        species="milotic",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    defender["ability"] = "marvel-scale"
    defender["status"] = "brn"

    move = {"name": "leaf-storm", "power": 130, "type": "grass", "damage_class": "special"}

    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        random_range=range(85, 101),
        debug=True,
    )

    expected = (86, 90, 90, 90, 92, 92, 92, 96, 96, 96, 98, 98, 98, 102, 102, 104)
    actual = tuple(result['damage_all'])
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    assert actual == expected


def test_venusaur_leaf_blade_vs_milotic_burned():
    print("\n" + "="*80)
    print("TEST: 0 Atk Venusaur Leaf Blade vs. 0 HP / 0 Def Marvel Scale Milotic (burned)")
    print("="*80)
    attacker = get_pokemon_stats(
        species="venusaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    defender = get_pokemon_stats(
        species="milotic",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    defender["ability"] = "marvel-scale"
    defender["status"] = "brn"

    move = {"name": "leaf-blade", "power": 90, "type": "grass", "damage_class": "physical"}

    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        random_range=range(85, 101),
        debug=True,
    )

    expected = (72, 72, 74, 74, 74, 78, 78, 78, 78, 80, 80, 80, 84, 84, 84, 86)
    actual = tuple(result['damage_all'])
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    assert actual == expected


def test_venusaur_leaf_blade_vs_milotic_not_burned():
    print("\n" + "="*80)
    print("TEST: 0 Atk Venusaur Leaf Blade vs. 0 HP / 0 Def Milotic (not burned)")
    print("="*80)
    attacker = get_pokemon_stats(
        species="venusaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    defender = get_pokemon_stats(
        species="milotic",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    defender["ability"] = None
    # ensure no status
    if "status" in defender:
        defender.pop("status")

    move = {"name": "leaf-blade", "power": 90, "type": "grass", "damage_class": "physical"}

    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        random_range=range(85, 101),
        debug=True,
    )

    expected = (104, 108, 108, 108, 110, 110, 114, 114, 116, 116, 116, 120, 120, 122, 122, 126)
    actual = tuple(result['damage_all'])
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    assert actual == expected


if __name__ == "__main__":
    tests = [
        ("Vine Whip vs Marvel Milotic (burned)", test_vine_whip_vs_marvel_milotic_burned),
        ("Leaf Storm SpA vs Milotic (burned)", test_leaf_storm_spa_vs_milotic_burned),
        ("Venusaur Leaf Blade vs Marvel Milotic (burned)", test_venusaur_leaf_blade_vs_milotic_burned),
        ("Venusaur Leaf Blade vs Milotic (not burned)", test_venusaur_leaf_blade_vs_milotic_not_burned),
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
