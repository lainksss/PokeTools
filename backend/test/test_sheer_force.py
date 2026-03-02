"""Test Sheer Force (Landorus) with Bite.

Case: 0 Atk Sheer Force Landorus Bite vs. 0 HP / 0 Def Bulbasaur: 62-74
Expected damage distribution (random 85-100):
(62, 63, 64, 65, 65, 66, 67, 68, 68, 69, 70, 71, 71, 72, 73, 74)
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from calculate_damages.calculate_damages import calculate_damage


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


def test_sheer_force_landorus_bite():
    # Attacker: Landorus, level 50, 0 EVs Attack (neutral nature)
    attacker = get_pokemon_stats(
        species="landorus-incarnate",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    attacker["ability"] = "sheer-force"

    # Defender: Bulbasaur, level 50, 0 HP EV / 0 Def EV
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    # Bite: base power 60 and has a flinch secondary effect (so Sheer Force should apply)
    move = {"name": "bite", "power": 60, "type": "dark", "damage_class": "physical"}

    print("Attacker attack:", attacker.get("attack"))
    print("Defender defense:", defender.get("defense"))
    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        random_range=range(85, 101),
        debug=True,
    )

    expected = (62, 63, 64, 65, 65, 66, 67, 68, 68, 69, 70, 71, 71, 72, 73, 74)
    actual = tuple(result["damage_all"])

    print("move after calculate_damage:", move)
    print("result debug:", result.get("debug"))
    print("Expected:", expected)
    print("Actual:  ", actual)

    assert actual == expected


def test_sheer_force_landorus_earthquake_no_secondary():
    # Attacker: Landorus, level 50, 0 EVs Attack (neutral nature)
    attacker = get_pokemon_stats(
        species="landorus-incarnate",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    attacker["ability"] = "sheer-force"

    # Defender: Bulbasaur, level 50, 0 HP EV / 0 Def EV
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    # Earthquake: base power 100, no secondary effects (ground move)
    # Simulate a double battle where Earthquake hits multiple targets
    move = {"name": "earthquake", "power": 100, "type": "ground", "damage_class": "physical", "targets": 2}
    field = {"battle_mode": "double"}

    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        field=field,
        random_range=range(85, 101),
        debug=True,
    )

    expected = (88, 90, 90, 91, 93, 94, 94, 96, 97, 97, 99, 100, 100, 102, 103, 105)
    actual = tuple(result["damage_all"])

    # Debug outputs to help diagnose unexpected modifiers
    print("move after calculate_damage:", move)
    print("result debug:", result.get("debug"))
    print("Expected:", expected)
    print("Actual:  ", actual)

    assert actual == expected
