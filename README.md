# [PokeTools](https://lainksss.github.io/PokeTools/) — Complete Documentation

This README provides a detailed overview of the PokeTools codebase: backend (Flask), frontend (React + Vite), data files, all HTTP/SSE API endpoints, request/response formats, and how to run the project locally.

---

## Table of Contents
- Quick Overview
- Repository Structure
- Backend
  - Main Modules
  - Data Loading
  - Actor Construction (attacker/defender)
  - API Endpoints (detailed list)
  - Streaming Endpoints (SSE) — Event Formats
  - Key Mechanics (Terastallization, STAB, natures, abilities)
- Frontend
  - Structure & Main Components
  - i18n
  - Available Pages
- API Request Examples
  - `curl` / EventSource (SSE)
- How to Run (dev)
  - Backend (Windows PowerShell)
  - Frontend (Vite)
- Developer Notes & Debugging
- Suggested Improvements

---

## Quick Overview

## Deployment

### Frontend (GitHub Pages)
- The React (Vite) frontend is automatically deployed to GitHub Pages using a GitHub Actions workflow.
- The `frontend/` folder contains the source code, and the build output (`dist/`) is published to the `gh-pages` branch.
- The workflow `.github/workflows/deploy.yml` builds and deploys the app on every push to `main`.
- The app is available at: https://lainksss.github.io/PokeTools/

### Backend (Render)
- The Flask backend is deployed as a web service on [Render](https://dashboard.render.com/).
- The `backend/` folder contains the source code and `requirements.txt`.
- The Render start command is: `gunicorn api:app`
- CORS is configured to allow requests from the GitHub Pages frontend and localhost.
PokeTools is a suite of tools for competitive Pokémon: damage calculator, threat analysis, offensive coverage, and type coverage. The backend is Python (Flask) exposing REST and SSE endpoints for long-running analyses. The frontend is a React (Vite) app consuming these endpoints.

## Repository Structure

- `backend/`
  - `api.py`: main Flask entrypoint. Loads data, exposes endpoints, assembles payloads, and includes SSE endpoints.
  - `requirements.txt`: Python dependencies.
  - `calculate_damages/`: damage, type, weather, ability, tera logic.
  - `calculate_statistics/`: computes final stats from base/EVs/nature.
  - `importation/`: utility scripts for importing raw data (JSONs already provided in `data/`).

- `data/`: JSON files used by the backend: `all_pokemon.json`, `all_moves.json`, `all_types.json`, `all_pokemon_moves.json`, `all_pokemon_abilities.json`, `all_natures.json`, `all_pokemon_names_multilang.json`.

- `frontend/`: React + Vite app
  - `index.html`, `package.json`, `vite.config.js`
  - `src/`: React code
    - `App.jsx`: main shell, header/nav
    - `pages/Calculate.jsx`, `Threats.jsx`, `Coverage.jsx`, `TypeCoverage.jsx`, `Home.jsx`
    - `components/`: MiddlePanel, PokemonPanel, ResultsPanel, etc.
    - `i18n/LanguageContext.jsx`, `translations.js`: simple i18n
    - `styles.css`: global styles

    - `pages/SpeedGame.jsx`: mini-games pour la vitesse — la page s'appelle **Trouve la vitesse** et propose deux mini-jeux :
      - `Duel de Vitesse` : devinez quel Pokémon a la vitesse finale la plus élevée (comportement existant),
      - `Juste prix (vitesse)` : devinez la vitesse de base d'un Pokémon; l'interface donne uniquement « Trop haut » / « Trop bas » jusqu'à la bonne réponse, puis révèle la valeur.

  Frontend EVs note:
  - The frontend UI uses a compact EV unit system to simplify inputs: each stat accepts 0..32 units and the total across all stats is capped at 66 units. This is a frontend convenience layer; before sending API requests the frontend converts these units to the traditional EV values expected by the backend (0..~252 scale) using the formula `0 -> 0`, `n (1..32) -> 4 + (n-1)*8`.
  - The backend API still expects standard EV values (0..252-ish), so the conversion is performed client-side and the backend remains unchanged.

## Backend — Details

### Main Modules
- `api.py`: exposes all endpoints (see below) and includes a utility `build_actor_from_payload()` to transform frontend payloads into the internal structure expected by calculators.
- `calculate_statistics/calc_all_stats`: computes final stats (HP, Attack, Defense, SpA, SpD, Speed) from base_stats, EVs, and nature effects.
- `calculate_damages/calculate_damage`: main damage simulation function. Returns detailed objects including `damage_all`, `damage_min`, `damage_max`, `defender_hp`, etc.

### Data Loading
- The backend loads JSON files from `data/` via `_load_json(filename)` (with in-memory cache). Key files:
  - `all_pokemon.json`: dict by slug {id, types, base_stats, ...}
  - `all_moves.json`: dict of moves (power, type, damage_class, accuracy...)
  - `all_pokemon_moves.json`: mapping {pokemon_id: [move_slugs...]}
  - `all_pokemon_abilities.json`: mapping {pokemon_id: [ability_slugs...]}
  - `all_natures.json`: mapping of natures -> increase/decrease
  - `all_pokemon_names_multilang.json`: translated names

### Actor Construction (attacker/defender)
- `build_actor_from_payload(p)`:
  - Normalizes `base_stats` (e.g. `special-attack` → `special_attack`).
  - Interprets `nature` (if present) to apply 1.1/0.9 multipliers to affected stats.
  - Computes final stats via `calc_all_stats(bases_normalized, evs, natures_map)`.
  - Handles terastallization: if `is_terastallized` and `tera_type` present, defensive types become only `tera_type` (original types kept in `orig_types` for STAB).

### Move Transformations & Special Cases
The backend includes a handful of hard‑coded move transformations and special behaviours. The canonical list is maintained in `backend/docs/moves_with_special_handling.md`.

- **Iron Head → Behemoth Blade/Bash**: when the attacker species contains `zacian-crowned` or `zamazenta-crowned`, any move named `iron-head` is rewritten to the corresponding Behemoth move. This happens both in the core `calculate_damage()` function and in the routing layers (`threats.py`, `coverage.py`) where moves are normalised prior to invoking the calculator. The transformation sets the move’s name, type and power (100) so coverage/threats analysis, which may receive move slugs from generic lists, behaves identically to the main damage calculator UI.

Refer to the “Moves With Special Handling” doc for more details.


### API Endpoints (detailed list)
All endpoints are prefixed with `/api`.

## Tests

Quick instructions to run backend tests (Windows PowerShell):

```powershell
cd backend
python -m venv .venv            # if not already created
.\.venv\Scripts\Activate.ps1  # activate the virtualenv
pip install -r requirements.txt
python -m pytest -q             # run the full test suite
```

- To run a single test file: `python -m pytest -q test/test_calcs.py`.
- To run a single test function: `python -m pytest -q test/test_calcs.py::test_case_1`.

Notes:
- The backend tests read JSON datasets from the repository `data/` folder (tests were adjusted to load data from the repo root).
- Tests in the suite were updated to use `assert` instead of returning boolean values to avoid pytest warnings.
See `backend/README.md` for more detailed commands and PowerShell snippets.

