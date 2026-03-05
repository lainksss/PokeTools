import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculate_damages.calculate_damages import calculate_damage

def test_wonder_guard_blocks_not_super_effective():
    """Test that Wonder Guard blocks moves that are NOT super-effective"""
    attacker = {
        "pokemon_id": 25,
        "base_stats": {"hp": 35, "attack": 55, "defense": 40, "special-attack": 50, "special-defense": 50, "speed": 90},
        "evs": {"hp": 0, "attack": 252, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 4},
        "nature": "jolly",
        "ability": "static",
        "item": None
    }
    
    # Defender: Shedinja with Wonder Guard
    defender = {
        "pokemon_id": 292,
        "base_stats": {"hp": 1, "attack": 90, "defense": 45, "special-attack": 30, "special-defense": 30, "speed": 75},
        "evs": {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        "nature": "jolly",
        "ability": "wonder-guard",
        "item": None,
        "types": ["bug", "ghost"]  # Shedinja's types: Bug/Ghost
    }
    
    # Move: Tackle (Normal type) - NOT super-effective against Shedinja
    move = {
        "name": "tackle",
        "type": "normal",
        "power": 40,
        "accuracy": 100,
        "category": "physical",
        "priority": 0,
        "flags": {"contact": True, "protect": True, "mirror": True}
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
        f"Wonder Guard should block Tackle (not super-effective), but got damage: {res.get('damage_all', [])}"
    
    # Verify effects
    assert res.get("effects", {}).get("immune") == "wonder-guard", \
        f"Expected immune flag 'wonder-guard', got {res.get('effects', {}).get('immune')}"
    assert res.get("effects", {}).get("wonder_guard_blocked") is True, \
        f"Expected wonder_guard_blocked=True"
    
    print("[OK] Wonder Guard successfully blocks non-super-effective moves")
    print(f"  - All damage rolls: {res['damage_all']}")
    print(f"  - Effects: immune={res['effects'].get('immune')}, wonder_guard_blocked={res['effects'].get('wonder_guard_blocked')}")


def test_wonder_guard_allows_super_effective():
    """Test that Wonder Guard allows super-effective moves"""
    # Attacker: Alakazam (high Special Attack)
    attacker = {
        "pokemon_id": 65,
        "base_stats": {"hp": 35, "attack": 35, "defense": 30, "special-attack": 120, "special-defense": 95, "speed": 120},
        "evs": {"hp": 0, "attack": 0, "defense": 0, "special-attack": 252, "special-defense": 0, "speed": 252},
        "nature": "timid",
        "ability": "magic-guard",
        "item": None
    }
    
    # Defender: Shedinja with Wonder Guard - Bug/Ghost type
    defender = {
        "pokemon_id": 292,
        "base_stats": {"hp": 1, "attack": 90, "defense": 45, "special-attack": 30, "special-defense": 30, "speed": 75},
        "evs": {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0},
        "nature": "jolly",
        "ability": "wonder-guard",
        "item": None,
        "types": ["bug", "ghost"]  # Bug/Ghost: weak to Rock, Fire, Flying, Ghost, Dark
    }
    
    # Move: Psychic (Psychic type) - NEUTRAL to Ghost but let's use a clearly super-effective move
    # Actually, use Fire Blast which is super-effective against Bug
    move = {
        "name": "fire-blast",
        "type": "fire",
        "power": 110,
        "accuracy": 85,
        "category": "special",
        "priority": 0,
        "flags": {"contact": False, "protect": True, "mirror": True}
    }
    
    res = calculate_damage(
        attacker=attacker,
        defender=defender,
        move=move,
        field={"weather": None, "terrain": None, "battle_mode": "singles"},
        is_critical=False,
        defender_hp=1,
        gen=9
    )
    
    # Fire is super-effective against Bug (2x), so type_mult should be > 1.0
    # Check if any damage roll is > 0 (there should be since it's super-effective)
    max_dam = max(res.get("damage_all", [0]))
    print(f"DEBUG: Damage rolls for Fire Blast (type_mult=2x Bug): {res['damage_all']}")
    print(f"DEBUG: Effects: {res.get('effects', {})}")
    
    # Since Fire is super-effective against Bug, Wonder Guard should NOT block
    # However, if type_mult is blocked, let's verify Wonder Guard DID NOT activate
    if res.get("effects", {}).get("wonder_guard_blocked"):
        print("WARNING: Wonder Guard blocked even though move is super-effective!")
        # This means our logic is still blocking - let's check type_mult
        assert False, "Wonder Guard should NOT have blocked a super-effective move"
    
    assert max_dam > 0, \
        f"Wonder Guard should allow super-effective moves (Fire on Bug), but got zero damage: {res}"
    
    print("[OK] Wonder Guard allows super-effective moves")
    print(f"  - Damage rolls: {res['damage_all'][:3]}...")


if __name__ == "__main__":
    test_wonder_guard_blocks_not_super_effective()
    test_wonder_guard_allows_super_effective()
    print("\n[PASS] All Wonder Guard tests passed!")
