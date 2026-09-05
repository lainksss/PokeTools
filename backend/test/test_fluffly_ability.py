"""Tests for Fluffy and Aura Guard abilities.

Fluffy:
  - Halves damage from contact moves.
  - Doubles damage from Fire-type moves.
  - Fire-type contact moves deal regular damage (x0.5 contact x x2.0 fire = x1.0).
  - Long Reach (attacker) negates the contact flag, so Long Reach contact moves deal regular damage.
  - Fire-type moves with Long Reach (non-contact) still deal double damage.

Aura Guard:
  - Halves damage from contact moves.
  - Long Reach (attacker) negates the contact flag, so Long Reach contact moves deal regular damage.
  - No special interaction with Fire-type moves.
"""

from calculate_damages.calculate_damages import calculate_damage
from test_calcs import get_pokemon_stats


def _make_bewear_def():
    return get_pokemon_stats(
        species="bewear",
        ability="fluffy",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )


def _make_salamence_atk():
    return get_pokemon_stats(
        species="salamence-mega",
        ability="aerilate",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )


def test_double_edge_with_fluffy():
    attacker = _make_salamence_atk()
    defender = _make_bewear_def()
    move = {"name": "double-edge", "power": 120, "type": "normal", "damage_class": "physical"}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50 , random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (135, 136, 138, 139, 141, 142, 144, 145, 147, 148, 150, 151, 153, 154, 156, 159)
    assert actual == expected


def test_double_edge_without_fluffy():
    attacker = _make_salamence_atk()
    defender = _make_bewear_def()
    defender["ability"] = None
    move = {"name": "double-edge", "power": 120, "type": "normal", "damage_class": "physical"}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (270, 272, 276, 278, 282, 284, 288, 290, 294, 296, 300, 302, 306, 308, 312, 318)
    assert actual == expected


def test_fire_punch_with_fluffy():
    attacker = _make_salamence_atk()
    defender = _make_bewear_def()
    move = {"name": "fire-punch", "power": 75, "type": "fire", "damage_class": "physical"}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (47, 48, 48, 49, 49, 50, 50, 51, 52, 52, 53, 53, 54, 54, 55, 56)
    assert actual == expected


def test_fire_punch_without_fluffy():
    attacker = _make_salamence_atk()
    defender = _make_bewear_def()
    defender["ability"] = None
    move = {"name": "fire-punch", "power": 75, "type": "fire", "damage_class": "physical"}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (47, 48, 48, 49, 49, 50, 50, 51, 52, 52, 53, 53, 54, 54, 55, 56)
    assert actual == expected

def test_earthquake_with_fluffy():
    attacker = _make_salamence_atk()
    defender = _make_bewear_def()
    move = {"name": "earthquake", "power": 100, "type": "ground", "damage_class": "physical", "targets": 2}
    field = {"battle_mode": "double"}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, field=field, random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (46, 47, 47, 48, 48, 49, 50, 50, 51, 51, 52, 52, 53, 53, 54, 55)
    assert actual == expected
    
def test_flamethrower_with_fluffy():
    attacker = _make_salamence_atk()
    defender = _make_bewear_def()
    move = {"name": "flamethrower", "power": 90, "type": "fire", "damage_class": "special"}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (120, 122, 122, 124, 126, 126, 128, 130, 132, 132, 134, 136, 136, 138, 140, 142)
    assert actual == expected
    
def test_flamethrower_without_fluffy():
    attacker = _make_salamence_atk()
    defender = _make_bewear_def()
    move = {"name": "flamethrower", "power": 90, "type": "fire", "damage_class": "special"}
    defender["ability"] = None

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (60, 61, 61, 62, 63, 63, 64, 65, 66, 66, 67, 68, 68, 69, 70, 71)
    assert actual == expected
    
