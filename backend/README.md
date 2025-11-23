# Backend — PokeTools

This document explains how to run and develop the backend (Flask) of PokeTools.

Prerequisites
- Python 3.10+ (3.11 recommended)

Setup (Windows PowerShell)
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run (development)
```powershell
# Run Flask app directly (debug mode)
python .\api.py

# Or use gunicorn for production-like run
pip install gunicorn
gunicorn api:app
```

Tests
```powershell
# From `backend/` with the virtualenv active
python -m pytest -q

# Run a single test file
python -m pytest -q test/test_calcs.py

# Run a single test function inside a file
python -m pytest -q test/test_calcs.py::test_case_1

# If you prefer to run each test script directly (useful for verbose output):
ForEach ($f in (Get-ChildItem -Path test -Filter 'test_*.py' | Select-Object -ExpandProperty Name)) {
  Write-Host "\n=== Running $f ===" -ForegroundColor Cyan
  & ".\.venv\Scripts\python.exe" "test\$f"
}

# Notes
- Tests expect the dataset files from the repository root `data/` (the test files were updated to read from `../data/`).
- I also replaced boolean `return` statements in the test suite with `assert` so pytest will not emit `PytestReturnNotNoneWarning` warnings.
```

Data
- JSON files are in `../data/` and loaded by the backend at startup.
- Import scripts live in `backend/importation/` and can be used to regenerate or update data files.

Notes for developers
- Key modules:
  - `calculate_damages/` — damage calculation core
  - `calculate_statistics/` — stat computation
  - `api.py` — routes and SSE streaming endpoints
- SSE endpoints: `find_threats_stream` and `analyze_coverage_stream` emit `text/event-stream` events with `data: <JSON>` lines. See `api.py` and frontend SSE handling.

Field conditions
- **Auras (Fairy Aura / Dark Aura / Aura Break)**: Implemented in `calculate_damages/special_conditions.py` and applied as base-power modifiers so rounding and authoritative 16-roll damage distributions match expected results. Unit tests covering aura combinations live in `backend/test/`.
- **Screens (Reflect / Light Screen) and Aurora Veil**: Implemented as final-stage damage modifiers (chain of fixed-point modifiers) so they affect the final chained rounding. Key behavior:
  - Reflect halves physical damage in single battles; in multi-battle modes (e.g., `battle_mode: "double"`) it uses a ~2/3 multiplier (Gen V uses `2703/4096`; Gen VI+ uses `2732/4096`).
  - Light Screen is analogous for special damage.
  - Aurora Veil acts like both screens but does not reduce damage from critical hits or fixed-damage moves; Aurora Veil is only effective while `hail` or `snow` (front-end or battle logic must enforce turn/set conditions).
  - Attacker with the `Infiltrator` ability ignores screens.
  - Certain moves (`brick-break`, `defog`, `psychic-fangs`, `raging-bull`) remove screens when they hit a non-immune target; the helper `remove_screens_on_move()` performs this mutation on the `field` dict.
  - A `Screen Cleaner` ability should call `handle_screen_cleaner_on_switch()` when a Pokémon switches in to clear screens.

These helpers live in `calculate_damages/special_conditions.py` and are exercised by the tests in `backend/test/test_screens_and_aurora.py`.

If you add or update datasets, ensure `data/` files remain JSON-valid and include required keys used by the calculators (types, base_stats, moves, abilities).
