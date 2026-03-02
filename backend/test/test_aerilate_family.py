"""Tests for Aerilate / Pixilate / Refrigerate / Galvanize behaviors.

These tests follow the same style as existing tests in the suite: they
load `data/all_pokemon.json`, compute stats for level 50 Pokémon with
specified EVs/natures, run `calculate_damage` with `random_range=range(85,101)`
and assert distributions or summary values provided by the user.
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


def test_aerilate_salamence_double_edge():
    # 0 Atk Aerilate Salamence Double-Edge vs. 0 HP / 0 Def Bulbasaur
    attacker = get_pokemon_stats(
        species="salamence",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    attacker["ability"] = "aerilate"

    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    move = {"name": "double-edge", "power": 120, "type": "normal", "damage_class": "physical"}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, random_range=range(85, 101))

    expected = (366, 368, 374, 378, 384, 386, 392, 396, 398, 404, 408, 414, 416, 422, 426, 432)
    actual = tuple(res["damage_all"])
    # Debug output to help if things diverge
    print("Expected:", expected)
    print("Actual:  ", actual)
    assert actual == expected
    # Defender HP is 128 -> guaranteed OHKO
    assert res.get("ko_chance", 0) == 100.0


def test_pixilate_sylveon_hyper_voice():
    # 0 SpA Pixilate Sylveon Hyper Voice vs. 0 HP / 0 SpD Bulbasaur
    attacker = get_pokemon_stats(
        species="sylveon",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    attacker["ability"] = "pixilate"

    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    field = {
        "battle_mode": "double",  # DOUBLE BATTLE!
    }
    move = {"name": "hyper-voice", "power": 90, "type": "normal", "damage_class": "special", "targets": 2}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, random_range=range(85, 101), field=field)

    expected = (34, 35, 35, 36, 36, 36, 37, 37, 38, 38, 39, 39, 39, 39, 40, 41)
    assert tuple(res["damage_all"]) == expected


def test_refrigerate_aurorus_round():
    # 0 SpA Refrigerate Aurorus Round vs. 0 HP / 0 SpD Bulbasaur
    attacker = get_pokemon_stats(
        species="aurorus",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    attacker["ability"] = "refrigerate"

    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    move = {"name": "round", "power": 60, "type": "normal", "damage_class": "special"}
    field = {
        "battle_mode": "double",  # DOUBLE BATTLE!
    }
    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, random_range=range(85, 101), field=field)

    expected = (116, 116, 120, 120, 120, 122, 122, 126, 126, 128, 128, 132, 132, 134, 134, 138)
    assert tuple(res["damage_all"]) == expected


def test_galvanize_golem_explosion_vs_abomasnow_in_snow():
    # 0 Atk Galvanize Golem-Alola Explosion vs. 0 HP / 0 Def bulbasaur
    attacker = get_pokemon_stats(
        species="golem-alola",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    attacker["ability"] = "galvanize"

    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    field = {
        "battle_mode": "double",  # DOUBLE BATTLE!
    }
    move = {"name": "explosion", "power": 250, "type": "normal", "damage_class": "physical", "targets": 2}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, random_range=range(85, 101), field=field)

    expected = (128, 129, 131, 132, 134, 135, 137, 138, 140, 141, 143, 144, 146, 147, 149, 151)
    assert tuple(res["damage_all"]) == expected


def test_normalize_bulbasaur_solar_beam():
    # 0 SpA Normalize Bulbasaur Solar Beam vs. 0 HP / 0 SpD Bulbasaur
    attacker = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    attacker["ability"] = "normalize"

    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 128, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    move = {"name": "solar-beam", "power": 120, "type": "grass", "damage_class": "special"}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, random_range=range(85, 101))

    expected = (55, 55, 56, 57, 57, 58, 59, 59, 60, 61, 61, 62, 63, 63, 64, 65)
    actual = tuple(res["damage_all"])
    print("Expected:", expected)
    print("Actual:  ", actual)
    assert actual == expected
