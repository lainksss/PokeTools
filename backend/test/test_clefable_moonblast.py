from calculate_damages.calculate_damages import calculate_damage
from test_calcs import get_pokemon_stats


def test_clefable_0spa_moonblast_vs_bulbasaur_under_fairy_aura():
    """0 SpA Clefable Moonblast vs. 0 HP / 0 SpD Bulbasaur under Fairy Aura: 48-57"""
    attacker = get_pokemon_stats(
        species="clefable",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

    move = {"name": "moonblast", "power": 95, "type": "fairy", "damage_class": "special"}
    field = {"fairy_aura": True}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, field=field, random_range=range(85, 101), debug=True)
    actual = tuple(res["damage_all"])

    expected = (48, 49, 49, 50, 51, 51, 52, 52, 53, 54, 54, 54, 55, 56, 57, 57)
    assert actual == expected
