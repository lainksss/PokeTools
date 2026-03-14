"""Tests to verify that our calculations match exactly with Smogon damage calculator."""
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
    """Calculate a stat using the standard Pokemon formula.
    
    For HP: floor((2*base + IV + floor(EV/4)) * level / 100) + level + 10
    For other stats: floor((floor((2*base + IV + floor(EV/4)) * level / 100) + 5) * nature)
    """
    if is_hp:
        return int((2 * base + iv + ev // 4) * level / 100) + level + 10
    else:
        base_stat = int((2 * base + iv + ev // 4) * level / 100) + 5
        return int(base_stat * nature_mult)


def get_pokemon_stats(species: str, level: int, evs: dict, ivs: dict = None, natures: dict = None, item: str = None):
    """Retrieve and calculate Pokemon stats from the JSON file.
    
    Args:
        species: Pokemon name (e.g., "bulbasaur")
        level: Pokemon level
        evs: Dict of EVs by stat (e.g., {"hp": 252, "attack": 0, ...})
        ivs: Dict of IVs by stat (defaults to 31 everywhere)
        natures: Dict of nature multipliers (e.g., {"attack": 1.1, "defense": 0.9})
        item: Held item (optional)
    
    Returns:
        Dict with calculated stats and Pokemon info
    """
    if ivs is None:
        ivs = {"hp": 31, "attack": 31, "defense": 31, "special-attack": 31, "special-defense": 31, "speed": 31}
    
    if natures is None:
        natures = {"hp": 1.0, "attack": 1.0, "defense": 1.0, "special-attack": 1.0, "special-defense": 1.0, "speed": 1.0}
    
    pokemon = POKEMON_DATA[species]
    base_stats = pokemon["base_stats"]
    
    # Calculate stats BEFORE item boosts (Choice Band, Eviolite, etc.)
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


def test_case_1():
    """0 SpA Meadow Plate Ivysaur Solar Beam vs. 0 HP / 0 SpD Assault Vest Bulbasaur: 16-19"""
    print("\n" + "="*80)
    print("TEST 1: 0 SpA Meadow Plate Ivysaur Solar Beam vs. 0 HP / 0 SpD Assault Vest Bulbasaur")
    print("="*80)
    
    # 0 SpA = 0 EVs, neutral nature
    attacker = get_pokemon_stats(
        species="ivysaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        item="meadow-plate"
    )
    
    # 0 HP / 0 SpD = 0 EVs, neutral nature (Assault Vest will boost SpD)
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        item="assault-vest"
    )
    defender["can_evolve"] = True  # For Eviolite (not used here but good to know)
    
    move = {
        "name": "solar-beam",
        "power": 120,
        "type": "grass",
        "damage_class": "special",
    }
    
    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        random_range=range(85, 101),
        debug=True,
    )
    
    expected = (16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 18, 18, 18, 18, 18, 19)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Base: {result.get('base_val')}")
    print(f"Attacker stats: Attack={attacker.get('attack')}, SpA={attacker.get('special_attack')}")
    print(f"Defender stats: Defense={defender.get('defense')}, SpD={defender.get('special_defense')}")
    
    if result.get('debug'):
        dbg = result['debug']
        print(f"A: {dbg.get('A')}, D: {dbg.get('D')}, Type: {dbg.get('type_mult')}, STAB: {dbg.get('stab')}")
        print(f"Item mult: {dbg.get('item_mult')}, Other mult: {dbg.get('other_mult')}")
    
    assert actual == expected


def test_case_2():
    """156 SpA Life Orb Ivysaur Solar Beam vs. 0 HP / 0+ SpD Eviolite Bulbasaur: 18-22"""
    print("\n" + "="*80)
    print("TEST 2: 156 SpA Life Orb Ivysaur Solar Beam vs. 0 HP / 0+ SpD Eviolite Bulbasaur")
    print("="*80)
    
    # 156 SpA = 156 EVs, 31 IVs, neutral nature
    attacker = get_pokemon_stats(
        species="ivysaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 156, "special-defense": 0, "speed": 0},
        item="life-orb"
    )
    
    # 0+ SpD = 0 EVs, 31 IVs, positive nature (Eviolite will boost)
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        natures={"special-defense": 1.1},
        item="eviolite"
    )
    defender["can_evolve"] = True
    
    move = {
        "name": "solar-beam",
        "power": 120,
        "type": "grass",
        "damage_class": "special",
    }
    
    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        random_range=range(85, 101),
        debug=True,
    )
    
    expected = (18, 19, 19, 19, 19, 19, 19, 21, 21, 21, 21, 21, 21, 22, 22, 22)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Base: {result.get('base_val')}")
    print(f"Attacker stats: Attack={attacker.get('attack')}, SpA={attacker.get('special_attack')}")
    print(f"Defender stats: Defense={defender.get('defense')}, SpD={defender.get('special_defense')}")
    
    if result.get('debug'):
        dbg = result['debug']
        print(f"A: {dbg.get('A')}, D: {dbg.get('D')}, Type: {dbg.get('type_mult')}, STAB: {dbg.get('stab')}")
        print(f"Item mult: {dbg.get('item_mult')}, Other mult: {dbg.get('other_mult')}")
    
    assert actual == expected


