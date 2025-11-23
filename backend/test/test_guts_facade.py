from calculate_damages.calculate_damages import calculate_damage
from test_calcs import get_pokemon_stats


def test_guts_ursaluna_facade():
    """0 Atk Guts Ursaluna Facade (140 BP) vs. 0 HP / 0 Def Bulbasaur: expect specific distribution
    """
    attacker = get_pokemon_stats(
        species="ursaluna",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    attacker["ability"] = "guts"
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
    expected = (274, 277, 280, 285, 288, 291, 294, 297, 300, 304, 307, 310, 313, 316, 319, 324)

    print('Expected:', expected)
    print('Actual:  ', actual)
    if result.get('debug'):
        print('Debug:', result['debug'])

    assert actual == expected
