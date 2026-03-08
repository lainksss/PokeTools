# Implemented Abilities

Note: the list below enumerates abilities that have special handling in the backend. Moves are listed separately in the moves documentation.

(Descriptions sourced from `calculate_abilities.py` and `calculate_damages.py` code.)

Note: move-level boolean flags (contact / punch / bite, etc.) are loaded
from `data/moves_with_flags.json` by `calculate_abilities.apply_ability_effects` at
runtime. The API layer no longer duplicates this enrichment — ability handlers
consume those flags directly.

Quick summary (implementation style):

- Base-power modifications (mutate `move["power"]`): `technician`, `strong-jaw`, `tough-claws`, `aerilate`/`pixilate`/`refrigerate`/`galvanize`/`normalize`, `reckless`.
- Final multipliers (applied to `other_mult`): `sheer-force`, `iron-fist`, and other simple multipliers remain as final modifiers.

Note: the `recoil` attribute is not universally present in `moves_with_flags.json`; some tests set `move["recoil"] = True` manually. If you want automatic detection of recoil moves, we can extend `backend/scripts/import_all_move_flags.py` to include a `recoil` flag based on move meta from PokeAPI.

- `huge-power` / `pure-power`: doubles the user's Attack for physical moves.
	- Test: ✅ `huge-power` is covered by `backend/test/test_huge_power.py` (Azumarill Aqua Jet case).

- `tough-claws`: +30% for moves that make contact.
	- Implementation: applied as a base-power modification (the ability mutates `move["power"] = int(p * 1.3)`) so rounding and 16-roll damage distributions match authoritative calculators.
	- Test: ✅ `tough-claws` is covered by `backend/test/test_tough_claws.py` (Perrserker Metal Claw case).

- `sheer-force`: +30% for moves with secondary effects (with secondary effects suppressed).
	- Implementation: applied as a base-power modification (the ability mutates `move["power"] = int(p * 1.3)`) so rounding and 16-roll damage distributions match authoritative calculators. When a move has no explicit power the code falls back to applying a final multiplier (`other_mult *= 1.3`). Detection: Sheer Force only activates when the move explicitly has `move['has_secondary'] is True` or when the precomputed file `data/moves_secondary_effect.json` contains `"has_secondary": true` for that move (regenerate with `backend/importation/import_all_moves_secondary_effects.py`). When applied the code also sets `move["secondary_suppressed"] = True` so other pipeline stages can skip flinch/status/stat secondary effects.
	- Test: ✅ `sheer-force` is covered by `backend/test/test_sheer_force.py` (Landorus Bite & Earthquake cases).

- `reckless`: +20% for moves with recoil.
	- Implementation: applied as a base-power modification (the ability mutates `move["power"] = int(p * 1.2)`) so rounding and 16-roll damage distributions match authoritative calculators. Tests may set `move["recoil"] = True` when recoil isn't present in `moves_with_flags.json`.
	- Test: ✅ `reckless` is covered by `backend/test/test_reckless.py` (Staraptor Double Edge case).

- `iron-fist`: +20% for punching moves.
	- Implementation: currently applied as a final multiplier (`other_mult *= 1.2`).
	- Test: ✅ `iron-fist` is covered by `backend/test/test_iron_fist.py` (Golurk Shadow Punch case).

- `strong-jaw`: +50% for biting moves.
	- Implementation: applied as a base-power modification (the ability mutates `move["power"] = int(p * 1.5)`) so rounding and 16-roll damage distributions match authoritative calculators.
	- Test: ✅ `strong-jaw` is covered by `backend/test/test_strong_jaw.py` (Bruxish Psychic Fangs case).

- `technician`: multiplies power by 1.5 for moves with base power <= 60.
	- Implementation: applied as a base-power modification (mutates `move["power"]`) to preserve expected rounding.
	- Test: ✅ `technician` is covered by `backend/test/test_technician.py` (Scizor Bullet Punch case).

- `sniper`: marks increased critical damage (handled as larger crit multiplier when applicable).
	- Test: ❌ But useless

