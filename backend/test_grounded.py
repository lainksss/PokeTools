"""Test is_grounded function with various conditions."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from calculate_damages.calculate_grounded import is_grounded


def test_grounded_cases():
    """Test various grounding scenarios."""
    print("\n" + "="*80)
    print("TEST: is_grounded function")
    print("="*80)
    
    tests = []
    
    # Test 1: Normal grounded Pokémon (Pikachu)
    pikachu = {"types": ["electric"], "ability": "static", "item": None}
    result = is_grounded(pikachu)
    tests.append(("Pikachu (grounded)", result == True, result))
    
    # Test 2: Flying type ungrounded (Pidgeot)
    pidgeot = {"types": ["normal", "flying"], "ability": "keen-eye", "item": None}
    result = is_grounded(pidgeot)
    tests.append(("Pidgeot (flying type)", result == False, result))
    
    # Test 3: Levitate ability ungrounded (Gengar)
    gengar = {"types": ["ghost", "poison"], "ability": "levitate", "item": None}
    result = is_grounded(gengar)
    tests.append(("Gengar (levitate)", result == False, result))
    
    # Test 4: Air Balloon ungrounded
    garchomp = {"types": ["dragon", "ground"], "ability": "sand-veil", "item": "air-balloon"}
    result = is_grounded(garchomp)
    tests.append(("Garchomp (air balloon)", result == False, result))
    
    # Test 5: Air Balloon popped (grounded)
    garchomp_popped = {"types": ["dragon", "ground"], "ability": "sand-veil", "item": "air-balloon", "air_balloon_popped": True}
    result = is_grounded(garchomp_popped)
    tests.append(("Garchomp (balloon popped)", result == True, result))
    
    # Test 6: Magnet Rise active (ungrounded)
    raichu = {"types": ["electric"], "ability": "static", "item": None, "magnet_rise": True}
    result = is_grounded(raichu)
    tests.append(("Raichu (magnet rise)", result == False, result))
    
    # Test 7: Telekinesis active (ungrounded)
    mewtwo = {"types": ["psychic"], "ability": "pressure", "item": None, "telekinesis": True}
    result = is_grounded(mewtwo)
    tests.append(("Mewtwo (telekinesis)", result == False, result))
    
    # Test 8: Gravity forces grounded (Flying type in Gravity)
    pidgeot_gravity = {"types": ["normal", "flying"], "ability": "keen-eye", "item": None}
    field_gravity = {"gravity": True}
    result = is_grounded(pidgeot_gravity, field_gravity)
    tests.append(("Pidgeot (flying + gravity)", result == True, result))
    
    # Test 9: Gravity overrides Levitate
    gengar_gravity = {"types": ["ghost", "poison"], "ability": "levitate", "item": None}
    result = is_grounded(gengar_gravity, field_gravity)
    tests.append(("Gengar (levitate + gravity)", result == True, result))
    
    # Test 10: Smack Down forces grounded
    pidgeot_smackdown = {"types": ["normal", "flying"], "ability": "keen-eye", "item": None, "smack_down": True}
    result = is_grounded(pidgeot_smackdown)
    tests.append(("Pidgeot (smack down)", result == True, result))
    
    # Test 11: Ingrain forces grounded
    venusaur = {"types": ["grass", "poison"], "ability": "overgrow", "item": None, "ingrain": True}
    result = is_grounded(venusaur)
    tests.append(("Venusaur (ingrain)", result == True, result))
    
    # Print results
    print()
    passed = 0
    failed = 0
    for name, expected, actual in tests:
        status = "✓ PASS" if expected else "✗ FAIL"
        print(f"{status}: {name} -> {actual}")
        if expected:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*80)
    print(f"SUMMARY: {passed}/{len(tests)} tests passed")
    print("="*80)
    
    return failed == 0


if __name__ == "__main__":
    success = test_grounded_cases()
    sys.exit(0 if success else 1)
