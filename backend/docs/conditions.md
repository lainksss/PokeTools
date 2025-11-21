**Conditions Summary**

This document summarizes the environmental and global conditions implemented in the damage calculation pipeline, where they are handled in the code, the flags/effects they produce, and notable interactions (items, abilities, moves).

**Weather**
- **Files**: `backend/calculate_damages/calculate_weather.py`, used from `calculate_damages.py`.
- **Field key**: `weather` (string). Neutralized by `cloud_nine` / `air_lock` or abilities `cloud-nine` / `air-lock` present on any `field['pokemon']`.
- **Handled weather types**: `harsh-sunlight` (strong sun), `sun`/`sunny-day`, `rain`, `sandstorm`, `hail` (and `snow`).
- **Effects / returned flags** (from `compute_weather_mult`):
  - `prevent_freeze`: strong sun prevents freeze.
  - `sandstorm_spdef_boost`: sandstorm causes the Rock-type special-defense boost behavior (used to indicate sandstorm defensive effect).
  - `hail_end_of_turn_damage`: hail (or Gen-dependent snow/hail handling) indicates end-of-turn damage for non-Ice types.
  - `snow_def_boost`: snow increases Ice-type Defense (flag to indicate this defensive boost).
  - `name`: canonical weather name placed into effects for downstream logic.
- **Power multipliers**: `compute_weather_mult` returns a multiplier (1.5 / 0.5) for moves of types affected by the weather (e.g. Fire boosted in sun, Water boosted in rain). Some moves receive special treatment (e.g. `hydro-steam` is Fire-boosted in sun per code).

Test coverage: ✅ Weather handling for `sun`, `rain`, `sandstorm` and `snow/hail` is exercised in unit tests (see `backend/test/test_calcs.py`, `backend/test/test_kyogre_simple.py`, `backend/test/test_raichu_ninetales.py`). Specific moves like `weather-ball` or `hydro-steam` are not explicitly unit-tested, but the weather multipliers are validated by tests.

**Terrain**
- **Files**: `backend/calculate_damages/calculate_terrain.py`, used from `calculate_damages.py`.
- **Field key**: `terrain` (string). Neutralized by `gravity` in the field (gravity sets `terrain = None` in `compute_terrain_multiplier`).
- **Handled terrain types**: `electric`, `grassy`, `misty`, `psychic`.
- **Effects / returned flags** (from `compute_terrain_multiplier`):
  - `terrain_heal_fraction` (e.g. 1/16 for Grassy Terrain): indicates per-turn healing for grounded Pokémon.
  - `halve_power`: used when Grassy Terrain halves the power of specific moves (Earthquake, Bulldoze, Magnitude).
  - `halve_dragon`: Misty Terrain halves Dragon-type damage against grounded defenders.
  - `prevent_status`: Misty Terrain prevents status conditions (flagging that effect).
  - `name`: canonical terrain name placed into effects for downstream logic.
- **Power multipliers**: attacker-grounded and move-type specific boosts (e.g. Electric/Psychic/Grass moves get 1.3 when user is grounded in their terrain per implemented Gen logic).

Test coverage: ✅ Grassy and Misty terrain are used in unit tests (`backend/test/test_ivysaur_tyranitar.py`, `backend/test/test_garchomp_golem.py`, `backend/test/test_calcs.py`), including grassy healing/boost behavior. Some per-move halving (e.g., Earthquake under Grassy Terrain) is not explicitly asserted but the terrain logic itself is tested.

**Grounding / Gravity / Ungrounding**
- **Files**: `backend/calculate_damages/calculate_grounded.py` (function `is_grounded`), consulted by terrain/weather logic and damage pipeline.
- **Field key**: `gravity` (boolean) — when true, all Pokémon are forced grounded.
- **Per-pokemon keys used**: `types` (list), `ability`, `item`, `magnet_rise` (flag), `telekinesis` (flag), `smack_down`, `ingrain`, `air_balloon_popped`.
- **Ungrounding conditions (return False)**:
  - Pokémon has `flying` in `types`.
  - Pokémon ability is `levitate`.
  - Pokémon holds item `air-balloon` (and `air_balloon_popped` is not set).
  - Pokémon has `magnet_rise` or `telekinesis` set.
- **Grounding conditions (return True)**:
  - Field `gravity` is active (overrides ungrounding).
  - Pokémon has `smack_down` or `ingrain` set.
  - Otherwise, default is grounded.
- **Interactions**: grounding affects whether terrain bonuses/heals and Misty Terrain's dragon-halving apply; grounded checks are consulted by `compute_terrain_multiplier` and elsewhere.

Test coverage: ✅ Grounding logic is covered by `backend/test/test_grounded.py` (Levitate, Air Balloon popped/unpopped, Gravity overrides).