- `guts`: +50% Attack if the user has a status condition and uses a physical move.
	- Test: ✅ totally implemented in its test `test_guts_facade.py` 

- `solar-power`: +50% Special Attack in harsh sunlight for special moves.
	- Test: ✅ Unit tests reference `solar-power` in `backend/test/test_calcs.py`.

- `hadron-engine`: +33% (factor 5461/4096) Special Attack in Electric Terrain for special moves. Signature ability of Miraidon.
	- Implementation: checks if the user has the ability, terrain is Electric/Electric-Terrain, and move is special. When all conditions are met, the Special Attack stat is multiplied by 5461/4096 using `pokeRound()` for precise rounding.
	- Test: ✅ `hadron-engine` covered by `backend/test/test_hadron_engine.py` (Volt Switch & Draco Meteor cases with/without Electric Terrain).

- `orichalcum-pulse`: +33% (factor 5461/4096) Attack in harsh sunlight for physical moves. Signature ability of Koraidon. Boost applies even with Utility Umbrella active.
	- Implementation: checks if the user has the ability, weather is harsh sunlight (sun/harsh-sunshine/harsh-sunlight/desolate-land), and move is physical. When all conditions are met, the Attack stat is multiplied by 5461/4096 using `pokeRound()` for precise rounding.
	- Test: ✅ `orichalcum-pulse` covered by `backend/test/test_orichalcum_pulse.py` (Close Combat & Fire Punch cases with/without harsh sunlight and ability).

- `protosynthesis`: boosts the user's highest non-HP stat by +30% (or +50% for Speed stat) in harsh sunlight or while holding Booster Energy. Signature ability of Flutter Mane. 
	- Implementation: determines the highest non-HP stat using stage multipliers (positive stage: 1.0 + min(stage×0.5, 4.0), negative stage: 1.0 + min(|stage|×0.33, 2.0)). Applies priority tie-breaker: attack > defense > special_attack > special_defense > speed. Boosts the corresponding attacking stat (Attack for physical moves, Special Attack for special moves) by +30% or +50% for Speed using `pokeRound()` for precise rounding. Activation requires harsh sunlight or Booster Energy (weather takes priority if both present). Boost only applies to the applicable stat for the move category.
	- Test: ✅ `protosynthesis` covered by `backend/test/test_protosynthesis.py` (5 tests: Dazzling Gleam/Shadow Ball with/without harsh sunlight, multi-target move reduction verified).

- `quark-drive`: boosts the user's highest non-HP stat by +30% (or +50% for Speed stat) in Electric Terrain or while holding Booster Energy. Signature ability of Iron Bundle. Also boosts the defender's Defense or Special Defense (if either is the highest stat) by +30% to reduce incoming damage.
	- Implementation: **Attacker-side**: determines the highest non-HP stat using stage multipliers (positive stage: 1.0 + min(stage×0.5, 4.0), negative stage: 1.0 + min(|stage|×0.33, 2.0)). Applies priority tie-breaker: attack > defense > special_attack > special_defense > speed. Boosts the corresponding attacking stat (Attack for physical moves, Special Attack for special moves) by +30% or +50% for Speed using `pokeRound()` for precise rounding. Activation requires Electric Terrain or Booster Energy (terrain takes priority if both present). **Defender-side**: applies identical stat detection logic to the defender. When Defense or Special Defense is the highest stat, boosts the corresponding defensive stat by +30% to reduce incoming damage. Both attacker and defender boosts apply independently; in battles with Electric Terrain, both can activate simultaneously, potentially offsetting each other's effects.
	- Test: ✅ `quark-drive` covered by `backend/test/test_quark_drive.py` (5 tests: Icy Wind/Volt Switch with Electric Terrain demonstrating attacker boost, Spark with terrain + defender boost showing mutual cancellation, baseline tests without terrain).

- `aerilate` / `pixilate` / `refrigerate` / `galvanize` / `normalize`: convert Normal moves to another type and apply ~20% boost (e.g., Aerilate turns Normal → Flying).
	- Implementation: these are applied as base-power modifications (they mutate `move["type"]` and `move["power"]`) so type-effectiveness and STAB are recalculated using the mutated move and rounding matches tests.
	- Test: ✅ `abilities` covered in `backend/test/test_aerilate_family.py`.

