"""Test Raichu vs Ninetales-Alola in Snow + Electric Terrain."""
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


def test_raichu_ninetales():
    """12 Atk Raichu Thunder Punch vs. 16 HP / 0 Def Ninetales-Alola in Snow: 45-54"""
    print("\n" + "="*80)
    print("TEST: 12 Atk Raichu Thunder Punch vs. 16 HP / 0 Def Ninetales-Alola in Snow + Electric Terrain")
    print("="*80)
    
    # Raichu: 12 Atk (12 EVs en Atk selon notation Smogon)
    attacker = get_pokemon_stats(
        species="raichu",
        level=50,
        evs={"hp": 0, "attack": 12, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        ivs={"hp": 31, "attack": 31, "defense": 31, "special-attack": 31, "special-defense": 31, "speed": 31},
        natures={"attack": 1.0},  # Neutral
    )
    attacker["is_grounded"] = True  # Pour Electric Terrain
    
    # Ninetales-Alola: 16 HP / 0 Def (16 EVs en HP selon notation Smogon)
    defender = get_pokemon_stats(
        species="ninetales-alola",
        level=50,
        evs={"hp": 16, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        ivs={"hp": 31, "attack": 31, "defense": 31, "special-attack": 31, "special-defense": 31, "speed": 31},
        natures={"defense": 1.0},  # Neutral
    )
    
    # Load move from JSON data
    move = MOVES_DATA.get("thunder-punch", {})
    move["name"] = "thunder-punch"
    
    print(f"Move loaded: {move}")
    
    field = {
        "weather": "snow",
        "terrain": "electric",
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
    
    expected = (45, 45, 46, 46, 48, 48, 48, 49, 49, 49, 51, 51, 51, 52, 52, 54)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"\nBase: {result.get('base_val')}")
    print(f"Attacker Atk: {attacker.get('attack')}")
    print(f"Defender HP: {defender.get('hp')}, Def: {defender.get('defense')}")
    
    if result.get('debug'):
        dbg = result['debug']
        print(f"\nDebug info:")
        print(f"  Power: {dbg.get('power')}")
        print(f"  A: {dbg.get('A')}, D: {dbg.get('D')}")
        print(f"  Type mult: {dbg.get('type_mult')}")
        print(f"  STAB: {dbg.get('stab')}")
        print(f"  Weather: {dbg.get('weather_mult')}")
        print(f"  Terrain: {dbg.get('terrain_mult')}")
        print(f"  Targets: {dbg.get('targets')}")
        print(f"  PB: {dbg.get('pb')}")
        print(f"  Burn mult: {dbg.get('burn_mult')}")
        print(f"  Multipliers applied: {dbg.get('multipliers')}")
    
    assert actual == expected


if __name__ == "__main__":
    passed = test_raichu_ninetales()
    print("\n" + "="*80)
    if passed:
        print("✓ TEST PASSED")
    else:
        print("✗ TEST FAILED")
    print("="*80)
