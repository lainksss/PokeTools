# Moves With Special Handling (backend)

This document lists moves that have explicit special-case handling in the backend code (`calculate_damages.py`, `calculate_weather.py`, `calculate_terrain.py`, etc.). For each move we provide file references and a short description of the behavior.

## Detected special-case moves

- **Weather Ball**
  - File: `backend/calculate_damages/calculate_damages.py`
  - Location: special-case block for Weather Ball (around the normalized name detection)
  - Behavior: when the move name is recognized as Weather Ball, the code treats it as a special-case: `damage_class` is forced to `special`, and if weather is active (and not neutralized by Cloud Nine / Air Lock) the move's base power is doubled and its type is set according to the weather (sun → Fire, rain → Water, hail/snow → Ice, sandstorm → Rock, fog → Normal). The `move` dict is updated (`move['type']`, `move['power']`).
  - Test: ❌ No unit test found that exercises Weather Ball specifically (weather logic is tested generally).

- **Hydro-Steam**
  - File: `backend/calculate_damages/calculate_weather.py`
  - Location: special handling in the sun/rain branches
  - Behavior: `hydro-steam` is treated specially during sunny weather: the sun boost applies to it as if it were Fire (it receives the sun boost and is exempted from the usual Water penalty in sun).
  - Test: ❌ Not directly tested by the current unit tests.

- **Body Press**
  - File: `backend/calculate_damages/calculate_damages.py`
  - Location: physical-category branch (stat selection)
  - Behavior: `body-press` uses the attacker's Defense stat as the attacking stat (A = Defense) instead of Attack.
  - Test: ❌ No direct unit test found for `body-press`.

- **Tera Blast**
  - File: `backend/calculate_damages/calculate_damages.py`
  - Location: Tera Blast / Stellar handling
  - Behavior: if the attacker is terastallized, `tera-blast` takes the attacker's `tera_type`. The move category (physical or special) is chosen by comparing the attacker's Attack vs. Sp. Atk using stat stages only. There is a special `stellar` case which fixes power to 100 and changes effectiveness for terastallized targets.
  - Test: ✅ Partial — terastallize behavior is exercised in the unit tests (`is_terastallized` and `tera_type` appear in tests), but `tera-blast` itself is not explicitly exercised.

- **Freeze-Dry**
  - File: `backend/calculate_damages/calculate_damages.py`
  - Location: after type effectiveness calculation
  - Behavior: `freeze-dry` is treated as super-effective against Water types (ensuring an effectiveness of at least 2.0 against Water).
  - Test: ❌ Not directly tested.

- **Flying Press**
  - File: `backend/calculate_damages/calculate_damages.py`
  - Location: after type effectiveness calculation
  - Behavior: `flying-press` is treated as applying both Fighting and Flying effectiveness (effectively combining type multipliers to emulate a dual-type move for effectiveness purposes).
  - Test: ❌ Not directly tested.

- **Earthquake / Bulldoze / Magnitude**
  - File: `backend/calculate_damages/calculate_damages.py` (terrain interaction)
  - Location: Grassy Terrain handling
  - Behavior: when `compute_terrain_multiplier` indicates `halve_power` (e.g., Grassy Terrain), these moves' base power is halved (BP modifier). The code explicitly mentions `Earthquake`, `Bulldoze`, and `Magnitude`.
  - Test: ⚠️ Indirect — Grassy Terrain is covered by unit tests (`test_ivysaur_tyranitar.py` and `test_calcs.py`), but the halving for these specific moves is not explicitly asserted.

- **Facade**
  - File: `backend/calculate_damages/calculate_damages.py`
  - Location: burn multiplier computation
  - Behavior: normally physical moves have their power halved when the attacker is burned, but `facade` is exempt from this reduction for Gen >= 6 (the code checks `if not (gen >= 6 and move.get('name') == 'facade')`).
  - Test: ❌ Not directly tested.

- **Always-critical moves**
  - File: `backend/calculate_damages/calculate_damages.py`
  - Location: `determine_crit_effective` logic
  - Behavior: a set of moves are forced to critically hit: `storm-throw`, `frost-breath`, `zippy-zap`, `surging-strikes`, `wicked-blow`, `flower-trick`. The code checks `if move.get('name') in always_crit or move.get('always_crit')`.
  - Test: ❌ Not directly tested in this test suite.

## General notes

- Some rules are implemented generically and apply to classes of moves rather than a single move (for example, Misty Terrain reducing damage from certain Dragon moves, multi-target move handling, STAB/Tera logic, etc.).
- Other moves can be indirectly affected by abilities/items/terrain (for example, `air-balloon` in `items/items.py` interacts with grounding logic, while `muscle-band`/`choice-band` affect power via `apply_item_stat_modifiers`).
