from calculate_damages.calculate_damages import calculate_damage
from test_calcs import get_pokemon_stats


def test_facade_when_burned():
    """0 Atk Bulbasaur Facade (140 BP) vs. 0 HP / 0 Def Bulbasaur: expect specific distribution"""
    attacker = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    attacker["status"] = "burn"

    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    move = {
        "name": "facade",
        "power": 70,
        "type": "normal",
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
    expected = (53, 54, 54, 55, 56, 56, 57, 57, 58, 59, 59, 60, 61, 61, 62, 63)

    print('Expected:', expected)
    print('Actual:  ', actual)
    if result.get('debug'):
        print('Debug:', result['debug'])

    assert actual == expected
