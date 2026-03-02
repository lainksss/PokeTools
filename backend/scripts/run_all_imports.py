"""Run all importation scripts in a sensible order.

This helper executes the scripts in `backend/importation/` and a few
supporting scripts in `backend/scripts/` in an order that respects common
dependencies (types -> moves -> pokemon -> derived maps).

Usage:
	python run_all_imports.py          # run all scripts, stop on first failure
	python run_all_imports.py --continue  # run all, continue on errors
	python run_all_imports.py --dry-run   # print the execution order only

The script uses the current Python interpreter (`sys.executable`) to run
each import script so it works correctly inside virtual environments.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List


ROOT = Path(__file__).resolve().parents[1]  # backend/
IMPORT_DIR = ROOT / "importation"
SCRIPTS_DIR = ROOT / "scripts"


DEFAULT_ORDER: List[Path] = [
	IMPORT_DIR / "import_all_types.py",
	IMPORT_DIR / "import_all_natures.py",
	IMPORT_DIR / "import_all_translated_talents.py",
	IMPORT_DIR / "import_all_attacks.py",
	IMPORT_DIR / "import_all_translated_moves.py",
	IMPORT_DIR / "import_all_pokemon.py",
	IMPORT_DIR / "import_all_pokemon_names.py",
	IMPORT_DIR / "import_all_pokemon_moves.py",
	IMPORT_DIR / "import_all_pokemon_abilities.py",
	IMPORT_DIR / "import_all_pokemon_weight.py",
	IMPORT_DIR / "import_all_moves_on_weight.py",
	IMPORT_DIR / "import_all_evolutions.py",
]

# Additional utility scripts to run after imports (optional)
POST_SCRIPTS: List[Path] = [
	SCRIPTS_DIR / "import_all_move_flags.py",
	SCRIPTS_DIR / "validate_mega_moves.py",
]


def find_existing(paths: List[Path]) -> List[Path]:
	return [p for p in paths if p.exists()]


def run_script(path: Path) -> int:
	print(f"\n=== Running: {path.relative_to(ROOT.parent)} ===")
	try:
		res = subprocess.run([sys.executable, str(path)], check=False)
		print(f"Exit code: {res.returncode}")
		return res.returncode
	except Exception as e:
		print(f"Execution failed for {path}: {e}")
		return 1


def main(argv: List[str] | None = None) -> int:
	import argparse

	argv = list(argv or sys.argv[1:])
	parser = argparse.ArgumentParser(description="Run backend importation scripts in order")
	parser.add_argument("--continue", dest="cont", action="store_true", help="continue on error")
	parser.add_argument("--dry-run", dest="dry", action="store_true", help="print execution plan only")
	args = parser.parse_args(argv)

	order = find_existing(DEFAULT_ORDER)
	post = find_existing(POST_SCRIPTS)

	if args.dry:
		print("Planned execution order:")
		for p in order:
			print(" -", p)
		if post:
			print("Post scripts:")
			for p in post:
				print(" -", p)
		return 0

	# Run import scripts
	for p in order:
		code = run_script(p)
		if code != 0:
			print(f"Script failed: {p} (code {code})")
			if not args.cont:
				print("Stopping due to failure. Re-run with --continue to skip failures.")
				return code

	# Run post-processing scripts
	for p in post:
		code = run_script(p)
		if code != 0:
			print(f"Post-script failed: {p} (code {code})")
			if not args.cont:
				return code

	print("\nAll scripts executed.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

