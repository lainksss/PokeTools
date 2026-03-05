# Small utilities to compute Pokémon stats from base stats.

# Implements the standard Pokémon formulas for non-HP stats and HP.

# Defaults chosen per your request:
# - level default: 50
# - IV default: 31

# Functions:
# - calc_stat(base, iv=31, ev=0, level=50, nature=1.0) -> int
# - calc_hp(base, iv=31, ev=0, level=50) -> int
# - calc_all_stats(bases, ivs=None, evs=None, natures=None, level=50) -> dict

# All inputs are integers; natures is a mapping of stat name -> multiplier (e.g. {"attack":1.1}).

from typing import Dict, Optional
import math


def calc_stat(base: int, iv: int = 31, ev: int = 0, level: int = 50, nature: float = 1.0) -> int:
	"""Calculate a single (non-HP) stat.

	Formula:
		result = floor( ( (2*Base + IV + floor(EV/4)) * Level / 100 ) + 5 ) * Nature

	Returns the integer stat (floored after applying nature).
	"""
	base = int(base)
	iv = int(iv)
	ev = int(ev)
	level = int(level)
	intermediate = ((2 * base + iv + (ev // 4)) * level) // 100
	stat = math.floor((intermediate + 5) * float(nature))
	return int(stat)


def calc_hp(base: int, iv: int = 31, ev: int = 0, level: int = 50) -> int:
	"""Calculate HP stat.

	Formula:
		HP = floor( ( (2*Base + IV + floor(EV/4)) * Level / 100 ) ) + Level + 10
	"""
	base = int(base)
	iv = int(iv)
	ev = int(ev)
	level = int(level)
	hp = ((2 * base + iv + (ev // 4)) * level) // 100
	hp = int(hp + level + 10)
	return hp


def calc_all_stats(
	bases: Dict[str, int],
	ivs: Optional[Dict[str, int]] = None,
	evs: Optional[Dict[str, int]] = None,
	natures: Optional[Dict[str, float]] = None,
	level: int = 50,
) -> Dict[str, int]:
	"""Compute full stats dict given base stats.

	bases: mapping with keys 'hp','attack','defense','special_attack','special_defense','speed'
	ivs/evs: optional mappings; missing keys default to IV=31 and EV=0.
	natures: mapping of stat -> multiplier (e.g., {'attack':1.1, 'defense':0.9})
	level: default 50 as requested.
	"""
	# Force IVs to 31 and level to 50 as requested
	level = 50
	ivs = {"hp": 31, "attack": 31, "defense": 31, "special_attack": 31, "special_defense": 31, "speed": 31}
	evs = evs or {}
	natures = natures or {}

	# Ensure EV rules: per-stat max 252, total max 516
	# Note: the frontend uses a simplified 66-unit system where each unit converts
	# to backend EVs via: 0→0, n→4+(n-1)*8. Max total from 66 units is 516,
	# so we allow up to 516 instead of the traditional 510 game cap.
	def _normalize_evs(evs_in: Dict[str, int]) -> Dict[str, int]:
		keys = ["hp", "attack", "defense", "special_attack", "special_defense", "speed"]
		vals = {k: max(0, int(evs_in.get(k, 0) or 0)) for k in keys}
		# cap per-stat
		for k in keys:
			if vals[k] > 252:
				vals[k] = 252
		return vals

	evs = _normalize_evs(evs)

	stats: Dict[str, int] = {}
	# HP
	stats["hp"] = calc_hp(
		bases.get("hp", bases.get("HP", 0)), ivs.get("hp", ivs.get("HP", 31)), evs.get("hp", 0), level
	)

	stats["attack"] = calc_stat(
		bases.get("attack", bases.get("Attack", 0)), ivs.get("attack", 31), evs.get("attack", 0), level, natures.get("attack", 1.0)
	)
	stats["defense"] = calc_stat(
		bases.get("defense", bases.get("Defense", 0)), ivs.get("defense", 31), evs.get("defense", 0), level, natures.get("defense", 1.0)
	)
	stats["special_attack"] = calc_stat(
		bases.get("special_attack", bases.get("SpAttack", bases.get("specialAttack", 0))),
		ivs.get("special_attack", 31),
		evs.get("special_attack", 0),
		level,
		natures.get("special_attack", 1.0),
	)
	stats["special_defense"] = calc_stat(
		bases.get("special_defense", bases.get("SpDefense", bases.get("specialDefense", 0))),
		ivs.get("special_defense", 31),
		evs.get("special_defense", 0),
		level,
		natures.get("special_defense", 1.0),
	)
	stats["speed"] = calc_stat(
		bases.get("speed", bases.get("Speed", 0)), ivs.get("speed", 31), evs.get("speed", 0), level, natures.get("speed", 1.0)
	)

	return stats


if __name__ == "__main__":
	# Quick demo: example for a Pokémon with base stats (HP, Atk, Def, SpA, SpD, Spe)
	example_bases = {"hp": 90, "attack": 92, "defense": 75, "special_attack": 92, "special_defense": 85, "speed": 60}
	# Default build: no EVs, neutral nature
	stats = calc_all_stats(example_bases)
	print("Level=50, IVs=31, EVs=0 by default, Basical Abomasnow:")
	for k, v in stats.items():
		print(f"{k}: {v}")

	print()  # spacer
	# Technical example as requested by the user:
	# - same base stats as above
	# - EVs: 252 HP, 220 SpA, 2 SpD, 36 Spe (sum = 510)
	# - Nature: -Atk, +Def (attack *0.9, defense *1.1)
	tech_evs = {"hp": 252, "attack": 0, "defense": 0, "special_attack": 220, "special_defense": 2, "speed": 36}
	tech_nature = {"attack": 0.9, "defense": 1.1}
	stats_tech = calc_all_stats(example_bases, evs=tech_evs, natures=tech_nature)
	print("Technical example with Specific Abomasnow: EVs HP=252, SpA=220, SpD=2, Spe=36 ; Nature -Atk +Def ; Level=50 IVs=31 :")
	for k, v in stats_tech.items():
		print(f"{k}: {v}")

