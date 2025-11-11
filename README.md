# PokeTools — Complete Documentation (English)

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

### API Endpoints (detailed list)
All endpoints are prefixed with `/api`.

#### GET /api/health
- Simple health-check
- Response: `{ ok: True, service: "PokeTools-backend" }`

#### GET /api/pokemon
- Returns Pokémon list: `{ count, results: [{id, name, types, base_stats}, ...] }`

#### GET /api/pokemon/<id>
- Pokémon details by ID: `{ id, name, types, base_stats }`

#### GET /api/pokemon/<id>/moves
- List of moves (limited details) for the Pokémon: `{ pokemon_id, count, moves: [{name, type, power, accuracy, damage_class}, ...] }`

#### GET /api/pokemon/<id>/abilities
- Returns abilities for the Pokémon: `{ pokemon_id, count, abilities: [...] }`

#### GET /api/types
- Simple type list: `{ count, types: ["fire","water",...] }`

#### GET /api/pokemon-names
- Returns `all_pokemon_names_multilang.json` (multi-language mapping)

#### GET /api/natures
- List of natures and their effects: `{ count, natures: [{name, increase, decrease}, ...] }`

#### POST /api/calc_stats
- Payload (JSON): `{ base_stats: {hp, attack, defense, special-attack, ...}, evs?: {...}, nature?: "adamant" }`
- Response: `{ stats: {hp, attack, defense, special_attack, special_defense, speed} }`

#### POST /api/calc_damage
- Payload (JSON):
  ```json
  {
    "attacker": { ...actor-payload... },
    "defender": { ...actor-payload... },
    "move": { "name"?: string, "type"?: string, "power"?: int, "damage_class"?: string },
    "field"?: { "weather", "terrain", "battle_mode", ... },
    "defender_hp"?: int,
    "is_critical"?: bool,
    "random_range"?: [min,max],
    "gen"?: int,
    "debug"?: bool
  }
  ```
- Behavior: enriches `move` from `all_moves.json` if `name` is provided, builds `attacker` and `defender` via `build_actor_from_payload`, calls `calculate_damage(...)` and returns the raw result (typically includes `damage_all`, `damage_min`, `damage_max`, `defender_hp`, etc.).

#### POST /api/find_threats
- Synchronous (non-stream) version — analyzes all Pokémon and returns those that can KO the defender with various variants (EVs/natures).
- Payload: `{ defender: <actor-payload>, ko_mode?: "OHKO"|"2HKO", field?: {...} }`
- Response: `{ defender_hp, ko_mode, threat_count, threats: [{attacker_name, attacker_id, variant, move_name, move_power, damage_min, damage_max, ko_percent, guaranteed_ko, other_moves_count}, ...] }`

#### POST /api/find_threats_stream
- Streaming (SSE) version, recommended for long analyses.
- Payload: same as `find_threats`.
- SSE events (prefix `data: JSON\n\n`):
  - type: "init" → `{ type: 'init', total, defender_hp }`
  - type: "progress" → `{ type: 'progress', processed, total, threats_found }`
  - type: "threat" → `{ type: 'threat', data: <threat_entry> }`
  - type: "complete" → `{ type: 'complete', total_threats, total_processed }`
  - type: "error" → `{ type: 'error', message }`

#### POST /api/analyze_coverage_stream
- Analyzes offensive coverage for an attacker (multiple moves) and streams results.
- Payload:
  ```json
  {
    "attacker": <actor-payload>,
    "moves": [ {name|partial move data}, ... ],
    "ko_mode"?: "OHKO"|"2HKO",
    "include_no_ko"?: bool,
    "bulk_mode"?: "none"|"custom"|"max",
    "custom_evs"?: int,
    "field"?: {...}
  }
  ```
- SSE events:
  - init/progress/coverage/complete/error
  - coverage entries: `{ defender_name, defender_id, defender_types, defender_hp, best_move_name, best_move_type, max_ko_chance, max_rolls_that_ko, damage_range }`

#### POST /api/analyze_type_coverage
- Non-streaming: finds Pokémon NOT hit super effectively by the provided moves.
- Payload: `{ attacker: {is_terastallized, tera_type, ...}, moves: [{name}, ...] }`
- Response: `{ not_super_effective: [ {pokemon_id, pokemon_name, types, best_effectiveness, best_move, best_move_type}, ... ], total_pokemon, not_covered, move_types_used }`

### Streaming Endpoints — Notes
- Streaming endpoints return `text/event-stream` and emit lines in SSE format `data: <JSON>\n\n`.
- On the frontend, use `new EventSource(url)` or a fetch+readable stream implementation to read data.
- JSON events include a `type` field (init/progress/threat/coverage/complete/error) for real-time progress/results.

