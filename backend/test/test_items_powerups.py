"""Item power-up tests (16-roll distributions) copied from user-provided expectations.

Each test follows the project's existing testing style (helpers to compute stats and call calculate_damage).
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


def run_case(attacker_species, attacker_item, move, defender_species="bulbasaur", field=None, evs_attacker=None, evs_defender=None, expected=None, set_targets=None, debug=False):
    if evs_attacker is None:
        evs_attacker = {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}
    if evs_defender is None:
        evs_defender = {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}

    attacker = get_pokemon_stats(species=attacker_species, level=50, evs=evs_attacker, item=attacker_item)
    defender = get_pokemon_stats(species=defender_species, level=50, evs=evs_defender)

    if set_targets:
        move["targets"] = set_targets

    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        field=field or {},
        random_range=range(85, 101),
        debug=debug,
    )

    actual = tuple(result["damage_all"])
    print(f"Case: {attacker_species} item={attacker_item} move={move.get('name')} field={field}")
    print("Expected:", expected)
    print("Actual:  ", actual)
    if debug and result.get('debug'):
        print("Debug:", result.get('debug'))
    assert actual == tuple(expected)


def test_charcoal_charizard_flamethrower():
    EXPECTED = (186, 188, 192, 194, 194, 198, 200, 204, 204, 206, 210, 212, 212, 216, 218, 222)
    move = {"name": "flamethrower", "power": 90, "type": "fire", "damage_class": "special"}
    run_case("charizard", "charcoal", move, expected=EXPECTED)


def test_magnet_magnezone_thunderbolt():
    EXPECTED = (54, 54, 54, 55, 56, 57, 57, 58, 59, 59, 60, 60, 61, 62, 63, 63)
    move = {"name": "thunderbolt", "power": 90, "type": "electric", "damage_class": "special"}
    run_case("magnezone", "magnet", move, expected=EXPECTED)


def test_sharp_beak_thundurus_fly():
    # Use incarnate form key present in data
    EXPECTED = (236, 240, 242, 246, 248, 252, 254, 258, 260, 264, 266, 270, 272, 276, 278, 282)
    move = {"name": "fly", "power": 90, "type": "flying", "damage_class": "physical"}
    run_case("thundurus-incarnate", "sharp-beak", move, expected=EXPECTED)


def test_black_belt_urshifu_close_combat():
    EXPECTED = (88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 99, 99, 100, 102, 102, 104)
    move = {"name": "close-combat", "power": 120, "type": "fighting", "damage_class": "physical"}
    run_case("urshifu-rapid-strike", "black-belt", move, expected=EXPECTED)


def test_mystic_water_kyogre_water_spout_rain_double():
    # Double battle note: set targets=2 and field battle_mode=double
    EXPECTED = (114, 115, 117, 118, 120, 121, 122, 123, 125, 126, 128, 129, 130, 132, 133, 135)
    move = {"name": "water-spout", "power": 150, "type": "water", "damage_class": "special"}
    field = {"weather": "rain", "battle_mode": "double"}
    run_case("kyogre", "mystic-water", move, field=field, set_targets=2, expected=EXPECTED)


def test_miracle_seed_venusaur_solar_beam():
    EXPECTED = (28, 29, 29, 30, 30, 30, 30, 31, 31, 31, 32, 32, 33, 33, 33, 34)
    move = {"name": "solar-beam", "power": 120, "type": "grass", "damage_class": "special"}
    run_case("venusaur", "miracle-seed", move, expected=EXPECTED)


def test_never_melt_ice_calyrex_glacial_lance_double():
    EXPECTED = (324, 330, 332, 336, 338, 344, 348, 350, 356, 360, 362, 366, 372, 374, 378, 384)
    move = {"name": "glacial-lance", "power": 120, "type": "ice", "damage_class": "physical"}
    # double battle context
    field = {"battle_mode": "double"}
    # species key in data is 'calyrex-ice'
    run_case("calyrex-ice", "never-melt-ice", move, field=field, set_targets=2, expected=EXPECTED)


def test_poison_barb_sneasler_dire_claw():
    EXPECTED = (118, 118, 120, 121, 123, 124, 126, 127, 129, 130, 132, 133, 135, 136, 138, 139)
    move = {"name": "dire-claw", "power": 80, "type": "poison", "damage_class": "physical"}
    # enable debug to inspect power/flags if mismatch occurs
    run_case("sneasler", "poison-barb", move, expected=EXPECTED, debug=True)


def test_hard_stone_tyranitar_rock_tomb_sandstorm():
    EXPECTED = (91, 91, 93, 94, 96, 96, 97, 99, 99, 100, 102, 103, 103, 105, 106, 108)
    move = {"name": "rock-tomb", "power": 60, "type": "rock", "damage_class": "physical"}
    field = {"weather": "sandstorm"}
    run_case("tyranitar", "hard-stone", move, field=field, expected=EXPECTED)


def test_soft_sand_hippowdon_earthquake_double_sandstorm():
    EXPECTED = (97, 99, 99, 100, 102, 103, 105, 105, 106, 108, 109, 109, 111, 112, 114, 115)
    move = {"name": "earthquake", "power": 100, "type": "ground", "damage_class": "physical"}
    field = {"weather": "sandstorm", "battle_mode": "double"}
    run_case("hippowdon", "soft-sand", move, field=field, set_targets=2, expected=EXPECTED)
