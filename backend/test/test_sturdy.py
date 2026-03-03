import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculate_damages.calculate_damages import calculate_damage

def test_sturdy_survives_at_full_hp():
    """Test that Sturdy survives KO when at full HP"""
    attacker = {
        "pokemon_id": 445,
        "name": "garchomp",
        "types": ["dragon", "ground"],
        "base_stats": {"hp": 108, "attack": 130, "defense": 95, "special-attack": 80, "special-defense": 85, "speed": 102},
        "evs": {"hp": 0, "attack": 252, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 4},
        "ivs": {"hp": 31, "attack": 31, "defense": 31, "special-attack": 31, "special-defense": 31, "speed": 31},
        "nature": "adamant",
        "ability": "rough-skin",
        "item": None,
        "is_terastallized": False,
        "tera_type": None,
        "stages": {}
    }
    
    defender = {
        "pokemon_id": 74,
        "name": "geodude",
        "types": ["rock", "ground"],
        "base_stats": {"hp": 40, "attack": 80, "defense": 100, "special-attack": 30, "special-defense": 30, "speed": 20},
        "evs": {"hp": 252, "attack": 0, "defense": 4, "special-attack": 0, "special-defense": 252, "speed": 0},
        "ivs": {"hp": 31, "attack": 31, "defense": 31, "special-attack": 31, "special-defense": 31, "speed": 31},
        "nature": "calm",
        "ability": "sturdy",
        "item": None,
        "is_terastallized": False,
        "tera_type": None,
        "stages": {},
        "max_hp": 142
    }
    
    move = {
        "name": "earthquake",
        "type": "ground",
        "power": 100,
        "accuracy": 100,
        "pp": 10,
        "damage_class": "physical",
        "category": "physical",
        "priority": 0,
        "target": "all_adjacent_foes",
        "flags": {}
    }
    
    max_hp = 142
    
    result = calculate_damage(
        move,
        attacker,
        defender,
        level=50,
        defender_hp=max_hp,
        is_critical=False,
        gen=9
    )
    
    damage_rolls = result.get("damage_all", [])
    remaining_hp = result.get("remaining_hp_all", [])
    effects = result.get("effects", {})
    
    assert all(dmg <= max_hp - 1 for dmg in damage_rolls), \
        f"Sturdy damage should be capped at {max_hp - 1}, got {damage_rolls}"
    
    assert all(hp >= 1 for hp in remaining_hp), \
        f"Sturdy should guarantee survival at 1+ HP, got {remaining_hp}"
    
    assert effects.get("sturdy_activated") is True, \
        f"sturdy_activated should be True, got {effects}"
    
    print(f"[OK] Sturdy survives KO at full HP (max damage: {max(damage_rolls)}, min HP: {min(remaining_hp)})")


def test_sturdy_no_protection_when_damaged():
    """Test that Sturdy does NOT protect when not at full HP"""
    attacker = {
        "pokemon_id": 445,
        "name": "garchomp",
        "types": ["dragon", "ground"],
        "base_stats": {"hp": 108, "attack": 130, "defense": 95, "special-attack": 80, "special-defense": 85, "speed": 102},
        "evs": {"hp": 0, "attack": 252, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 4},
        "ivs": {"hp": 31, "attack": 31, "defense": 31, "special-attack": 31, "special-defense": 31, "speed": 31},
        "nature": "adamant",
        "ability": "rough-skin",
        "item": None,
        "is_terastallized": False,
        "tera_type": None,
        "stages": {}
    }
    
    defender = {
        "pokemon_id": 74,
        "name": "geodude",
        "types": ["rock", "ground"],
        "base_stats": {"hp": 40, "attack": 80, "defense": 100, "special-attack": 30, "special-defense": 30, "speed": 20},
        "evs": {"hp": 252, "attack": 0, "defense": 4, "special-attack": 0, "special-defense": 252, "speed": 0},
        "ivs": {"hp": 31, "attack": 31, "defense": 31, "special-attack": 31, "special-defense": 31, "speed": 31},
        "nature": "calm",
        "ability": "sturdy",
        "item": None,
        "is_terastallized": False,
        "tera_type": None,
        "stages": {},
        "max_hp": 142
    }
    
    move = {
        "name": "earthquake",
        "type": "ground",
        "power": 100,
        "accuracy": 100,
        "pp": 10,
        "damage_class": "physical",
        "category": "physical",
        "priority": 0,
        "target": "all_adjacent_foes",
        "flags": {}
    }
    
    max_hp = 142
    result_full = calculate_damage(
        move,
        attacker,
        defender,
        level=50,
        defender_hp=max_hp,
        is_critical=False,
        gen=9
    )
    damage_full = result_full.get("damage_all", [])[0]
    
    damaged_hp = 80
    result_partial = calculate_damage(
        move,
        attacker,
        defender,
        level=50,
        defender_hp=damaged_hp,
        is_critical=False,
        gen=9
    )
    damage_partial = result_partial.get("damage_all", [])[0]
    
    assert damage_partial == damage_full, \
        f"Earthquake should do same damage regardless of HP, got {damage_full} vs {damage_partial}"
    
    effects_partial = result_partial.get("effects", {})
    assert effects_partial.get("sturdy_activated") is not True, \
        f"Sturdy should NOT be activated when not at full HP, got {effects_partial}"
    
    print(f"[OK] Sturdy does not protect when not at full HP (damage: {damage_partial})")


if __name__ == "__main__":
    try:
        test_sturdy_survives_at_full_hp()
        test_sturdy_no_protection_when_damaged()
        print("\n[PASS] All Sturdy tests passed!")
    except AssertionError as e:
        print(f"\n[FAIL] {e}")
        sys.exit(1)