def test_case_3():
    """156+ SpA Choice Specs Ivysaur Solar Beam vs. 252 HP / 252+ SpD Assault Vest Bulbasaur: 17-21"""
    print("\n" + "="*80)
    print("TEST 3: 156+ SpA Choice Specs Ivysaur Solar Beam vs. 252 HP / 252+ SpD Assault Vest Bulbasaur")
    print("="*80)
    
    # 156+ SpA = 156 EVs, 31 IVs, positive nature
    attacker = get_pokemon_stats(
        species="ivysaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 156, "special-defense": 0, "speed": 0},
        natures={"special-attack": 1.1},
        item="choice-specs"
    )
    
    # 252 HP / 252+ SpD = 252 EVs in both, positive SpD nature
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 252, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 252, "speed": 0},
        natures={"special-defense": 1.1},
        item="assault-vest"
    )
    defender["can_evolve"] = True
    
    move = {
        "name": "solar-beam",
        "power": 120,
        "type": "grass",
        "damage_class": "special",
    }
    
    # PAS de terrain cette fois !
    result = calculate_damage(
        move=move,
        attacker=attacker,
        defender=defender,
        level=50,
        random_range=range(85, 101),
        debug=True,
    )
    
    expected = (17, 18, 18, 18, 18, 18, 18, 19, 19, 19, 19, 19, 20, 20, 20, 21)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Base: {result.get('base_val')}")
    print(f"Attacker stats: Attack={attacker.get('attack')}, SpA={attacker.get('special_attack')}")
    print(f"Defender stats: Defense={defender.get('defense')}, SpD={defender.get('special_defense')}")
    
    if result.get('debug'):
        dbg = result['debug']
        print(f"A: {dbg.get('A')}, D: {dbg.get('D')}, Type: {dbg.get('type_mult')}, STAB: {dbg.get('stab')}")
        print(f"Terrain mult: {dbg.get('terrain_mult')}")
        print(f"Item mult: {dbg.get('item_mult')}, Other mult: {dbg.get('other_mult')}")
    
    assert actual == expected


