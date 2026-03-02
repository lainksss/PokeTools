import json
from pathlib import Path

from calculate_damages.calculate_damages import calculate_damage

# Load Pokemon data
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


def test_solar_beam_through_light_screen():
    """0 SpA Bulbasaur Solar Beam vs. 0 HP / 0 SpD Bulbasaur through Light Screen: 11-13"""
    attacker = get_pokemon_stats("bulbasaur", 50, {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0})
    defender = get_pokemon_stats("bulbasaur", 50, {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0})

    move = {"name": "solar-beam", "power": 120, "type": "grass", "damage_class": "special"}
    field = {"light_screen": True, "battle_mode": "double"}

    result = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, field=field, random_range=range(85, 101), debug=True)
    expected = (11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 13, 13, 13, 13, 13, 13)
    actual = tuple(result["damage_all"]) 
    assert actual == expected


def test_solar_beam_through_aurora_veil():
    """0 SpA Bulbasaur Solar Beam vs. 0 HP / 0 SpD Bulbasaur through Aurora Veil: 11-13"""
    attacker = get_pokemon_stats("bulbasaur", 50, {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0})
    defender = get_pokemon_stats("bulbasaur", 50, {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0})

    move = {"name": "solar-beam", "power": 120, "type": "grass", "damage_class": "special"}
    field = {"aurora_veil": True, "battle_mode": "double"}

    result = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, field=field, random_range=range(85, 101), debug=True)
    expected = (11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 13, 13, 13, 13, 13, 13)
    actual = tuple(result["damage_all"]) 
    assert actual == expected


def test_razor_leaf_through_reflect():
    """0 Atk Bulbasaur Razor Leaf vs. 0 HP / 0 Def Bulbasaur through Reflect: 4-5"""
    attacker = get_pokemon_stats("bulbasaur", 50, {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0})
    defender = get_pokemon_stats("bulbasaur", 50, {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0})

    move = {"name": "razor-leaf", "power": 55, "type": "grass", "damage_class": "physical"}
    field = {"reflect": True, "battle_mode": "double"}

    result = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, field=field, random_range=range(85, 101), debug=True)
    expected = (5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6)
    actual = tuple(result["damage_all"]) 
    assert actual == expected


def test_razor_leaf_through_aurora_veil():
    """0 Atk Bulbasaur Razor Leaf vs. 0 HP / 0 Def Bulbasaur through Aurora Veil: 4-5"""
    attacker = get_pokemon_stats("bulbasaur", 50, {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0})
    defender = get_pokemon_stats("bulbasaur", 50, {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0})

    move = {"name": "razor-leaf", "power": 55, "type": "grass", "damage_class": "physical"}
    field = {"aurora_veil": True, "battle_mode": "double"}

    result = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, field=field, random_range=range(85, 101), debug=True)
    expected = (5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6)
    actual = tuple(result["damage_all"]) 
    assert actual == expected


def test_brick_break_clears_screens():
    """0 Atk Bulbasaur Brick Break vs. 0 HP / 0 Def Bulbasaur: 14-17 (screens on)"""
    attacker = get_pokemon_stats("bulbasaur", 50, {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0})
    defender = get_pokemon_stats("bulbasaur", 50, {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0})

    move = {"name": "brick-break", "power": 75, "type": "fighting", "damage_class": "physical"}
    # Both screens present
    field = {"reflect": True, "light_screen": True, "battle_mode": "double"}

    result = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, field=field, random_range=range(85, 101), debug=True)
    expected = (9, 10, 10, 10, 10, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11)
    actual = tuple(result["damage_all"]) 
    assert actual == expected


def test_psychic_fangs_clears_screens():
    """0 Atk Bulbasaur Psychic Fangs vs. 0 HP / 0 Def Bulbasaur: 66-78 (screens on)"""
    attacker = get_pokemon_stats("bulbasaur", 50, {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0})
    defender = get_pokemon_stats("bulbasaur", 50, {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0})

    move = {"name": "psychic-fangs", "power": 85, "type": "psychic", "damage_class": "physical"}
    field = {"reflect": True, "light_screen": True, "battle_mode": "double"}

    result = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, field=field, random_range=range(85, 101), debug=True)
    expected = (44, 44, 44, 45, 45, 47, 47, 47, 48, 48, 49, 49, 49, 51, 51, 52)
    actual = tuple(result["damage_all"]) 
    assert actual == expected


def test_raging_bull_clears_screens():
    """0 Atk Bulbasaur Raging Bull vs. 0 HP / 0 Def Bulbasaur: 34-41 (screens on)"""
    attacker = get_pokemon_stats("bulbasaur", 50, {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0})
    defender = get_pokemon_stats("bulbasaur", 50, {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0})

    move = {"name": "raging-bull", "power": 90, "type": "normal", "damage_class": "physical"}
    field = {"reflect": True, "light_screen": True, "battle_mode": "double"}

    result = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, field=field, random_range=range(85, 101), debug=True)
    expected = (23, 23, 23, 24, 24, 24, 25, 25, 25, 25, 25, 26, 26, 27, 27, 27)
    actual = tuple(result["damage_all"]) 
    assert actual == expected