- `protean` / `libero`: change the user's type to the move's type (marked in effects for later logic).
	- Test: ✅ `protean`/`libero` covered by `backend/test/test_protean_libero.py` (Cinderace / Greninja cases).

- `blaze` / `torrent` / `overgrow` / `swarm`: 1.5x boost for the respective type when HP <= 1/3.
	- Test: ❌

- `steelworker` / `steely-spirit`: +50% for Steel-type moves.
	- Implementation: applied as a base-power modification (the ability mutates `move["power"] = int(p * 1.5)`) so rounding and 16-roll damage distributions match authoritative calculators. If a move has no explicit power the code falls back to applying a final multiplier (`other_mult *= 1.5`).
	- Test: ✅ `steelworker`/`steely-spirit` covered by `backend/test/test_steel_abilities.py` (Dialga Flash Cannon case).

- `victory-star`: implemented as a precision/accuracy flag (placeholder-like handling).
	- Test: ❌ But useless

- `levitate`: immunity to Ground-type moves (treated as type multiplier = 0.0 where applicable).
	- Test: ✅ `levitate` is tested in `backend/test/test_grounded.py` (ungrounded behavior and gravity override).

- `water-absorb` / `volt-absorb` / `dry-skin`: absorb Water/Electric/Water respectively (negates damage and marks absorption effects).

	- Behavior: when hit by the corresponding type these abilities make the holder immune (damage negated) and signal activation. `water-absorb` / `dry-skin` also restore HP (implemented as a 25% max-HP heal reported in the damage result when `max_hp` is provided). `volt-absorb` behaves similarly for Electric moves.
	- Test: ✅ `water-absorb` / `volt-absorb` / `dry-skin` covered by `backend/test/test_absorb_abilities.py` (zero damage + heal/activation checks).

- `flash-fire`: absorbs Fire moves (negates/hides damage and signals activation).
	- Behavior: grants immunity to Fire moves and signals activation via `effects['flash_fire_activated'] = True`. No automatic HP restore.
	- Test: ✅ covered by `backend/test/test_absorb_abilities.py` (zero damage + activation check).

- `lightning-rod`: absorbs Electric moves (negates damage and signals activation).
	- Behavior: when hit by an Electric move the holder is immune and `effects['lightning_rod_activated'] = True` is set; no automatic HP restore.
	- Test: ✅ covered by `backend/test/test_absorb_abilities.py` (zero damage + activation check).

- `storm-drain`: absorbs Water moves (negates damage and signals activation).
	- Behavior: when hit by a Water move the holder is immune and `effects['storm_drain_activated'] = True` is set; no automatic HP restore in current implementation (activation flagged for consumers).
	- Test: ✅ covered by `backend/test/test_absorb_abilities.py` (zero damage + activation check).

- `earth-eater`: absorbs Ground moves and heals the holder instead of taking damage.
	- Behavior: when hit by a Ground move the holder is immune and regains HP (implemented as a 25% max-HP heal reported in the damage result when `max_hp` is provided).
	- Test: ✅ covered by `backend/test/test_absorb_abilities.py` (zero damage + heal check).

- `solid-rock` / `filter` / `prism-armor`: reduce super-effective damage by ~25%.
	- Implementation: applied as a final multiplier (`other_mult *= 0.75`) when the move is super-effective (type_mult > 1.0). All three abilities have identical mechanics.
	- Test: ✅ `solid-rock`/`filter`/`prism-armor` covered by `backend/test/test_solid_rock_filter.py` (flamethrower vs grass type with ability reduction).

- `tera-shell`: when at full HP, halves incoming damage (other_mult *= 0.5). Only active when the defender is at full HP.
	- Implementation: checks `defender['hp'] >= defender['max_hp']` and applies 0.5× multiplier to other_mult if true.
	- Test: ✅ `tera-shell` covered by `backend/test/test_tera_shell.py` (damage reduction at full/partial HP).

