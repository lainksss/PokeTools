"""Tests for Fire Mane.

Cases:
- 0 SpA Fire Mane Mega Pyroar Heat Wave vs. 32 HP / 2 SpD Aegislash-Shield in Sun: 168-198
- 0 SpA Mega Pyroar Heat Wave vs. 32 HP / 2 SpD Aegislash-Shield in Sun: 114-134
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from calculate_damages.calculate_damages import calculate_damage


POKEMON_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "all_pokemon.json"
with open(POKEMON_DATA_PATH, "r", encoding="utf-8") as f:
    POKEMON_DATA = json.load(f)


def convert_unit_to_backend(n: int) -> int:
    if n <= 0:
        return 0
    return 4 + (min(32, n) - 1) * 8


def calculate_stat(base: int, iv: int, ev: int, level: int, nature_mult: float = 1.0, is_hp: bool = False) -> int:
    if is_hp:
        return int((2 * base + iv + ev // 4) * level / 100) + level + 10

    base_stat = int((2 * base + iv + ev // 4) * level / 100) + 5
    return int(base_stat * nature_mult)


def get_pokemon_stats(species: str, level: int, evs: dict, ability: str = None):
    pokemon = POKEMON_DATA[species]
    base_stats = pokemon["base_stats"]

    return {
        "species": species,
        "level": level,
        "types": pokemon["types"],
        "hp": calculate_stat(base_stats["hp"], 31, evs.get("hp", 0), level, is_hp=True),
        "attack": calculate_stat(base_stats["attack"], 31, evs.get("attack", 0), level),
        "defense": calculate_stat(base_stats["defense"], 31, evs.get("defense", 0), level),
        "special_attack": calculate_stat(base_stats["special-attack"], 31, evs.get("special-attack", 0), level),
        "special_defense": calculate_stat(base_stats["special-defense"], 31, evs.get("special-defense", 0), level),
        "speed": calculate_stat(base_stats["speed"], 31, evs.get("speed", 0), level),
        "ability": ability,
        "item": None,
        "is_terastallized": False,
    }


def run_heat_wave(ability: str = None):
    attacker = get_pokemon_stats(
        species="pyroar-mega",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        ability=ability,
    )
    defender = get_pokemon_stats(
        species="aegislash-shield",
        level=50,
        evs={
            "hp": convert_unit_to_backend(32),
            "attack": 0,
            "defense": 0,
            "special-attack": 0,
            "special-defense": convert_unit_to_backend(2),
            "speed": 0,
        },
    )
    move = {
        "name": "heat-wave",
        "power": 95,
        "type": "fire",
        "damage_class": "special",
        "targets": 2,
    }
    field = {
        "weather": "sun",
        "battle_mode": "double",
    }

    return calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        field=field,
        level=50,
        random_range=range(85, 101),
        debug=True,
    )


def test_fire_mane_boosts_fire_special_attack_damage():
    result = run_heat_wave(ability="fire-mane")

    expected = (168, 168, 170, 174, 174, 176, 180, 180, 182, 186, 186, 188, 192, 192, 194, 198)
    actual = tuple(result["damage_all"])

    assert actual == expected
    assert result["debug"]["ability_effects"]["fire_mane"] is True


def test_heat_wave_without_fire_mane():
    result = run_heat_wave(ability=None)

    expected = (114, 114, 116, 116, 120, 120, 120, 122, 122, 126, 126, 128, 128, 132, 132, 134)
    actual = tuple(result["damage_all"])

    assert actual == expected
    assert "fire_mane" not in result["debug"].get("ability_effects", {})
