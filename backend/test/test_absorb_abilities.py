"""Tests for absorb/immune abilities: water-absorb, volt-absorb, dry-skin, flash-fire, lightning-rod."""
import sys
from pathlib import Path
# Ensure backend package root is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from calculate_damages.calculate_damages import calculate_damage


def make_move(name: str, mv_type: str, power: int = 90):
    return {"name": name, "type": mv_type, "power": power, "damage_class": "special", "targets": 1}


def run_absorb_test(ability: str, mv_name: str, mv_type: str, expect_heal: bool):
    print("\nTEST:", ability, "against", mv_type)
    attacker = {"types": [mv_type], "ability": None}
    defender = {"types": ["normal"], "ability": ability, "hp": 50, "max_hp": 200}
    move = make_move(mv_name, mv_type, 90)

    res = calculate_damage(move=move, attacker=attacker, defender=defender, level=50, random_range=range(85, 101), field={}, debug=True)

    dmg_list = res.get("damage_all", [])
    # Expect every roll to deal 0 damage for true absorption/immunity
    all_zero = all(d == 0 for d in dmg_list)
    assert all_zero, f"{ability} should absorb {mv_type} moves (got damages: {dmg_list})"

    effects = res.get("effects", {})
    assert effects.get("absorbed") == ability or (ability == "flash-fire" and effects.get("absorbed") == "flash-fire") or (ability == "lightning-rod" and effects.get("absorbed") == "lightning-rod"), (
        f"ability '{ability}' did not set absorbed effect, effects: {effects}"
    )

    healed = res.get("healed")
    if expect_heal:
        assert healed and healed.get("amount", 0) > 0, f"{ability} should have healed but healed={healed}"
    else:
        # flash-fire and lightning-rod do not heal by default in our implementation
        assert healed is None or healed.get("amount", 0) == 0, f"{ability} should not heal (healed={healed})"


def test_water_absorb_and_dry_skin():
    run_absorb_test("water-absorb", "surf", "water", expect_heal=True)
    run_absorb_test("dry-skin", "hydro-pump", "water", expect_heal=True)
    # Earth Eater heals from Ground moves
    run_absorb_test("earth-eater", "earthquake", "ground", expect_heal=True)


def test_volt_absorb_and_lightning_rod_and_flash_fire():
    run_absorb_test("volt-absorb", "thunderbolt", "electric", expect_heal=True)
    run_absorb_test("lightning-rod", "thunder", "electric", expect_heal=False)
    run_absorb_test("flash-fire", "flare-blitz", "fire", expect_heal=False)
    # Storm Drain absorbs water moves and triggers activation (no heal)
    run_absorb_test("storm-drain", "surf", "water", expect_heal=False)


if __name__ == "__main__":
    test_water_absorb_and_dry_skin()
    test_volt_absorb_and_lightning_rod_and_flash_fire()
    print("All absorb tests passed")
