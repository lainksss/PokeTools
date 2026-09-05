from calculate_damages.calculate_damages import calculate_damage
from test_calcs import get_pokemon_stats


def _make_tyranitar_def():
    return get_pokemon_stats(
        species="tyranitar",
        ability="sand-stream",
        level=50,
        evs={"hp": 2, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

def _make_pelipper_def():
    return get_pokemon_stats(
        species="pelipper",
        ability="drizzle",
        level=50,
        evs={"hp": 2, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )

def _make_meganium_atk():
    return get_pokemon_stats(
        species="meganium-mega",
        ability="mega-sol",
        level=50,
        evs={"hp": 0, "attack": 32, "defense": 0, "special-attack": 252, "special-defense": 0, "speed": 0},
        natures={"special-attack": 1.1},
    )


def test_weather_ball_under_rain_with_mega_sol():
    attacker = _make_meganium_atk()
    defender = _make_pelipper_def()
    move = {"name": "weather-ball", "power": 50, "type": "fire", "damage_class": "special"}
    field = {"weather": "rain"}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50 , field = field, random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (67, 68, 69, 69, 70, 71, 72, 73, 73, 74, 75, 76, 77, 77, 78, 79)
    assert actual == expected


def test_weather_ball_under_sandstorm_with_mega_sol():
    attacker = _make_meganium_atk()
    defender = _make_tyranitar_def()
    move = {"name": "weather-ball", "power": 50, "type": "normal", "damage_class": "special"}
    field = {"weather": "sand"}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50 , field = field, random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (51, 51, 52, 52, 53, 54, 54, 55, 55, 56, 57, 57, 58, 58, 59, 60)
    assert actual == expected

def test_solar_beam_under_sandstorm_with_mega_sol():
    attacker = _make_meganium_atk()
    defender = _make_tyranitar_def()
    move = {"name": "solar-beam", "power": 120, "type": "grass", "damage_class": "special"}
    field = {"weather": "sand"}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50 , field = field, random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (242, 246, 248, 252, 254, 258, 260, 264, 266, 270, 272, 276, 278, 282, 284, 288)
    assert actual == expected