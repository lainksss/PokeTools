"""Test Hatterene vs Golem in Sandstorm + Psychic Terrain."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from calculate_damages.calculate_damages import calculate_damage

# Load Pokemon data
POKEMON_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "all_pokemon.json"
with open(POKEMON_DATA_PATH, "r", encoding="utf-8") as f:
    POKEMON_DATA = json.load(f)

# Load moves data
MOVES_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "all_moves.json"
with open(MOVES_DATA_PATH, "r", encoding="utf-8") as f:
    MOVES_DATA = json.load(f)


def calculate_stat(base: int, iv: int, ev: int, level: int, nature_mult: float = 1.0, is_hp: bool = False) -> int:
    """Calculate a stat using the standard Pokemon formula."""
    if is_hp:
        return int((2 * base + iv + ev // 4) * level / 100) + level + 10
    else:
        base_stat = int((2 * base + iv + ev // 4) * level / 100) + 5
        return int(base_stat * nature_mult)


def get_pokemon_stats(species: str, level: int, evs: dict, ivs: dict = None, natures: dict = None, item: str = None):
    """Retrieve and calculate Pokemon stats from the JSON file."""
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


def test_hatterene_golem():
    """20 SpA Hatterene Psychic vs. 0 HP / 0 SpD Golem in Sand: 84-99 (54.1 - 63.8%) -- guaranteed 2HKO"""
    print("\n" + "="*80)
    print("TEST: 20 SpA Hatterene Psychic vs. 0 HP / 0 SpD Golem in Sand + Psychic Terrain")
    print("="*80)
    
    # Hatterene: 20 SpA EVs
    attacker = get_pokemon_stats(
        species="hatterene",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 20, "special-defense": 0, "speed": 0},
        natures={"special-attack": 1.0},  # Neutral
    )
    attacker["is_grounded"] = True  # Pour Psychic Terrain
    
    # Golem: 0 HP / 0 SpD
    defender = get_pokemon_stats(
        species="golem",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        natures={"special-defense": 1.0},  # Neutral
    )
    
    # Load move from JSON data
    move = MOVES_DATA.get("psychic", {})
    move["name"] = "psychic"
    
    print(f"Move loaded: {move}")
    print(f"Hatterene SpA: {attacker['special_attack']}")
    print(f"Golem HP: {defender['hp']}, SpD: {defender['special_defense']}")
    print(f"Golem types: {defender['types']}")
    
    field = {
        "weather": "sandstorm",
        "terrain": "psychic",
    }
    
    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        field=field,
        random_range=range(85, 101),
        debug=True,
    )
    
    expected = (84, 84, 85, 87, 87, 88, 90, 90, 91, 93, 93, 94, 96, 96, 97, 99)
    actual = tuple(result['damage_all'])
    
    print(f"\nExpected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"\nBase: {result.get('base_val')}")
    
    if result.get('debug'):
        dbg = result['debug']
        print(f"\nDebug info:")
        print(f"  Power: {dbg.get('power')}")
        print(f"  A: {dbg.get('A')}, D: {dbg.get('D')}")
        print(f"  Type mult: {dbg.get('type_mult')}")
        print(f"  STAB: {dbg.get('stab')}")
        print(f"  Weather: {dbg.get('weather_mult')}")
        print(f"  Terrain: {dbg.get('terrain_mult')}")
    
    assert actual == expected


if __name__ == "__main__":
    passed = test_hatterene_golem()
    print("\n" + "="*80)
    if passed:
        print("✓ TEST PASSED")
    else:
        print("✗ TEST FAILED")
    print("="*80)
