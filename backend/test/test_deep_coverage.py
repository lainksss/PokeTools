from calculate_damages.calculate_damages import calculate_damage
from utils.data_loader import load_json
from utils.helpers import build_actor_from_payload


def test_deep_coverage_prefers_bulletproof():
    """Ensure deep coverage logic records zero damage when one of the defender's
    abilities is Bulletproof (even if another ability would yield non-zero damage).
    """
    # Setup attacker with a single damaging move (Shadow Ball)
    attacker = {
        "pokemon_id": 25,
        "base_stats": {"hp": 35, "attack": 55, "defense": 40,
                       "special-attack": 50, "special-defense": 50, "speed": 90},
        "evs": {"hp": 0, "attack": 0, "defense": 0,
                "special-attack": 252, "special-defense": 0, "speed": 252},
        "nature": "timid",
        "ability": "static",
        "item": None,
    }
    attacker = build_actor_from_payload(attacker)

    # Defender: Kommo-o (ID 784) with bulletproof + another ability
    all_pokemon = load_json("all_pokemon.json")
    kommo = all_pokemon.get("kommo-o")
    assert kommo, "Kommo-o data missing"

    defender_base = {
        "pokemon_id": 784,
        "base_stats": kommo["base_stats"],
        "evs": {"hp": 252, "attack": 0, "defense": 4,
                "special-attack": 0, "special-defense": 0, "speed": 252},
        "nature": "bold",
        # ability will be set dynamically for each iteration
        "item": None,
    }

    move = {"name": "shadow-ball", "type": "ghost", "power": 80,
            "damage_class": "special"}

    # Copy of map for abilities
    abilities_map = load_json("all_pokemon_abilities.json")
    defender_abilities = abilities_map.get(str(784), []) or [None]
    # Ensure bulletproof is among them for sanity
    assert "bulletproof" in defender_abilities

    # simulate deep logic: for each ability/status compute KO% and track worst
    worst_ko = float('inf')
    worst_info = None
    for ability in defender_abilities:
        for status in ['normal', 'burn', 'poison']:
            payload = {
                **defender_base,
                "ability": ability,
                "status": status,
                "types": kommo.get("types", []),
                "name": "kommo-o",
            }
            defender = build_actor_from_payload(payload)
            res = calculate_damage(move, attacker, defender, field={}, gen=9)
            dmg_all = res.get("damage_all", [])
            hp = res.get("defender_hp", defender.get("hp", 1))
            ko_count = sum(1 for d in dmg_all if d >= hp)
            ko_percent = (ko_count / len(dmg_all) * 100) if dmg_all else 0
            dmin = min(dmg_all) if dmg_all else 0
            # update worst
            if ko_percent < worst_ko or (ko_percent == worst_ko and dmin < (worst_info or {}).get("damage_min", float('inf'))):
                worst_ko = ko_percent
                worst_info = {"damage_min": dmin, "ko": ko_percent, "ability": ability, "status": status}

    # Expect worst case from bulletproof, i.e. damage_min == 0, ko == 0
    assert worst_info is not None
    assert worst_info["ability"] == "bulletproof"
    assert worst_info["damage_min"] == 0
    assert worst_info["ko"] == 0
