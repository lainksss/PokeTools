"""Zamazenta & Zacian damage tests inspired by `test_calcs.py`.

Tests are level 50, no terrain, duplicated as requested.
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
        "stages": {},
    }
    return stats


def _run_case(move, attacker, defender, expected):
    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        random_range=range(85, 101),
        debug=True,
    )
    actual = tuple(result['damage_all'])
    assert actual == expected


def test_case_1():
    """+1 Def Zamazenta-Crowned Body Press vs. +1 0 HP / 0 Def Zamazenta-Crowned"""
    attacker = get_pokemon_stats(
        species="zamazenta-crowned",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    attacker["stages"] = {"defense": 1}

    defender = get_pokemon_stats(
        species="zamazenta-crowned",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    defender["stages"] = {"defense": 1}

    move = {"name": "body-press", "power": 80, "type": "fighting", "damage_class": "physical"}

    expected = (92, 92, 96, 96, 96, 98, 98, 102, 102, 102, 104, 104, 104, 108, 108, 110)
    _run_case(move, attacker, defender, expected)


def test_case_1_dup():
    test_case_1()


def test_case_2():
    """0 Atk Zamazenta-Crowned Behemoth Bash vs. +1 0 HP / 0 Def Zamazenta-Crowned"""
    attacker = get_pokemon_stats(
        species="zamazenta-crowned",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    defender = get_pokemon_stats(
        species="zamazenta-crowned",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    defender["stages"] = {"defense": 1}

    move = {"name": "behemoth-bash", "power": 100, "type": "steel", "damage_class": "physical"}

    expected = (16, 17, 17, 17, 18, 18, 18, 18, 18, 18, 18, 18, 19, 19, 19, 20)
    _run_case(move, attacker, defender, expected)


def test_case_2_dup():
    test_case_2()


def test_case_3():
    "+1 Atk Zacian-Crowned Behemoth Blade vs. +1 0 HP / 0 Def Zamazenta-Crowned"
    attacker = get_pokemon_stats(
        species="zacian-crowned",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    attacker["stages"] = {"attack": 1}

    defender = get_pokemon_stats(
        species="zamazenta-crowned",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    defender["stages"] = {"defense": 1}

    move = {"name": "behemoth-blade", "power": 100, "type": "steel", "damage_class": "physical"}

    expected = (30, 30, 30, 31, 31, 32, 32, 33, 33, 33, 33, 34, 34, 35, 35, 36)
    _run_case(move, attacker, defender, expected)


def test_case_3_dup():
    test_case_3()


def test_case_4():
    "+1 Atk Zacian Iron Head vs. 0 HP / 0 Def Zacian-Crowned"
    attacker = get_pokemon_stats(
        species="zacian",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    attacker["stages"] = {"attack": 1}

    defender = get_pokemon_stats(
        species="zacian-crowned",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    move = {"name": "iron-head", "power": 80, "type": "steel", "damage_class": "physical"}

    expected = (47, 48, 48, 49, 49, 50, 50, 51, 52, 52, 53, 53, 54, 54, 55, 56)
    _run_case(move, attacker, defender, expected)


def test_case_4_dup():
    test_case_4()


def test_case_5():
    "+1 Atk Zacian-Crowned Behemoth Blade vs. 0 HP / 0 Def Zacian (OHKO)"
    attacker = get_pokemon_stats(
        species="zacian-crowned",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    attacker["stages"] = {"attack": 1}

    defender = get_pokemon_stats(
        species="zacian",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    move = {"name": "behemoth-blade", "power": 100, "type": "steel", "damage_class": "physical"}

    expected = (216, 218, 218, 222, 224, 228, 230, 234, 236, 236, 240, 242, 246, 248, 252, 254)
    _run_case(move, attacker, defender, expected)


def test_case_5_dup():
    test_case_5()


if __name__ == "__main__":
    funcs = [
        test_case_1, test_case_1_dup,
        test_case_2, test_case_2_dup,
        test_case_3, test_case_3_dup,
        test_case_4, test_case_4_dup,
        test_case_5, test_case_5_dup,
    ]
    for f in funcs:
        print(f"Running {f.__name__}...")
        f()
    print("All cases invoked.")
