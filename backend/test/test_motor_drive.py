import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculate_damages.calculate_damages import calculate_damage

def test_motor_drive_blocks_electric():
    """Test that Motor Drive blocks Electric-type moves"""
    attacker = {
        "pokemon_id": 25,
        "base_stats": {"hp": 35, "attack": 55, "defense": 40, "special-attack": 50, "special-defense": 50, "speed": 90},
        "evs": {"hp": 0, "attack": 0, "defense": 0, "special-attack": 252, "special-defense": 0, "speed": 252},
        "nature": "timid",
        "ability": "static",
        "item": None
    }
    
    # Defender: Blitzle with Motor Drive
    defender = {
        "pokemon_id": 522,
        "base_stats": {"hp": 45, "attack": 63, "defense": 37, "special-attack": 52, "special-defense": 41, "speed": 76},
        "evs": {"hp": 252, "attack": 0, "defense": 4, "special-attack": 0, "special-defense": 0, "speed": 252},
        "nature": "bold",
        "ability": "motor-drive",
        "item": None
    }
    
    # Move: Thunderbolt (Electric)
    move = {
        "name": "thunderbolt",
        "type": "electric",
        "power": 90,
        "accuracy": 100,
        "category": "special",
        "priority": 0,
        "flags": {"contact": False, "sound": False, "powder": False, "reflectable": True, "protect": True}
    }
    
    res = calculate_damage(
        attacker=attacker,
        defender=defender,
        move=move,
        field={"weather": None, "terrain": None, "battle_mode": "singles"},
        is_critical=False,
        defender_hp=100,
        gen=9
    )
    
    # Verify all damage rolls are 0
    assert all(d == 0 for d in res.get("damage_all", [])), \
        f"Motor Drive should block Thunderbolt, but got damage: {res.get('damage_all', [])}"
    
    # Verify effects
    assert res.get("effects", {}).get("immune") == "motor-drive", \
        f"Expected immune flag 'motor-drive', got {res.get('effects', {}).get('immune')}"
    assert res.get("effects", {}).get("motor_drive_activated") is True, \
        f"Expected motor_drive_activated=True"
    
    print("[OK] Motor Drive successfully blocks Electric moves (zero damage)")
    print(f"  - All damage rolls: {res['damage_all']}")
    print(f"  - Effects: immune={res['effects'].get('immune')}, motor_drive_activated={res['effects'].get('motor_drive_activated')}")


def test_motor_drive_allows_other_types():
    """Test that Motor Drive allows non-Electric moves"""
    attacker = {
        "pokemon_id": 25,
        "base_stats": {"hp": 35, "attack": 55, "defense": 40, "special-attack": 50, "special-defense": 50, "speed": 90},
        "evs": {"hp": 0, "attack": 252, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 4},
        "nature": "jolly",
        "ability": "static",
        "item": None
    }
    
    defender = {
        "pokemon_id": 522,
        "base_stats": {"hp": 45, "attack": 63, "defense": 37, "special-attack": 52, "special-defense": 41, "speed": 76},
        "evs": {"hp": 252, "attack": 0, "defense": 4, "special-attack": 0, "special-defense": 0, "speed": 252},
        "nature": "bold",
        "ability": "motor-drive",
        "item": None
    }
    
    # Flame Charge (Fire)
    move = {
        "name": "flame-charge",
        "type": "fire",
        "power": 50,
        "accuracy": 100,
        "category": "physical",
        "priority": 0,
        "flags": {"contact": False, "sound": False, "powder": False, "reflectable": True, "protect": True}
    }
    
    res = calculate_damage(
        attacker=attacker,
        defender=defender,
        move=move,
        field={"weather": None, "terrain": None, "battle_mode": "singles"},
        is_critical=False,
        defender_hp=100,
        gen=9
    )
    
    # Verify damage is non-zero
    assert max(res.get("damage_all", [0])) > 0, \
        f"Motor Drive should allow Fire moves, but got zero damage: {res}"
    
    # Verify no immunity
    assert res.get("effects", {}).get("immune") != "motor-drive", \
        f"Expected no motor-drive immunity for Fire move"
    
    print("[OK] Motor Drive allows non-Electric moves")
    print(f"  - Damage rolls: {res['damage_all'][:3]}...")


if __name__ == "__main__":
    test_motor_drive_blocks_electric()
    test_motor_drive_allows_other_types()
    print("\n[PASS] All Motor Drive tests passed!")
