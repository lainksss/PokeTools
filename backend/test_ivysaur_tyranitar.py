"""Test Ivysaur vs Tyranitar avec Grassy Terrain et Sandstorm."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from calculate_damages.calculate_damages import calculate_damage

# Load Pokemon data
POKEMON_DATA_PATH = Path(__file__).parent.parent / "data" / "all_pokemon.json"
with open(POKEMON_DATA_PATH, "r", encoding="utf-8") as f:
    POKEMON_DATA = json.load(f)


def calculate_stat(base: int, iv: int, ev: int, level: int, nature_mult: float = 1.0, is_hp: bool = False) -> int:
    """Calculate a stat using the standard Pokemon formula."""
    if is_hp:
        return int((2 * base + iv + ev // 4) * level / 100) + level + 10
    else:
        base_stat = int((2 * base + iv + ev // 4) * level / 100) + 5
        return int(base_stat * nature_mult)


def test_ivysaur_tyranitar():
    """156 SpA Ivysaur Solar Beam (60 BP) vs. 0 HP / 0 SpD Assault Vest Tyranitar in Sand + Grassy Terrain: 42-50"""
    print("\n" + "="*80)
    print("TEST: 156 SpA Ivysaur Solar Beam (60 BP) vs. 0 HP / 0 SpD Assault Vest Tyranitar")
    print("      in Sandstorm + Grassy Terrain")
    print("="*80)
    
    # Ivysaur: 156 SpA EVs, neutral nature
    ivysaur_data = POKEMON_DATA["ivysaur"]
    ivysaur_base = ivysaur_data["base_stats"]
    
    attacker = {
        "species": "ivysaur",
        "level": 50,
        "types": ivysaur_data["types"],
        "hp": calculate_stat(ivysaur_base["hp"], 31, 0, 50, is_hp=True),
        "attack": calculate_stat(ivysaur_base["attack"], 31, 0, 50),
        "defense": calculate_stat(ivysaur_base["defense"], 31, 0, 50),
        "special_attack": calculate_stat(ivysaur_base["special-attack"], 31, 156, 50),
        "special_defense": calculate_stat(ivysaur_base["special-defense"], 31, 0, 50),
        "speed": calculate_stat(ivysaur_base["speed"], 31, 0, 50),
        "ability": None,
        "item": None,
        "is_terastallized": False,
        "is_grounded": True,  # Affected by Grassy Terrain
    }
    
    # Tyranitar: 0 HP / 0 SpD, Assault Vest
    # Rock type gets 1.5x SpD in Sandstorm
    tyranitar_data = POKEMON_DATA["tyranitar"]
    tyranitar_base = tyranitar_data["base_stats"]
    
    defender = {
        "species": "tyranitar",
        "level": 50,
        "types": tyranitar_data["types"],  # rock/dark
        "hp": calculate_stat(tyranitar_base["hp"], 31, 0, 50, is_hp=True),
        "attack": calculate_stat(tyranitar_base["attack"], 31, 0, 50),
        "defense": calculate_stat(tyranitar_base["defense"], 31, 0, 50),
        "special_attack": calculate_stat(tyranitar_base["special-attack"], 31, 0, 50),
        "special_defense": calculate_stat(tyranitar_base["special-defense"], 31, 0, 50),
        "speed": calculate_stat(tyranitar_base["speed"], 31, 0, 50),
        "ability": None,
        "item": "assault-vest",
        "is_terastallized": False,
    }
    
    move = {
        "name": "solar-beam",
        "power": 60,  # Reduced power (not in Sun)
        "type": "grass",
        "damage_class": "special",
    }
    
    field = {
        "weather": "sandstorm",
        "terrain": "grassy",
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
    
    expected = (42, 42, 42, 42, 44, 44, 44, 44, 44, 44, 48, 48, 48, 48, 48, 50)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"\nBase: {result.get('base_val')}")
    print(f"Attacker SpA: {attacker.get('special_attack')}")
    print(f"Defender HP: {defender.get('hp')}, SpD: {defender.get('special_defense')}")
    
    if result.get('debug'):
        dbg = result['debug']
        print(f"\nDebug info:")
        print(f"  A: {dbg.get('A')}, D: {dbg.get('D')}")
        print(f"  Type mult: {dbg.get('type_mult')}")
        print(f"  STAB: {dbg.get('stab')}")
        print(f"  Weather: {dbg.get('weather_mult')}")
        print(f"  Terrain: {dbg.get('terrain_mult')}")
        if dbg.get('effects'):
            print(f"  Effects: {dbg['effects']}")
    
    return actual == expected


if __name__ == "__main__":
    passed = test_ivysaur_tyranitar()
    print("\n" + "="*80)
    if passed:
        print("✓ TEST PASSED")
    else:
        print("✗ TEST FAILED")
    print("="*80)
