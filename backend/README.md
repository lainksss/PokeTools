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

  Field conditions (auras)
  - **Fairy Aura / Dark Aura / Aura Break**: These three auras were implemented as field-level conditions (in `calculate_damages/special_conditions.py`) and are applied as base-power modifiers so rounding and authoritative 16-roll damage distributions match expected results. Unit tests covering aura combinations live in `backend/test/test_auras.py`.

If you add or update datasets, ensure `data/` files remain JSON-valid and include required keys used by the calculators (types, base_stats, moves, abilities).
