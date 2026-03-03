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
	- Test: ❌

- `tera-shell`: when at full HP, sets `effects['tera_shell_active'] = True` (used by `calculate_damages` to adjust type effectiveness).
	- Test: ❌

- `multiscale`: when at full HP, halves incoming damage (other_mult *= 0.5).
	- Test: ❌

- `shadow-shield`: similar to Multiscale; reduces damage to 0.5 when at full HP.
	- Test: ❌

- `thick-fat`: halves damage from Fire and Ice types.
	- Test: ❌

- `scrappy`: ignores Ghost immunities for Normal/Fighting moves (handled in damage calculations).
	- Test: ❌

- `merciless`: forces critical hits when the target is poisoned (handled in crit logic).
	- Test: ❌

- `battle-armor` / `shell-armor`: prevent critical hits (handled in crit logic).
	- Test: ❌

Note: `sniper` and other crit-related flags are set by ability handling and used in the main damage calculation to modify the critical multiplier.
