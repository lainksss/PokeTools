"""Test simple pour Kyogre vs Ivysaur."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from calculate_damages.calculate_damages import calculate_damage

# Load Pokemon data
POKEMON_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "all_pokemon.json"
with open(POKEMON_DATA_PATH, "r", encoding="utf-8") as f:
    POKEMON_DATA = json.load(f)


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


def test_kyogre_ivysaur():
    """0 SpA Tera-Water Kyogre Water Spout (150 BP) vs. 252 HP / 252+ SpD Eviolite Ivysaur in Rain: 51-60"""
    print("\n" + "="*80)
    print("TEST: 0 SpA Tera-Water Kyogre Water Spout vs. 252 HP / 252+ SpD Eviolite Ivysaur in Rain")
    print("="*80)
    
    # Kyogre: 0 EVs, neutral nature, Tera Water
    attacker = get_pokemon_stats(
        species="kyogre",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        natures={"special-attack": 1.0},  # Neutral (Hardi)
    )
    attacker["is_terastallized"] = True
    attacker["tera_type"] = "water"
    attacker["orig_types"] = ["water"]
    
    # Ivysaur: 252 HP / 252+ SpD, Prudent nature (+SpD), Eviolite
    defender = get_pokemon_stats(
        species="ivysaur",
        level=50,
        evs={"hp": 252, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 252, "speed": 0},
        natures={"special-defense": 1.1},  # Prudent (+SpD)
        item="eviolite"
    )
    defender["can_evolve"] = True
    
    move = {
        "name": "water-spout",
        "power": 150,
        "type": "water",
        "damage_class": "special",
        "targets": 2,  # Single target move
    }
    
    field = {
        "weather": "rain",
        "battle_mode": "double",  # DOUBLE BATTLE!
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
    
    expected = (51, 51, 52, 52, 53, 54, 54, 55, 55, 56, 57, 57, 58, 58, 59, 60)
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
        print(f"  Weather mult: {dbg.get('weather_mult')}")
    
    assert actual == expected


if __name__ == "__main__":
    passed = test_kyogre_ivysaur()
    print("\n" + "="*80)
    if passed:
        print("✓ TEST PASSED")
    else:
        print("✗ TEST FAILED")
    print("="*80)
