"""Tests for sap-sipper ability: immunity to Grass-type moves."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from calculate_damages.calculate_damages import calculate_damage


def test_sap_sipper_boosts_attack():
    """Sap Sipper grants immunity to Grass attacks and marks activation."""
    print("\nTEST: sap-sipper immunity to grass moves")
    
    attacker = {"types": ["grass"], "ability": None}
    defender = {"types": ["normal"], "ability": "sap-sipper", "hp": 100, "max_hp": 100}
    move = {"name": "solar-beam", "type": "grass", "power": 120, "damage_class": "special", "targets": 1}
    
    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, random_range=range(85, 101))
    
    dmg_list = res.get("damage_all", [])
    # All rolls should deal 0 damage due to immunity
    assert all(d == 0 for d in dmg_list), f"Sap Sipper should block Grass moves, got damages: {dmg_list}"
    
    # Check that the ability is marked as activated
    effects = res.get("effects", {})
    assert effects.get("immune") == "sap-sipper", f"Expected immune=sap-sipper, got: {effects}"
    assert effects.get("sap_sipper_activated") == True, f"Expected sap_sipper_activated flag, got: {effects}"
    
    print("✓ PASS: sap-sipper blocks Grass moves and is marked as activated")


if __name__ == "__main__":
    test_sap_sipper_boosts_attack()
    print("\nAll sap-sipper tests passed!")