### Key Mechanics & Rules
- Terastallization: when a Pokémon is terastallized and a `tera_type` is provided, the backend treats its defensive types as only `tera_type`; `orig_types` is kept for correct STAB calculation.
- Natures: `all_natures.json` is used to determine nature effects. Stat names are normalized (e.g. `special-attack` → `special_attack`) and multipliers (1.1/0.9) are applied.
- Abilities & edge cases: for `2HKO` mode, the backend tries to handle abilities that activate at full HP (e.g. Multiscale) by recalculating the second hit without the effect if needed.
- Tera Blast: detected by move name `tera-blast` — if the attacker is terastallized, the move takes the `tera_type` as its type.
- Simplifications: some calculations use approximations (e.g. KO% estimation based on rolls) — see code for details.

## Frontend — Details

### Stack & Structure
- React 18 with Vite
- `src/App.jsx`: main shell, navigation (uses `NavLink` for active nav bar)
- `src/pages/`: main pages — `Calculate`, `Threats`, `Coverage`, `TypeCoverage`, `Home`
- `src/components/`: panels and reusable widgets
- Global styles: `src/styles.css`
- i18n: `src/i18n/LanguageContext.jsx` with `translations.js` (FR/EN)

### Expected Behavior
- The frontend consumes REST endpoints for lists/details (Pokémon, moves, natures).
- For heavy analyses (coverage/threats), the frontend opens an SSE connection (`EventSource`) to `/api/find_threats_stream` or `/api/analyze_coverage_stream` and processes `init/progress/threat/coverage/complete/error` messages for real-time progress/results.

## API Request Examples

### 1) Example `calc_stats` (PowerShell curl)
```powershell
curl -Method POST -Uri http://127.0.0.1:5000/api/calc_stats -Headers @{"Content-Type"="application/json"} -Body (
  (@{
    base_stats = @{ hp= 70; attack= 90; defense=70; "special-attack"= 60; "special-defense"= 70; speed= 80 }
    evs = @{ hp= 0; attack=252; defense=0; "special-attack"=0; "special-defense"=0; speed= 0 }
    nature = 'adamant'
  } | ConvertTo-Json -Depth 5)
)
```
- Expected response: `{ "stats": { ... } }`

### 2) Example `calc_damage`
```powershell
curl -Method POST -Uri http://127.0.0.1:5000/api/calc_damage -Headers @{"Content-Type"="application/json"} -Body (
  (@{
    attacker = @{ pokemon_id=1; base_stats=@{ attack=100; "special-attack"=50 }; evs=@{}; nature='adamant'; types=['fire'] }
    defender = @{ pokemon_id=2; base_stats=@{ defense=90; "special-defense"=80 }; evs=@{}; nature='calm'; types=['water'] }
    move = @{ name = 'flamethrower' }
  } | ConvertTo-Json -Depth 6)
)
```
- Response: JSON from `calculate_damage` (typically `damage_all`, `damage_min`, `damage_max`, `defender_hp`, ...)

### 3) Example SSE (Threats) in browser (JS)
```javascript
const evt = new EventSource('http://127.0.0.1:5000/api/find_threats_stream');
evt.onmessage = (e) => {
  try {
    const payload = JSON.parse(e.data);
    switch(payload.type) {
      case 'init': /* show total */ break;
      case 'progress': /* update progress bar */ break;
      case 'threat': /* show intermediate threat */ break;
      case 'complete': /* finish */ break;
      case 'error': /* show error */ break;
    }
  } catch (err) { console.error(err); }
}
// Note: in our React frontend, we sometimes use fetch + ReadableStream for more control.
```

## How to Run (dev)

### Backend (Windows PowerShell)
1. Create a virtual environment and install dependencies
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
2. Start the API
```powershell
# direct launch (api.py contains Flask runner)
python .\api.py
# Options: override host/port
$env:API_HOST = '127.0.0.1'; $env:API_PORT = '5000'; python .\api.py
```
- The backend listens on 0.0.0.0:5000 by default (debug=True). CORS is enabled for local frontend access.

### Frontend
```powershell
cd frontend
npm install
npm run dev
```
- Vite starts a dev server (default http://localhost:5173). The frontend is configured to call the backend API (check config if needed).

## Developer Notes / Debug
- If endpoints are missing or you get 500 errors, check the backend console (the runner prints logs and debug info for the first Pokémon in streaming analyses).
- The calculation modules (`calculate_damages`, `calculate_statistics`) are the core logic: modifying these requires sanity tests (unit consistency, stat naming, key normalization). Pay attention to stat names (`special-attack` vs `special_attack`).
- Streaming endpoints use approximations for KO% — for perfect accuracy, see how `damage_all` is computed in `calculate_damage` and prefer full distributions.

## Contact & Credits
The project is maintained by me (Alexandro 'Lainkss').

---
