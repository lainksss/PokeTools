"""Tests for Steelworker and Steely Spirit with Dialga Flash Cannon.

Cases:
- 0 SpA Steelworker Dialga Flash Cannon vs. 0 HP / 0 SpD Bulbasaur: 135-160
- 0 SpA Steely Spirit Dialga Flash Cannon vs. 0 HP / 0 SpD Bulbasaur: 135-160

Expected distribution (random 85-100):
(135, 138, 139, 141, 142, 144, 145, 147, 148, 150, 151, 153, 154, 156, 157, 160)
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


EXPECTED = (135, 138, 139, 141, 142, 144, 145, 147, 148, 150, 151, 153, 154, 156, 157, 160)


def run_flash_cannon_test(ability_name: str):
    # Attacker: Dialga, level 50, 0 SpA (0 EVs) - special attacker
    attacker = get_pokemon_stats(
        species="dialga",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    attacker["ability"] = ability_name

    # Defender: Bulbasaur, level 50, 0 HP / 0 SpD
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    move = {"name": "flash-cannon", "power": 80, "type": "steel", "damage_class": "special"}

    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        random_range=range(85, 101),
        debug=True,
    )

    actual = tuple(result["damage_all"])

    print(f"Ability: {ability_name}")
    print("Expected:", EXPECTED)
    print("Actual:  ", actual)

    assert actual == EXPECTED


def test_steelworker_dialga_flash_cannon():
    run_flash_cannon_test("steelworker")


def test_steely_spirit_dialga_flash_cannon():
    run_flash_cannon_test("steely-spirit")