- `sap-sipper`: grants immunity to Grass-type moves.
	- Behavior: when hit by a Grass move the holder is immune (damage negated) and `effects['sap_sipper_activated'] = True` is set.
	- Test: ✅ `sap-sipper` covered by `backend/test/test_sap_sipper.py` (zero damage + activation).

- `bulletproof`: grants immunity to ball/bomb moves (moves with the `"ballistics"` flag).
	- Behavior: when hit by a ballistics move the holder is immune (damage negated) and `effects['bulletproof_activated'] = True` is set.
	- Implementation: move flags are loaded from `data/moves_with_flags.json` at runtime; detection checks for `"ballistics"` in the move's flag list.
	- Test: ✅ `bulletproof` covered by `backend/test/test_bulletproof.py` (blocks ball/bomb moves like Seed Bomb, allows normal moves).

- `motor-drive`: grants immunity to Electric-type moves.
	- Behavior: when hit by an Electric move the holder is immune (damage negated) and `effects['motor_drive_activated'] = True` is set.
	- Test: ✅ `motor-drive` covered by `backend/test/test_motor_drive.py` (zero damage + activation).

- `soundproof` / `cacophony`: grant immunity to sound-based moves (moves with the `"sound"` flag).
	- Behavior: when hit by a sound move the holder is immune (damage negated) and activation is flagged (e.g., `effects['soundproof_activated'] = True` or `effects['cacophony_activated'] = True`).
	- Implementation: move flags are loaded from `data/moves_with_flags.json` at runtime; detection checks for `"sound"` in the move's flag list.
	- Test: ✅ `soundproof`/`cacophony` covered by `backend/test/test_soundproof.py` (blocks sound moves, dual ability support).

- `wind-rider`: grants immunity to wind-based moves.
	- Behavior: when hit by a wind move the holder is immune (damage negated) and `effects['wind_rider_activated'] = True` is set.
	- Implementation: moves are detected by hardcoded name list: `{"razor-wind", "whirlwind", "tailwind", "icy-wind", "silver-wind", "ominous-wind", "fairy-wind"}`. This approach accommodates moves not yet flagged in `moves_with_flags.json`.
	- Test: ✅ `wind-rider` covered by `backend/test/test_wind_rider.py` (blocks wind moves, allows normal moves).

- `wonder-guard`: blocks all non-super-effective moves.
	- Behavior: only moves with type effectiveness > 1.0 (super-effective) deal damage; all neutral/non-effective moves are blocked (damage set to 0.0).
	- Implementation: implemented as a flag-based check in `calculate_damages.py` (lines ~820–827) after type multipliers are computed. The handler returns `effects['wonder_guard_enabled'] = True`, and the main pipeline checks `type_mult <= 1.0` to nullify damage.
	- Notes: this ability requires special post-computation handling because it depends on the final `type_mult` value, which is computed after `apply_ability_effects()` returns. Shedinja's Wonder Guard is particularly important in competitive play.
	- Test: ✅ `wonder-guard` covered by `backend/test/test_wonder_guard.py` (blocks non-super-effective moves, allows super-effective).

- `sturdy`: grants immunity to KO at full HP; guarantees survival at 1 HP if damage would otherwise cause KO.
	- Behavior: when the holder is at full HP and takes damage that would normally result in KO (remaining HP ≤ 0), the damage is capped so that the holder survives at exactly 1 HP. If the holder is not at full HP, Sturdy provides no protection.
	- Implementation: implemented as a post-damage-calculation check in `calculate_damages.py` (lines ~957–968). After damage rolls are computed, if the defender has Sturdy and `current_hp == max_hp`, all damage values are capped at `max_hp - 1` and remaining HP is recalculated.
	- Notes: Sturdy only activates when the Pokemon is at full HP; partial damage negates the ability's protection. This matches official Pokémon mechanics (e.g., generation 5+).
	- Test: ✅ `sturdy` covered by `backend/test/test_sturdy.py` (survives KO at full HP, no protection when damaged).

