"""Tests for Tera Shell ability.

Tera Shell: when at full HP, provides resistance to all types (halves damage).

Test cases:
1. At full HP with Tera Shell (damage halved):
   0 SpA Bulbasaur Flamethrower vs. 0 HP / 0 SpD Tera Shell Bulbasaur: 17-20 (14.1 - 16.6%)
   Possible damage amounts: (17, 17, 17, 18, 18, 18, 18, 18, 19, 19, 19, 19, 19, 20, 20, 20)

2. At partial HP (1 HP less than max), Tera Shell inactive:
   0 SpA Bulbasaur Flamethrower vs. 119 HP / 0 SpD normal Bulbasaur: 68-82 (56.6 - 68.3%)
   Possible damage amounts: (68, 70, 70, 72, 72, 72, 74, 74, 76, 76, 76, 78, 78, 80, 80, 82)
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

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


def get_pokemon_stats(species: str, level: int, evs: dict, ivs: dict = None, natures: dict = None, ability: str = None, custom_hp: int = None):
    if ivs is None:
        ivs = {"hp": 31, "attack": 31, "defense": 31, "special-attack": 31, "special-defense": 31, "speed": 31}
    if natures is None:
        natures = {"hp": 1.0, "attack": 1.0, "defense": 1.0, "special-attack": 1.0, "special-defense": 1.0, "speed": 1.0}

    pokemon = POKEMON_DATA[species]
    base_stats = pokemon["base_stats"]

    base_hp = calculate_stat(base_stats["hp"], ivs.get("hp", 31), evs.get("hp", 0), level, is_hp=True)
    if custom_hp is not None:
        hp = custom_hp
    else:
        hp = base_hp
    max_hp = base_hp

    stats = {
        "species": species,
        "level": level,
        "types": pokemon["types"],
        "hp": hp,
        "max_hp": max_hp,
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


def test_tera_shell_at_full_hp():
    """0 SpA Bulbasaur Flamethrower vs. Tera Shell Bulbasaur (at full HP)."""
    attacker = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        ability="tera-shell",
    )

    move = {"name": "flamethrower", "power": 90, "type": "fire", "damage_class": "special"}

    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        random_range=range(85, 101),
        debug=False,
    )

    expected = (17, 17, 17, 18, 18, 18, 18, 18, 19, 19, 19, 19, 19, 20, 20, 20)
    actual = tuple(result["damage_all"])

    print(f"Flamethrower vs Tera Shell (full HP): {actual}")
    assert actual == expected, f"Expected {expected}, got {actual}"


def test_flamethrower_at_partial_hp():
    """0 SpA Bulbasaur Flamethrower vs. Bulbasaur at 119 HP (partial HP, Tera Shell inactive)."""
    attacker = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    # Custom HP = 119 (1 less than max to simulate partial damage)
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        ability="tera-shell",
        custom_hp=119,
    )

    move = {"name": "flamethrower", "power": 90, "type": "fire", "damage_class": "special"}

    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        random_range=range(85, 101),
        debug=False,
    )

    expected = (68, 70, 70, 72, 72, 72, 74, 74, 76, 76, 76, 78, 78, 80, 80, 82)
    actual = tuple(result["damage_all"])

    print(f"Flamethrower vs Tera Shell (119 HP, inactive): {actual}")
    assert actual == expected, f"Expected {expected}, got {actual}"


if __name__ == "__main__":
    test_tera_shell_at_full_hp()
    test_flamethrower_at_partial_hp()
    print("All Tera Shell tests passed!")