**Tera / Terastallize related**
- **Files**: many call-site points: `backend/api.py` (payload keys), `calculate_damages.py` checks, `calculate_abilities.py` (tera-shell handling), and move special-cases (e.g. `tera-blast`).
- **Per-pokemon keys**: `is_terastallized` (boolean), `tera_type` (string).
- **Behaviors implemented in code**:
  - If attacker `is_terastallized` and `move` is `tera-blast`, `tera-blast` takes `tera_type` as its type and may change category (physical/special) depending on stat stages; there is a special `stellar` handling in the code.
  - `tera-shell` (ability) is noted: when a Pokémon with `tera-shell` is at full HP, code sets `effects['tera_shell_active'] = True` for special interactions (see `calculate_abilities.py` and `api.py`).

  Test coverage: ✅ Terastallize flags (`is_terastallized`, `tera_type`) are used in unit tests (`backend/test/test_calcs.py`, `backend/test/test_kyogre_simple.py`). Some Tera-specific moves (e.g., `tera-blast`) are not directly exercised but tera-related type changes are validated in the tests.

**Items & Abilities that affect global/field logic**
- **Items**:
  - `air-balloon`: makes holder ungrounded until popped (checked in `is_grounded` by `item == 'air-balloon' and not pokemon.get('air_balloon_popped')`).
  - `iron-ball`: appears in items logic and may affect weighting/grounding in other interactions (see `backend/items/items.py`).

Test coverage: ✅ `air-balloon` interactions are tested in `backend/test/test_grounded.py` (popped vs not popped). `iron-ball` is present in items code but not directly exercised by unit tests in this suite.
- **Abilities**:
  - `cloud-nine` / `air-lock`: neutralize weather if present on any Pokémon (checked by `compute_weather_mult`).
  - `levitate`: makes the Pokémon ungrounded (checked in `is_grounded`).
  - `multiscale`, `shadow-shield`, `tera-shell`: abilities that rely on full-HP checks; `api.py` and `calculate_abilities.py` mark these cases for `calculate_damages` to consider.
  - Many other battle-affecting abilities are processed in `calculate_abilities.py` (Huge Power, Tough Claws, Sheer Force, Scrappy, Pixilate/Aerilate/Galvanize/Refrigerate, etc.). Abilities typically return multipliers/effects used by the damage pipeline.

**Move-specific / pipeline interactions**
- Some moves are adjusted because of the field conditions or special logic in `calculate_damages.py`:
  - **Weather Ball** (Ball'Météo): code inspects normalized move names and doubles power / sets type according to current weather (see `calculate_damages.py`).
  - **Hydro-Steam**: special behavior in sun (treated akin to Fire-boosted in sun in weather logic).
  - **Tera Blast**: changes type (to `tera_type`) while terastallized and may change category based on stat stages.
  - **Earthquake / Bulldoze / Magnitude**: power halved under Grassy Terrain (`effects['halve_power']`) in `compute_terrain_multiplier`.

  Test coverage: ⚠️ Grassy Terrain is tested, but the explicit halving for `Earthquake`/`Bulldoze`/`Magnitude` is not directly asserted by current tests.
  - **Misty Terrain**: halves Dragon damage to grounded defenders (`effects['halve_dragon']`) and prevents status (`prevent_status`).

**Field / Pipeline keys used across modules**
- `field` is a Dict passed around; commonly consulted keys include:
  - `weather`, `terrain`, `gravity`, `cloud_nine`, `air_lock`, and `pokemon` (list of per-pokemon dicts used for cross-checks such as cloud-nine abilities).
- Per-Pokémon keys consulted by routines include (non-exhaustive):
  - `types`, `ability`, `item`, `smack_down`, `ingrain`, `magnet_rise`, `telekinesis`, `air_balloon_popped`, `is_terastallized`, `tera_type`, `is_grounded` (sometimes precomputed), stat stages/EVs/nature keys required by stat comparisons.

**Where to look in code**
- Weather logic: `backend/calculate_damages/calculate_weather.py` (function `compute_weather_mult`).
- Terrain logic: `backend/calculate_damages/calculate_terrain.py` (function `compute_terrain_multiplier`).
- Grounding: `backend/calculate_damages/calculate_grounded.py` (function `is_grounded`).
- Ability-based field effects & full-HP checks: `backend/calculate_damages/calculate_abilities.py` and `backend/api.py` (payload preparation and full-HP ability list checks).
- Damage pipeline & move special-cases: `backend/calculate_damages/calculate_damages.py` (search for Ball'Météo / `tera-blast` / `body-press` / `freeze-dry` / `flying-press` blocks).
