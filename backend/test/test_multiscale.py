"""Tests for Multiscale ability.

When a Pokémon with Multiscale is at full HP, it halves incoming damage.

Test cases:
1. 0 SpA Bulbasaur Solar Beam vs. 0 HP / 0 SpD Multiscale Bulbasaur: 16-19 (6.9 - 8.2%)
   Possible damage amounts: (16, 16, 16, 16, 16, 17, 17, 17, 17, 17, 18, 18, 18, 18, 18, 19)

2. 0 SpA Bulbasaur Ice Beam vs. 0 HP / 0 SpD Multiscale Bulbasaur: 65-77 (28.1 - 33.3%)
   Possible damage amounts: (65, 66, 66, 67, 68, 69, 70, 70, 71, 72, 73, 73, 74, 75, 76, 77)
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


def get_pokemon_stats(species: str, level: int, evs: dict, ivs: dict = None, natures: dict = None, ability: str = None):
    if ivs is None:
        ivs = {"hp": 31, "attack": 31, "defense": 31, "special-attack": 31, "special-defense": 31, "speed": 31}
    if natures is None:
        natures = {"hp": 1.0, "attack": 1.0, "defense": 1.0, "special-attack": 1.0, "special-defense": 1.0, "speed": 1.0}

    pokemon = POKEMON_DATA[species]
    base_stats = pokemon["base_stats"]

    hp = calculate_stat(base_stats["hp"], ivs.get("hp", 31), evs.get("hp", 0), level, is_hp=True)
    
    stats = {
        "species": species,
        "level": level,
        "types": pokemon["types"],
        "hp": hp,
        "max_hp": hp,
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


def test_multiscale_solar_beam():
    """0 SpA Bulbasaur Solar Beam vs. Multiscale Bulbasaur."""
    attacker = get_pokemon_stats(
        species="bulbasaur",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    defender = get_pokemon_stats(
        species="bulbasaur",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        ability="multiscale",
    )

    move = {"name": "solar-beam", "power": 120, "type": "grass", "damage_class": "special"}

    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=100,
        random_range=range(85, 101),
        debug=False,
    )

    expected = (16, 16, 16, 16, 16, 17, 17, 17, 17, 17, 18, 18, 18, 18, 18, 19)
    actual = tuple(result["damage_all"])

    print(f"Solar Beam vs Multiscale: {actual}")
    assert actual == expected, f"Expected {expected}, got {actual}"


def test_multiscale_ice_beam():
    """0 SpA Bulbasaur Ice Beam vs. Multiscale Bulbasaur."""
    attacker = get_pokemon_stats(
        species="bulbasaur",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    defender = get_pokemon_stats(
        species="bulbasaur",
        level=100,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        ability="multiscale",
    )

    move = {"name": "ice-beam", "power": 90, "type": "ice", "damage_class": "special"}

    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=100,
        random_range=range(85, 101),
        debug=False,
    )

    expected = (65, 66, 66, 67, 68, 69, 70, 70, 71, 72, 73, 73, 74, 75, 76, 77)
    actual = tuple(result["damage_all"])

    print(f"Ice Beam vs Multiscale: {actual}")
    assert actual == expected, f"Expected {expected}, got {actual}"


if __name__ == "__main__":
    test_multiscale_solar_beam()
    test_multiscale_ice_beam()
    print("All Multiscale tests passed!")
