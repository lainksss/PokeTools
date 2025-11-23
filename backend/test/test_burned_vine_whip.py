import json
from pathlib import Path

from calculate_damages.calculate_damages import calculate_damage
from test_calcs import get_pokemon_stats


def test_burned_bulbasaur_vine_whip():
    """0 Atk burned Bulbasaur Vine Whip vs. 0 HP / 0 Def Bulbasaur: expect all 3s"""
    # Attacker: Bulbasaur level 50, 0 EVs, burned
    attacker = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    attacker["status"] = "burn"

    # Defender: Bulbasaur level 50, 0 EVs
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    move = {
        "name": "vine-whip",
        "power": 45,
        "type": "grass",
        "damage_class": "physical",
    }

    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        random_range=range(85, 101),
        debug=True,
    )

    actual = tuple(result['damage_all'])
    expected = tuple([3] * 16)

    print("Expected:", expected)
    print("Actual:  ", actual)
    if result.get('debug'):
        print('Debug:', result['debug'])

    assert actual == expected