- `multiscale`: when at full HP, halves incoming damage (other_mult *= 0.5). Signature ability of Dragonite.
	- Implementation: checks `defender['hp'] >= defender['max_hp']` and applies 0.5× multiplier to other_mult if true.
	- Test: ✅ `multiscale` covered by `backend/test/test_multiscale.py` (Solar Beam / Ice Beam with 50% reduction at full HP).

- `shadow-shield`: similar to Multiscale; reduces damage to 0.5 when at full HP. Signature ability of Necrozma.
	- Implementation: identical to Multiscale; checks full HP and applies 0.5× multiplier.
	- Test: ✅ `shadow-shield` covered by `backend/test/test_shadow_shield.py` (Ice Beam / Solar Blade with 50% reduction at full HP).

- `thick-fat`: halves damage from Fire and Ice types (other_mult *= 0.5 when move type is fire or ice).
	- Implementation: checks `move['type'] in ('fire', 'ice')` and applies 0.5× multiplier to other_mult if true.
	- Test: ✅ `thick-fat` covered by `backend/test/test_thick_fat.py` (Ice Beam / Flamethrower with 50% reduction, baseline comparison).

- `scrappy` / `minds-eye`: ignores Ghost immunities for Normal/Fighting moves (handled in damage calculations).
	- Test: ❌

- `merciless`: forces critical hits when the target is poisoned.
	- Implementation: checks `defender['status'] == 'poisoned'` and forces critical hit (returns `effects['merciless_crit'] = True`).
	- Test: ✅ `merciless` covered by `backend/test/test_merciless.py` (Solar Beam with poison status forcing crits vs normal non-crit).

- `battle-armor` / `shell-armor`: prevent critical hits (blocks critical hit calculation).
	- Implementation: checks if defender has this ability and sets `is_critical = False` if a critical would have been triggered. Note: cannot block crits forced by ability effects like Merciless.
	- Test: ✅ `battle-armor`/`shell-armor` covered by `backend/test/test_battle_armor.py` (demonstrates that Merciless-forced crits cannot be blocked).

- `intrepid-sword` / `dauntless-shield`
	- Transformation behaviour for `iron-head` → `behemoth-blade`/`bash` is documented in `backend/docs/moves_with_special_handling.md`.
	- Test: ✅ `intrepid-sword` / `dauntless-shield` covered by `backend/test/test_zamazenta_zacian.py`.

Note: `sniper` and other crit-related flags are set by ability handling and used in the main damage calculation to modify the critical multiplier.

## Test Coverage Summary

**Recently Tested (25 tests, ✅):**
- Damage reduction abilities: `multiscale`, `shadow-shield`, `thick-fat`, `tera-shell`, `solid-rock`, `filter`, `prism-armor`
- Critical mechanics: `merciless`, `battle-armor`, `shell-armor`
- Stat-boosting abilities: `hadron-engine`, `orichalcum-pulse`, `protosynthesis`, `quark-drive` (Flutter Mane, Iron Bundle; multi-target move mechanics validated; defender-side stat boosts for Quark Drive)

**Other Fully Tested (✅):**
- Power modifiers: `huge-power`, `sheer-force`, `tough-claws`, `strong-jaw`, `technician`, `iron-fist`, `reckless`, `steelworker`, `steely-spirit`
- Type conversions: `aerilate`, `pixilate`, `refrigerate`, `galvanize`, `normalize`
- Type immunity/absorption: `water-absorb`, `volt-absorb`, `dry-skin`, `flash-fire`, `lightning-rod`, `storm-drain`, `earth-eater`, `sap-sipper`, `bulletproof`, `motor-drive`, `soundproof`, `cacophony`, `wind-rider`
- Special mechanics: `levitate`, `protean`, `libero`, `wonder-guard`, `sturdy`, `solar-power`, `guts`, `hadron-engine`, `orichalcum-pulse`

**Not Yet Tested (❌):**
- Type boost at low HP: `blaze`, `torrent`, `overgrow`, `swarm`
- Other: `victory-star`

**Legendaries/important abilities (with full damage calculations)**
- Ogerpon (each of them)
- Chien pao / Ting Lu / Yu-yu / Chong jian
- marvel-scale
