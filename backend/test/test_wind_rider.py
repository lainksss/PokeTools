import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculate_damages.calculate_damages import calculate_damage

def test_wind_rider_blocks_wind_moves():
    """Test that Wind Rider blocks wind-based moves"""
    attacker = {
        "pokemon_id": 16,
        "base_stats": {"hp": 40, "attack": 35, "defense": 40, "special-attack": 35, "special-defense": 35, "speed": 56},
        "evs": {"hp": 0, "attack": 0, "defense": 0, "special-attack": 252, "special-defense": 0, "speed": 252},
        "nature": "timid",
        "ability": "keen-eye",
        "item": None
    }
    
    # Defender: Rufflet with Wind Rider
    defender = {
        "pokemon_id": 627,
        "base_stats": {"hp": 50, "attack": 86, "defense": 56, "special-attack": 48, "special-defense": 42, "speed": 57},
        "evs": {"hp": 252, "attack": 0, "defense": 4, "special-attack": 0, "special-defense": 0, "speed": 252},
        "nature": "jolly",
        "ability": "wind-rider",
        "item": None
    }
    
    # Move: Razor Wind (Wind move)
    move = {
        "name": "razor-wind",
        "type": "normal",
        "power": 60,
        "accuracy": 100,
        "category": "special",
        "priority": 0,
        "flags": {"charge": True, "protect": True, "mirror": True}
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
        f"Wind Rider should block Razor Wind, but got damage: {res.get('damage_all', [])}"
    
    # Verify effects
    assert res.get("effects", {}).get("immune") == "wind-rider", \
        f"Expected immune flag 'wind-rider', got {res.get('effects', {}).get('immune')}"
    assert res.get("effects", {}).get("wind_rider_activated") is True, \
        f"Expected wind_rider_activated=True"
    
    print("[OK] Wind Rider successfully blocks wind moves (zero damage)")
    print(f"  - All damage rolls: {res['damage_all']}")
    print(f"  - Effects: immune={res['effects'].get('immune')}, wind_rider_activated={res['effects'].get('wind_rider_activated')}")


def test_wind_rider_allows_non_wind_moves():
    """Test that Wind Rider allows non-wind moves"""
    attacker = {
        "pokemon_id": 16,
        "base_stats": {"hp": 40, "attack": 35, "defense": 40, "special-attack": 35, "special-defense": 35, "speed": 56},
        "evs": {"hp": 0, "attack": 252, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 4},
        "nature": "jolly",
        "ability": "keen-eye",
        "item": None
    }
    
    defender = {
        "pokemon_id": 627,
        "base_stats": {"hp": 50, "attack": 86, "defense": 56, "special-attack": 48, "special-defense": 42, "speed": 57},
        "evs": {"hp": 252, "attack": 0, "defense": 4, "special-attack": 0, "special-defense": 0, "speed": 252},
        "nature": "jolly",
        "ability": "wind-rider",
        "item": None
    }
    
    # Tackle (normal move, not wind)
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
    
    # Verify damage is non-zero
    assert max(res.get("damage_all", [0])) > 0, \
        f"Wind Rider should allow non-wind moves, but got zero damage: {res}"
    
    # Verify no immunity
    assert res.get("effects", {}).get("immune") != "wind-rider", \
        f"Expected no wind-rider immunity"
    
    print("[OK] Wind Rider allows non-wind moves")
    print(f"  - Damage rolls: {res['damage_all'][:3]}...")


if __name__ == "__main__":
    test_wind_rider_blocks_wind_moves()
    test_wind_rider_allows_non_wind_moves()
    print("\n[PASS] All Wind Rider tests passed!")
