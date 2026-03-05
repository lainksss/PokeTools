import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculate_damages.calculate_damages import calculate_damage

def test_soundproof_blocks_sound_moves():
    """Test that Soundproof blocks sound-based moves"""
    attacker = {
        "pokemon_id": 25,
        "base_stats": {"hp": 35, "attack": 55, "defense": 40, "special-attack": 50, "special-defense": 50, "speed": 90},
        "evs": {"hp": 0, "attack": 0, "defense": 0, "special-attack": 252, "special-defense": 0, "speed": 252},
        "nature": "timid",
        "ability": "static",
        "item": None
    }
    
    # Defender: Whismur with Soundproof
    defender = {
        "pokemon_id": 293,
        "base_stats": {"hp": 64, "attack": 66, "defense": 52, "special-attack": 66, "special-defense": 52, "speed": 60},
        "evs": {"hp": 252, "attack": 0, "defense": 4, "special-attack": 0, "special-defense": 0, "speed": 252},
        "nature": "bold",
        "ability": "soundproof",
        "item": None
    }
    
    # Move: Hyper Voice (Sound-based)
    move = {
        "name": "hyper-voice",
        "type": "normal",
        "power": 90,
        "accuracy": 100,
        "category": "special",
        "priority": 0,
        "flags": {"contact": False, "sound": True, "powder": False, "reflectable": True, "protect": True}
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
    
    # Verify all damage rolls are 0 (flag should come from _MOVES_WITH_FLAGS)
    assert all(d == 0 for d in res.get("damage_all", [])), \
        f"Soundproof should block sound moves, but got damage: {res.get('damage_all', [])}"
    
    # Verify effects
    assert res.get("effects", {}).get("immune") == "soundproof", \
        f"Expected immune flag 'soundproof', got {res.get('effects', {}).get('immune')}"
    assert res.get("effects", {}).get("soundproof_activated") is True, \
        f"Expected soundproof_activated=True"
    
    print("[OK] Soundproof successfully blocks sound moves (zero damage)")
    print(f"  - All damage rolls: {res['damage_all']}")
    print(f"  - Effects: immune={res['effects'].get('immune')}, soundproof_activated={res['effects'].get('soundproof_activated')}")


def test_cacophony_blocks_sound_moves():
    """Test that Cacophony (alternate ability) blocks sound moves"""
    attacker = {
        "pokemon_id": 25,
        "base_stats": {"hp": 35, "attack": 55, "defense": 40, "special-attack": 50, "special-defense": 50, "speed": 90},
        "evs": {"hp": 0, "attack": 0, "defense": 0, "special-attack": 252, "special-defense": 0, "speed": 252},
        "nature": "timid",
        "ability": "static",
        "item": None
    }
    
    # Defender: Pokemon with Cacophony
    defender = {
        "pokemon_id": 293,
        "base_stats": {"hp": 64, "attack": 66, "defense": 52, "special-attack": 66, "special-defense": 52, "speed": 60},
        "evs": {"hp": 252, "attack": 0, "defense": 4, "special-attack": 0, "special-defense": 0, "speed": 252},
        "nature": "bold",
        "ability": "cacophony",
        "item": None
    }
    
    # Move: Hyper Voice (Sound-based, has damage)
    move = {
        "name": "hyper-voice",
        "type": "normal",
        "power": 90,
        "accuracy": 100,
        "category": "special",
        "priority": 0,
        "flags": {"contact": False, "sound": True, "powder": False, "reflectable": True, "protect": True}
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
        f"Cacophony should block sound moves, but got damage: {res.get('damage_all', [])}"
    
    # Verify effects
    assert res.get("effects", {}).get("immune") == "cacophony", \
        f"Expected immune flag 'cacophony', got {res.get('effects', {}).get('immune')}"
    assert res.get("effects", {}).get("cacophony_activated") is True, \
        f"Expected cacophony_activated=True"
    
    print("[OK] Cacophony successfully blocks sound moves (zero damage)")
    print(f"  - All damage rolls: {res['damage_all']}")
    print(f"  - Effects: immune={res['effects'].get('immune')}, cacophony_activated={res['effects'].get('cacophony_activated')}")


def test_soundproof_allows_non_sound_moves():
    """Test that Soundproof allows non-sound moves"""
    attacker = {
        "pokemon_id": 25,
        "base_stats": {"hp": 35, "attack": 55, "defense": 40, "special-attack": 50, "special-defense": 50, "speed": 90},
        "evs": {"hp": 0, "attack": 252, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 4},
        "nature": "jolly",
        "ability": "static",
        "item": None
    }
    
    defender = {
        "pokemon_id": 293,
        "base_stats": {"hp": 64, "attack": 66, "defense": 52, "special-attack": 66, "special-defense": 52, "speed": 60},
        "evs": {"hp": 252, "attack": 0, "defense": 4, "special-attack": 0, "special-defense": 0, "speed": 252},
        "nature": "bold",
        "ability": "soundproof",
        "item": None
    }
    
    # Tackle (not sound)
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
        f"Soundproof should allow non-sound moves, but got zero damage: {res}"
    
    # Verify no immunity
    assert res.get("effects", {}).get("immune") != "soundproof", \
        f"Expected no soundproof immunity"
    
    print("[OK] Soundproof allows non-sound moves")
    print(f"  - Damage rolls: {res['damage_all'][:3]}...")


if __name__ == "__main__":
    test_soundproof_blocks_sound_moves()
    test_cacophony_blocks_sound_moves()
    test_soundproof_allows_non_sound_moves()
    print("\n[PASS] All Soundproof/Cacophony tests passed!")
