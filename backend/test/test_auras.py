from calculate_damages.calculate_damages import calculate_damage
from test_calcs import get_pokemon_stats


def _make_bulbasaur_def():
    return get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )


def _make_xerneas_atk():
    return get_pokemon_stats(
        species="xerneas",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )


def _make_yveltal_atk():
    return get_pokemon_stats(
        species="yveltal",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )


def test_moonblast_with_fairy_aura():
    attacker = _make_xerneas_atk()
    defender = _make_bulbasaur_def()
    move = {"name": "moonblast", "power": 95, "type": "fairy", "damage_class": "special"}
    field = {"fairy_aura": True}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, field=field, random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (63, 64, 65, 66, 66, 67, 68, 69, 69, 70, 71, 72, 72, 73, 74, 75)
    assert actual == expected


def test_moonblast_without_fairy_aura():
    attacker = _make_xerneas_atk()
    defender = _make_bulbasaur_def()
    move = {"name": "moonblast", "power": 95, "type": "fairy", "damage_class": "special"}
    field = {}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, field=field, random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (48, 48, 49, 49, 50, 51, 51, 51, 52, 53, 54, 54, 54, 55, 56, 57)
    assert actual == expected


def test_moonblast_with_fairy_and_aura_break():
    attacker = _make_xerneas_atk()
    defender = _make_bulbasaur_def()
    move = {"name": "moonblast", "power": 95, "type": "fairy", "damage_class": "special"}
    field = {"fairy_aura": True, "aura_break": True}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, field=field, random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (36, 36, 36, 37, 37, 38, 38, 39, 39, 39, 40, 40, 41, 41, 42, 42)
    assert actual == expected


def test_darkpulse_with_dark_aura():
    attacker = _make_yveltal_atk()
    defender = _make_bulbasaur_def()
    move = {"name": "dark-pulse", "power": 80, "type": "dark", "damage_class": "special"}
    field = {"dark_aura": True}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, field=field, random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (106, 108, 109, 109, 111, 112, 114, 115, 117, 117, 118, 120, 121, 123, 124, 126)
    assert actual == expected


def test_darkpulse_without_dark_aura():
    attacker = _make_yveltal_atk()
    defender = _make_bulbasaur_def()
    move = {"name": "dark-pulse", "power": 80, "type": "dark", "damage_class": "special"}
    field = {}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, field=field, random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (81, 82, 82, 84, 84, 85, 87, 87, 88, 90, 90, 91, 93, 93, 94, 96)
    assert actual == expected


def test_darkpulse_with_dark_and_aura_break():
    attacker = _make_yveltal_atk()
    defender = _make_bulbasaur_def()
    move = {"name": "dark-pulse", "power": 80, "type": "dark", "damage_class": "special"}
    field = {"dark_aura": True, "aura_break": True}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, field=field, random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (60, 61, 61, 63, 63, 64, 64, 66, 66, 67, 67, 69, 69, 70, 70, 72)
    assert actual == expected


def test_aura_break_alone_on_yveltal():
    attacker = _make_yveltal_atk()
    defender = _make_bulbasaur_def()
    move = {"name": "dark-pulse", "power": 80, "type": "dark", "damage_class": "special"}
    field = {"aura_break": True}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, field=field, random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (81, 82, 82, 84, 84, 85, 87, 87, 88, 90, 90, 91, 93, 93, 94, 96)
    assert actual == expected


def test_aura_break_alone_on_xerneas():
    attacker = _make_xerneas_atk()
    defender = _make_bulbasaur_def()
    move = {"name": "moonblast", "power": 95, "type": "fairy", "damage_class": "special"}
    field = {"aura_break": True}

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, field=field, random_range=range(85, 101), debug=True)
    actual = tuple(res['damage_all'])
    expected = (48, 48, 49, 49, 50, 51, 51, 51, 52, 53, 54, 54, 54, 55, 56, 57)
    assert actual == expected
