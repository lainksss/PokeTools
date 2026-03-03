import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculate_damages.calculate_damages import calculate_damage

def test_bulletproof_blocks_ball_moves():
    """Test that Bulletproof blocks ball/bomb moves (ballistics flag)"""
    # Attacker: Pikachu with basic stats
    attacker = {
        "pokemon_id": 25,
        "base_stats": {
            "hp": 35,
            "attack": 55,
            "defense": 40,
            "special-attack": 50,
            "special-defense": 50,
            "speed": 90
        },
        "evs": {"hp": 0, "attack": 0, "defense": 0, "special-attack": 252, "special-defense": 0, "speed": 252},
        "nature": "timid",
        "ability": "static",
        "item": None
    }
    
    # Defender: Escavalier with Bulletproof
    defender = {
        "pokemon_id": 475,
        "base_stats": {
            "hp": 65,
            "attack": 131,
            "defense": 95,
            "special-attack": 66,
            "special-defense": 65,
            "speed": 28
        },
        "evs": {"hp": 252, "attack": 0, "defense": 4, "special-attack": 0, "special-defense": 0, "speed": 252},
        "nature": "bold",
        "ability": "bulletproof",
        "item": None
    }
    
    # Move: Seed Bomb (ballistics flag)
    move = {
        "name": "seed-bomb",
        "type": "grass",
        "power": 80,
        "accuracy": 100,
        "category": "physical",
        "priority": 0,
        "flags": {"contact": False, "sound": False, "powder": False, "reflectable": True, "protect": True}
    }
    
    # Calculate damage
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
        f"Bulletproof should block Seed Bomb, but got damage: {res.get('damage_all', [])}"
    
    # Verify effects
    assert res.get("effects", {}).get("immune") == "bulletproof", \
        f"Expected immune flag 'bulletproof', got {res.get('effects', {}).get('immune')}"
    assert res.get("effects", {}).get("bulletproof_activated") is True, \
        f"Expected bulletproof_activated=True, got {res.get('effects', {}).get('bulletproof_activated')}"
    
    print("[OK] Bulletproof successfully blocks ball/bomb moves (zero damage)")
    print(f"  - All damage rolls: {res['damage_all']}")
    print(f"  - Effects: immune={res['effects'].get('immune')}, bulletproof_activated={res['effects'].get('bulletproof_activated')}")


def test_bulletproof_allows_normal_moves():
    """Test that Bulletproof allows non-ball/bomb moves"""
    attacker = {
        "pokemon_id": 25,
        "base_stats": {"hp": 35, "attack": 55, "defense": 40, "special-attack": 50, "special-defense": 50, "speed": 90},
        "evs": {"hp": 0, "attack": 252, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 4},
        "nature": "jolly",
        "ability": "static",
        "item": None
    }
    
    defender = {
        "pokemon_id": 475,
        "base_stats": {"hp": 65, "attack": 131, "defense": 95, "special-attack": 66, "special-defense": 65, "speed": 28},
        "evs": {"hp": 252, "attack": 0, "defense": 4, "special-attack": 0, "special-defense": 0, "speed": 252},
        "nature": "bold",
        "ability": "bulletproof",
        "item": None
    }
    
    # Tackle is NOT a ball/bomb move
    move = {
        "name": "tackle",
        "type": "normal",
        "power": 40,
        "accuracy": 100,
        "category": "physical",
        "priority": 0,
        "flags": {"contact": True, "sound": False, "powder": False, "reflectable": False, "protect": True}
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
        f"Bulletproof should allow Tackle, but got zero damage: {res}"
    
    # Verify no immunity
    assert res.get("effects", {}).get("immune") != "bulletproof", \
        f"Expected no bulletproof immunity for Tackle, but got immune={res.get('effects', {}).get('immune')}"
    
    print("[OK] Bulletproof allows non-ball/bomb moves")
    print(f"  - Damage rolls: {res['damage_all'][:3]}...")


if __name__ == "__main__":
    test_bulletproof_blocks_ball_moves()
    test_bulletproof_allows_normal_moves()
    print("\n[PASS] All Bulletproof tests passed!")