def test_case_4():
    """252+ Atk Choice Band Groudon Heat Crash (120 BP) vs. 252 HP / 0 Def Eviolite Bulbasaur in Sun: 438-516"""
    print("\n" + "="*80)
    print("TEST 4: 252+ Atk Choice Band Groudon Heat Crash (120 BP) vs. 252 HP / 0 Def Eviolite Bulbasaur in Sun")
    print("="*80)
    
    # 252+ Atk = 252 EVs, 31 IVs, positive nature
    attacker = get_pokemon_stats(
        species="groudon",
        level=50,
        evs={"hp": 0, "attack": 252, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        natures={"attack": 1.1},
        item="choice-band"
    )
    
    # 252 HP / 0 Def = 252 HP EVs, 0 Def EVs
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 252, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        item="eviolite"
    )
    defender["can_evolve"] = True
    
    move = {
        "name": "heat-crash",
        "power": 120,  # Already calculated based on weight
        "type": "fire",
        "damage_class": "physical",
    }
    
    field = {
        "weather": "sun",
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
    
    expected = (438, 442, 448, 454, 458, 464, 468, 474, 478, 484, 490, 494, 500, 504, 510, 516)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Base: {result.get('base_val')}")
    
    if result.get('debug'):
        dbg = result['debug']
        print(f"A: {dbg.get('A')}, D: {dbg.get('D')}, Type: {dbg.get('type_mult')}, STAB: {dbg.get('stab')}")
        print(f"Weather mult: {dbg.get('weather_mult')}")
    
    assert actual == expected


def test_case_5():
    """252+ Atk Choice Band Tera-Fire Groudon Heat Crash (120 BP) vs. 252 HP / 0 Def Eviolite Bulbasaur in Sun: 656-774"""
    print("\n" + "="*80)
    print("TEST 5: 252+ Atk Choice Band Tera-Fire Groudon Heat Crash (120 BP) vs. 252 HP / 0 Def Eviolite Bulbasaur in Sun")
    print("="*80)
    
    # Same as Test 4
    attacker = get_pokemon_stats(
        species="groudon",
        level=50,
        evs={"hp": 0, "attack": 252, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        natures={"attack": 1.1},
        item="choice-band"
    )
    attacker["is_terastallized"] = True
    attacker["tera_type"] = "fire"
    attacker["orig_types"] = ["ground"]
    
    # Same as Test 4
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 252, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        item="eviolite"
    )
    defender["can_evolve"] = True
    
    move = {
        "name": "heat-crash",
        "power": 120,
        "type": "fire",
        "damage_class": "physical",
    }
    
    field = {
        "weather": "sun",
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
    
    expected = (656, 662, 672, 680, 686, 696, 702, 710, 716, 726, 734, 740, 750, 756, 764, 774)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Base: {result.get('base_val')}")
    
    if result.get('debug'):
        dbg = result['debug']
        print(f"A: {dbg.get('A')}, D: {dbg.get('D')}, Type: {dbg.get('type_mult')}, STAB: {dbg.get('stab')}")
        print(f"Weather mult: {dbg.get('weather_mult')}")
    
    assert actual == expected


def test_case_6():
    """156+ SpA Choice Specs Ivysaur Solar Beam vs. 252 HP / 252+ SpD Assault Vest Bulbasaur in Grassy Terrain: 22-27"""
    print("\n" + "="*80)
    print("TEST 6: 156+ SpA Choice Specs Ivysaur Solar Beam vs. 252 HP / 252+ SpD Assault Vest Bulbasaur in Grassy Terrain")
    print("="*80)
    
    # 156+ SpA = 156 EVs, 31 IVs, positive nature
    attacker = get_pokemon_stats(
        species="ivysaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 156, "special-defense": 0, "speed": 0},
        natures={"special-attack": 1.1},
        item="choice-specs"
    )
    attacker["is_grounded"] = True  # Affected by terrain
    
    # 252 HP / 252+ SpD = 252 EVs in both, positive SpD nature
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 252, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 252, "speed": 0},
        natures={"special-defense": 1.1},
        item="assault-vest"
    )
    defender["can_evolve"] = True
    
    move = {
        "name": "solar-beam",
        "power": 120,
        "type": "grass",
        "damage_class": "special",
    }
    
    field = {
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
    
    expected = (22, 22, 23, 23, 24, 24, 24, 24, 24, 25, 25, 25, 25, 26, 26, 27)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Base: {result.get('base_val')}")
    print(f"Attacker stats: Attack={attacker.get('attack')}, SpA={attacker.get('special_attack')}")
    print(f"Defender stats: Defense={defender.get('defense')}, SpD={defender.get('special_defense')}")
    
    if result.get('debug'):
        dbg = result['debug']
        print(f"A: {dbg.get('A')}, D: {dbg.get('D')}, Type: {dbg.get('type_mult')}, STAB: {dbg.get('stab')}")
        print(f"Terrain mult: {dbg.get('terrain_mult')}")
        print(f"Item mult: {dbg.get('item_mult')}, Other mult: {dbg.get('other_mult')}")
    
    assert actual == expected


def test_case_7():
    """252 SpA Choice Specs Solar Power Tera-Fire Charizard Solar Beam vs. 252 HP / 252+ SpD Assault Vest Bulbasaur in Sun: 27-32 (17.7 - 21%) in Grassy Terrain"""
    print("\n" + "="*80)
    print("TEST 7: 252 SpA Choice Specs Solar Power Tera-Fire Charizard Solar Beam vs. 252 HP / 252+ SpD Assault Vest Bulbasaur in Sun + Grassy Terrain")
    print("="*80)
    
    # 252 SpA = 252 EVs, 31 IVs, neutral nature
    # Charizard base SpA = 109
    # Solar Power boost 1.5x in sun
    # Choice Specs 1.5x
    # Tera Fire (changes type to Fire)
    attacker = get_pokemon_stats(
        species="charizard",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 252, "special-defense": 0, "speed": 0},
        natures={"special-attack": 1.0},  # Neutral
        item="choice-specs"
    )
    attacker["ability"] = "solar-power"
    attacker["is_terastallized"] = True
    attacker["tera_type"] = "grass"
    attacker["orig_types"] = ["fire", "flying"]
    attacker["types"] = ["fire"]  # After Tera
    attacker["is_grounded"] = True  # Affected by Grassy Terrain
    
    # 252 HP / 252+ SpD = 252 EVs in both, positive SpD nature
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 252, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 252, "speed": 0},
        natures={"special-defense": 1.1},
        item="assault-vest"
    )
    defender["can_evolve"] = True
    defender["is_grounded"] = True
    
    move = {
        "name": "solar-beam",
        "power": 120,
        "type": "grass",
        "damage_class": "special",
    }
    
    field = {
        "weather": "sun",
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
    
    expected = (41, 42, 42, 43, 43, 43, 44, 45, 45, 46, 46, 46, 47, 48, 48, 49)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Base: {result.get('base_val')}")
    print(f"Attacker stats: SpA={attacker.get('special_attack')}")
    print(f"Defender stats: HP={defender.get('hp')}, SpD={defender.get('special_defense')}")
    
    if result.get('debug'):
        dbg = result['debug']
        print(f"A: {dbg.get('A')}, D: {dbg.get('D')}, Type: {dbg.get('type_mult')}, STAB: {dbg.get('stab')}")
        print(f"Weather mult: {dbg.get('weather_mult')}")
        print(f"Terrain mult: {dbg.get('terrain_mult')}")
        print(f"Item mult: {dbg.get('item_mult')}, Other mult: {dbg.get('other_mult')}")
    
    if result.get('effects'):
        print(f"Effects: {result['effects']}")
    
    assert actual == expected


def test_case_8():
    """0 Atk Bulbasaur Fire Fang vs. 0 HP / 0 Def Bulbasaur (no modifiers)"""
    print("\n" + "="*80)
    print("TEST 8: 0 Atk Bulbasaur Fire Fang vs. 0 HP / 0 Def Bulbasaur (no modifiers)")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    
    move = {
        "name": "fire-fang",
        "power": 65,
        "type": "fire",
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
    
    expected = (50, 50, 52, 52, 52, 54, 54, 54, 54, 56, 56, 56, 58, 58, 58, 60)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Base: {result.get('base_val')}")
    
    assert actual == expected


def test_case_9():
    """0 Atk Bulbasaur Solar Blade vs. 0 HP / 0 Def Bulbasaur (no modifiers)"""
    print("\n" + "="*80)
    print("TEST 9: 0 Atk Bulbasaur Solar Blade vs. 0 HP / 0 Def Bulbasaur (no modifiers)")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    
    move = {
        "name": "solar-blade",
        "power": 125,
        "type": "grass",
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
    
    expected = (18, 18, 18, 18, 18, 19, 19, 19, 19, 19, 20, 20, 20, 20, 21, 21)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Base: {result.get('base_val')}")
    
    assert actual == expected


def test_case_10():
    """0 Atk Bulbasaur Helping Hand Fire Fang vs. 0 HP / 0 Def Bulbasaur"""
    print("\n" + "="*80)
    print("TEST 10: 0 Atk Bulbasaur Helping Hand Fire Fang vs. 0 HP / 0 Def Bulbasaur")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    
    move = {
        "name": "fire-fang",
        "power": 65,
        "type": "fire",
        "damage_class": "physical",
    }
    
    field = {
        "helping_hand": True,
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
    
    expected = (74, 74, 76, 76, 78, 78, 80, 80, 80, 82, 82, 84, 84, 86, 86, 88)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Base: {result.get('base_val')}")
    
    assert actual == expected


def test_case_11():
    """0 Atk Bulbasaur Helping Hand Solar Blade vs. 0 HP / 0 Def Bulbasaur"""
    print("\n" + "="*80)
    print("TEST 11: 0 Atk Bulbasaur Helping Hand Solar Blade vs. 0 HP / 0 Def Bulbasaur")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    
    move = {
        "name": "solar-blade",
        "power": 125,
        "type": "grass",
        "damage_class": "physical",
    }
    
    field = {
        "helping_hand": True,
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
    
    expected = (26, 27, 27, 27, 27, 28, 28, 28, 29, 29, 29, 30, 30, 30, 31, 31)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Base: {result.get('base_val')}")
    
    assert actual == expected


def test_case_12():
    """0 Atk Bulbasaur Fire Fang vs. 0 HP / 0 Def Bulbasaur with Friend Guard"""
    print("\n" + "="*80)
    print("TEST 12: 0 Atk Bulbasaur Fire Fang vs. 0 HP / 0 Def Bulbasaur with Friend Guard")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    
    move = {
        "name": "fire-fang",
        "power": 65,
        "type": "fire",
        "damage_class": "physical",
    }
    
    field = {
        "friend_guard": True,
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
    
    expected = (37, 37, 39, 39, 39, 40, 40, 40, 40, 42, 42, 42, 43, 43, 43, 45)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Base: {result.get('base_val')}")
    
    assert actual == expected


def test_case_13():
    """0 Atk Bulbasaur Solar Blade vs. 0 HP / 0 Def Bulbasaur with Friend Guard"""
    print("\n" + "="*80)
    print("TEST 13: 0 Atk Bulbasaur Solar Blade vs. 0 HP / 0 Def Bulbasaur with Friend Guard")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    
    move = {
        "name": "solar-blade",
        "power": 125,
        "type": "grass",
        "damage_class": "physical",
    }
    
    field = {
        "friend_guard": True,
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
    
    expected = (13, 13, 13, 13, 13, 14, 14, 14, 14, 14, 15, 15, 15, 15, 16, 16)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Base: {result.get('base_val')}")
    
    assert actual == expected


def test_case_14():
    """0 Atk Bulbasaur Helping Hand Fire Fang vs. 0 HP / 0 Def Bulbasaur with Friend Guard"""
    print("\n" + "="*80)
    print("TEST 14: 0 Atk Bulbasaur Helping Hand Fire Fang vs. 0 HP / 0 Def Bulbasaur with Friend Guard")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    
    move = {
        "name": "fire-fang",
        "power": 65,
        "type": "fire",
        "damage_class": "physical",
    }
    
    field = {
        "helping_hand": True,
        "friend_guard": True,
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
    
    expected = (55, 55, 57, 57, 58, 58, 60, 60, 60, 61, 61, 63, 63, 64, 64, 66)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Base: {result.get('base_val')}")
    
    assert actual == expected


def test_case_15():
    """0 Atk Bulbasaur Helping Hand Solar Blade vs. 0 HP / 0 Def Bulbasaur with Friend Guard"""
    print("\n" + "="*80)
    print("TEST 15: 0 Atk Bulbasaur Helping Hand Solar Blade vs. 0 HP / 0 Def Bulbasaur with Friend Guard")
    print("="*80)
    
    attacker = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    
    defender = get_pokemon_stats(
        species="bulbasaur",
        level=50,
        evs={"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
    )
    
    move = {
        "name": "solar-blade",
        "power": 125,
        "type": "grass",
        "damage_class": "physical",
    }
    
    field = {
        "helping_hand": True,
        "friend_guard": True,
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
    
    expected = (19, 20, 20, 20, 20, 21, 21, 21, 22, 22, 22, 22, 22, 22, 23, 23)
    actual = tuple(result['damage_all'])
    
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Match: {actual == expected}")
    print(f"Base: {result.get('base_val')}")
    
    assert actual == expected


if __name__ == "__main__":
    results = []
    
    results.append(("Test 1 - Meadow Plate", test_case_1()))
    results.append(("Test 2 - Life Orb", test_case_2()))
    results.append(("Test 3 - Choice Specs", test_case_3()))
    results.append(("Test 4 - Choice Band + Sun", test_case_4()))
    results.append(("Test 5 - Tera Fire + Choice Band + Sun", test_case_5()))
    results.append(("Test 6 - Choice Specs + Grassy Terrain", test_case_6()))
    results.append(("Test 7 - Solar Power + Tera Fire + Sun + Grassy Terrain", test_case_7()))
    results.append(("Test 8 - Fire Fang (no modifiers)", test_case_8()))
    results.append(("Test 9 - Solar Blade (no modifiers)", test_case_9()))
    results.append(("Test 10 - Fire Fang + Helping Hand", test_case_10()))
    results.append(("Test 11 - Solar Blade + Helping Hand", test_case_11()))
    results.append(("Test 12 - Fire Fang + Friend Guard", test_case_12()))
    results.append(("Test 13 - Solar Blade + Friend Guard", test_case_13()))
    results.append(("Test 14 - Fire Fang + Helping Hand + Friend Guard", test_case_14()))
    results.append(("Test 15 - Solar Blade + Helping Hand + Friend Guard", test_case_15()))
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll tests passed!")
    else:
        print(f"\n{total - passed} test(s) failed")
