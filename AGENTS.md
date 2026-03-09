# Agents — API Documentation for Autonomous Tools

> **Agents.md** : Complete reference for any autonomous system, bot, or external tool interacting with the PokeTools API.

---

## Table of Contents

1. [API Base & CORS](#api-base--cors)
2. [Data Importation & Management](#data-importation--management)
3. [Endpoints Reference](#endpoints-reference)
   - [Health Check](#health-check)
   - [Data Endpoints](#data-endpoints)
   - [Calculation Endpoints](#calculation-endpoints)
4. [Data Structures](#data-structures)
5. [Payload Examples](#payload-examples)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)

---

## API Base & CORS

**Base URL** (Development)
```
http://localhost:5000
```

**Base URL** (Production)
```
https://lainksss.github.io/PokeTools/api  [via backend service]
```

**CORS Allowed Origins**
```
https://lainksss.github.io
https://lainksss.github.io/PokeTools
http://localhost:5173  (dev frontend)
```

All requests use standard HTTP/JSON. No authentication required.

---

## Data Importation & Management

### Overview

The PokeTools project includes a comprehensive data pipeline for importing and validating Pokémon data. All data is loaded from JSON files in the `data/` directory and exposed via the API.

### Data Files

| File | Purpose | Source |
|------|---------|--------|
| `all_pokemon.json` | Pokémon metadata (base stats, types, IDs) | PokéAPI, custom imports |
| `all_pokemon_moves.json` | Move lists per Pokémon (learnable moves) | PokéAPI |
| `all_pokemon_abilities.json` | Ability mappings per Pokémon | PokéAPI |
| `all_moves.json` | Move definitions (power, accuracy, category, etc.) | PokéAPI |
| `all_types.json` | Type matchups (super-effective, weaknesses) | PokéAPI |
| `all_natures.json` | Nature stat modifiers | PokéAPI |
| `all_items.json` | Item effects and descriptions | PokéAPI |
| `pokemon_evolution.json` | Evolution chains and conditions | PokéAPI |
| `moves_secondary_effect.json` | Secondary effects on moves (paralysis, burn, etc.) | Custom |
| `all_pokemon_weight_height.json` | Weight/height data for custom calcs | PokéAPI |

### Data Importation Scripts

All data import scripts are located in `backend/importation/`. They fetch from external sources (PokéAPI, custom databases) and generate the JSON files above.

**Key Importation Files:**
- `import_all_pokemon.py` — Import base Pokémon stats and metadata
- `import_all_types.py` — Import type matchups
- `import_all_moves.py` / `import_all_attacks.py` — Import move data
- `import_all_pokemon_abilities.py` — Import ability data
- `import_all_pokemon_moves.py` — Assign moves to Pokémon
- `import_all_natures.py` — Import nature multipliers
- `import_all_translated_moves.py` — Import translated move names
- `import_all_pokemon_names.py` — Import translated Pokémon names

### Mega Evolution Move Handling

*New feature:* when a Pokémon is given a `mega-gem` or `primal-gem` the frontend automatically switches it to its strongest Mega/Primal form (appending `-mega` or `-primal` to the slug) and the backend mirrors this behaviour so calculations use the correct base stats. Removing the gem will revert the species to its base form. This mirrors the existing logic for Zacian/Zamazenta crowned forms with rusted items.


**Important:** Mega-evolution forms must inherit moves from their base forms to function correctly in the damage calculator.

#### Validation & Auto-merge Script

**File:** `backend/scripts/validate_mega_moves.py`

This script validates that all mega-evolution Pokémon have move lists. If a mega form is missing moves, it automatically merges them from the base form.

**Usage:**

```bash
# Dry-run (show what would be changed)
python backend/scripts/validate_mega_moves.py

# Apply merge (copy base moves into mega forms)
python backend/scripts/validate_mega_moves.py --merge-mega

# Apply with custom options
python backend/scripts/validate_mega_moves.py --merge-mega --no-backup
```

**Options:**
- `--merge-mega` — Merge base Pokémon moves into their mega counterparts (alias for `--apply`)
- `--apply` — Same as `--merge-mega`
- `--no-backup` — Skip backup creation when applying
- `--dry-run` — Show what would be changed (default if no `--apply`)

**Output:**
- Console: Progress log with summary
- JSON Report: `logs/validate_mega_moves.json` — Detailed report of changes

**Example Report:**
```json
{
  "timestamp": "2025-12-17T19:35:56Z",
  "checked": 96,
  "written": 91,
  "fails": 5,
  "changes": [
    {
      "slug": "charizard-mega-x",
      "mega_id": 10034,
      "base_slug": "charizard",
      "base_id": 6,
      "added": 48
    }
  ]
}
```

### Master Runner Script

**File:** `backend/importation/run_all.py`

This is the master script that executes all data importation and validation scripts in the correct order, with proper logging and error handling.

**Usage:**

```bash
# Run all imports and scripts
python backend/importation/run_all.py

# Run with increased timeout (in seconds)
python backend/importation/run_all.py --timeout 1200

# Stop on first error
python backend/importation/run_all.py --stop-on-error
```

**Options:**
- `--timeout <seconds>` — Per-script timeout (default: 900 seconds / 15 minutes)
- `--stop-on-error` — Exit immediately on first non-zero exit code

**Execution Order:**

The runner executes scripts in two phases:

**Phase 1: Importation (Defined Order)**
1. `import_all_types.py`
2. `import_all_natures.py`
3. `import_all_attacks.py`
4. `import_all_moves_secondary_effects.py`
5. `import_all_moves_on_weight.py`
6. `import_all_translated_moves.py`
7. `import_all_translated_talents.py`
8. `import_all_pokemon_moves.py`
9. `import_all_pokemon_abilities.py`
10. `import_all_pokemon_names.py`
11. `import_all_pokemon_weight.py`
12. `import_all_pokemon.py`
13. `import_all_evolutions.py`

**Phase 2: Validation Scripts (Alphabetical)**
- All `.py` files from `backend/scripts/`

**Features:**
- Automatic UTF-8 encoding for child processes
- Stdout/stderr capture for each script
- JSON report generation: `logs/run_all_imports.log`
- Configurable per-script timeout (useful for large imports)
- Keyboard interrupt handling (Ctrl+C)

**Output:**
- Console: Progress with timestamps and exit codes
- Log File: `logs/run_all_imports.log` — Full transcript with DEBUG level details

### Example Run

```bash
# Navigate to project root
cd D:\- ECOLE OU CODE\Code\pokemon_calculator

# Activate Python environment
.\.venv\Scripts\Activate.ps1

# Run all imports
python backend/importation/run_all.py

# Expected output:
# [2025-12-17 20:35:56] [INFO    ] Script started
# [2025-12-17 20:35:56] [INFO    ] Repository root: D:\- ECOLE OU CODE\Code\pokemon_calculator
# [2025-12-17 20:35:56] [INFO    ] ================================================================================
# [2025-12-17 20:35:56] [INFO    ] Starting import sequence
# [2025-12-17 20:35:56] [INFO    ] Phase 1: Executing importation files in defined order...
# [2025-12-17 20:35:56] [INFO    ] [1/13] import_all_types.py
# [2025-12-17 20:35:36] [INFO    ] ✓ Success: import_all_types.py
# ... (more scripts)
# [2025-12-17 20:55:00] [INFO    ] Phase 3: Executing scripts from scripts...
# [2025-12-17 20:55:01] [INFO    ] ✓ Success: import_all_move_flags.py
# [2025-12-17 20:55:02] [INFO    ] ✓ Success: validate_mega_moves.py
# [2025-12-17 20:55:02] [INFO    ] Completed successfully.
```

---

## Endpoints Reference

### Health Check

#### `GET /api/health`

Simple health check to verify the API is running.

**Response:**
```json
{
  "ok": true,
  "service": "PokeTools-backend"
}
```

**Status Codes:** `200 OK`

---

### Data Endpoints

#### 1. `GET /api/pokemon`

Returns complete list of all Pokémon with base stats.

**Query Parameters:** None

**Response:**
```json
{
  "count": 1025,
  "results": [
    {
      "id": 1,
      "name": "bulbasaur",
      "types": ["grass", "poison"],
      "base_stats": {
        "hp": 45,
        "attack": 49,
        "defense": 49,
        "special-attack": 65,
        "special-defense": 65,
        "speed": 45
      },
      "can_evolve": true
    },
    {
      "id": 2,
      "name": "ivysaur",
      "types": ["grass", "poison"],
      "base_stats": { ... },
      "can_evolve": true
    }
    // ... more Pokémon
  ]
}
```

**Status Codes:** `200 OK`

---

#### 2. `GET /api/pokemon/<pokemon_id>`

Get details for a single Pokémon by numeric ID.

**Path Parameters:**
- `pokemon_id` (int): Pokémon national dex ID

**Response:**
```json
{
  "id": 25,
  "name": "pikachu",
  "types": ["electric"],
  "base_stats": {
    "hp": 35,
    "attack": 55,
    "defense": 40,
    "special-attack": 50,
    "special-defense": 50,
    "speed": 90
  }
}
```

**Status Codes:** `200 OK`, `404 Not Found`

---

#### 3. `GET /api/pokemon/<pokemon_id>/moves`

Get all moves a Pokémon can learn by ID.

**Path Parameters:**
- `pokemon_id` (int): Pokémon national dex ID

**Response:**
```json
{
  "pokemon_id": 25,
  "name": "pikachu",
  "move_count": 87,
  "moves": [
    {
      "name": "thunderbolt",
      "type": "electric",
      "power": 90,
      "accuracy": 100,
      "pp": 15,
      "category": "special",
      "priority": 0
    },
    {
      "name": "quick-attack",
      "type": "normal",
      "power": 40,
      "accuracy": 100,
      "pp": 30,
      "category": "physical",
      "priority": 1
    }
    // ... more moves
  ]
}
```

**Status Codes:** `200 OK`, `404 Not Found`

---

#### 4. `GET /api/pokemon/<pokemon_id>/abilities`

Get all abilities for a Pokémon by ID.

**Path Parameters:**
- `pokemon_id` (int): Pokémon national dex ID

**Response:**
```json
{
  "pokemon_id": 25,
  "name": "pikachu",
  "abilities": [
    {
      "name": "static",
      "description": "Contact with the Pokémon may cause paralysis.",
      "is_hidden": false
    },
    {
      "name": "lightning-rod",
      "description": "Raises Sp. Atk if hit by an Electric move. Electric moves are drawn to this Pokémon.",
      "is_hidden": false
    },
    {
      "name": "surge-surfer",
      "description": "Boosts Speed if Electric Terrain is active.",
      "is_hidden": true
    }
  ]
}
```

**Status Codes:** `200 OK`, `404 Not Found`

---

#### 5. `GET /api/types`

Get all types and their effectiveness (type matchups).

**Query Parameters:** None

**Response:**
```json
{
  "count": 18,
  "types": [
    {
      "name": "normal",
      "super_effective_against": ["ghost"],
      "weak_to": ["fighting"],
      "resists": [],
      "immune_to": []
    },
    {
      "name": "fire",
      "super_effective_against": ["grass", "ice", "bug", "steel"],
      "weak_to": ["water", "ground", "rock"],
      "resists": ["grass", "ice", "bug", "steel", "fairy"],
      "immune_to": []
    },
    // ... all 18 types
  ]
}
```

**Status Codes:** `200 OK`

---

#### 6. `GET /api/natures`

Get all natures and their stat multipliers.

**Query Parameters:** None

**Response:**
```json
{
  "count": 25,
  "natures": [
    {
      "name": "adamant",
      "increase": "attack",
      "decrease": "special-attack",
      "multipliers": {
        "attack": 1.1,
        "special-attack": 0.9
      }
    },
    {
      "name": "bold",
      "increase": "defense",
      "decrease": "attack",
      "multipliers": {
        "defense": 1.1,
        "attack": 0.9
      }
    },
    // ... all 25 natures
  ]
}
```

**Status Codes:** `200 OK`

---

### Calculation Endpoints

#### 1. `POST /api/calc_stats`

Calculate final stats for a Pokémon given base stats, EVs, IVs, and nature.

**Request Body:**
```json
{
  "pokemon_id": 25,
  "base_stats": {
    "hp": 35,
    "attack": 55,
    "defense": 40,
    "special-attack": 50,
    "special-defense": 50,
    "speed": 90
  },
  "evs": {
    "hp": 0,
    "attack": 0,
    "defense": 0,
    "special-attack": 252,
    "special-defense": 0,
    "speed": 252
  },
  "ivs": {
    "hp": 31,
    "attack": 31,
    "defense": 31,
    "special-attack": 31,
    "special-defense": 31,
    "speed": 31
  },
  "nature": "timid",
  "level": 50
}
```

**Response:**
```json
{
  "level": 50,
  "nature": "timid",
  "base_stats": { ... },
  "ivs": { ... },
  "evs": { ... },
  "final_stats": {
    "hp": 105,
    "attack": 75,
    "defense": 70,
    "special-attack": 97,
    "special-defense": 80,
    "speed": 124
  }
}
```

**Status Codes:** `200 OK`, `400 Bad Request`, `500 Internal Server Error`

---

#### 2. `POST /api/calc_damage`

Calculate damage from a move hit (normal or critical), including roll damage.

**Request Body:**
```json
{
  "attacker": {
    "pokemon_id": 25,
    "base_stats": { ... },
    "evs": { ... },
    "nature": "timid",
    "ability": "static",
    "item": null,
    "is_terastallized": false,
    "tera_type": null
  },
  "defender": {
    "pokemon_id": 7,
    "base_stats": { ... },
    "evs": { ... },
    "nature": "bold",
    "ability": "torrent",
    "item": null,
    "is_terastallized": false,
    "tera_type": null
  },
  "move": {
    "name": "thunderbolt",
    "type": "electric",
    "power": 90,
    "accuracy": 100,
    "category": "special",
    "priority": 0,
    "flags": {
      "contact": false,
      "sound": false,
      "powder": false,
      "reflectable": true,
      "protect": true
    }
  },
  "field": {
    "weather": null,
    "terrain": null,
    "battle_mode": "singles",
    "screens": [],
    "auras": []
  },
  "is_critical": false,
  "random_range": [0.85, 1.0],
  "defender_hp": 100,
  "gen": 9,
  "debug": false
}
```

**Response:**
```json
{
  "min_damage": 73,
  "max_damage": 86,
  "min_percent": 73,
  "max_percent": 86,
  "rolls": [73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86],
  "guaranteed_ko": false,
  "ohko_chance": 0,
  "hits_to_ko": 2,
  "power": 90,
  "stab": 1.0,
  "type_effectiveness": 2.0,
  "critical_multiplier": 1.5,
  "weather": null,
  "terrain": null,
  "breakdown": {
    "attacker": {
      "name": "pikachu",
      "final_stats": { ... },
      "boosted_stats": { ... },
      "ability_effects": []
    },
    "defender": {
      "name": "squirtle",
      "final_stats": { ... },
      "boosted_stats": { ... },
      "ability_effects": []
    },
    "move_effects": {
      "stab": 1.0,
      "type_effectiveness": 2.0,
      "critical": 1.0,
      "weather": 1.0,
      "terrain": 1.0
    }
  }
}
```

**Status Codes:** `200 OK`, `400 Bad Request`, `500 Internal Server Error`

---

## Data Structures

### Pokémon Object

```json
{
  "id": 25,
  "name": "pikachu",
  "types": ["electric"],
  "base_stats": {
    "hp": 35,
    "attack": 55,
    "defense": 40,
    "special-attack": 50,
    "special-defense": 50,
    "speed": 90
  },
  "can_evolve": true
}
```

**Notes:**
- `id`: National Pokédex number (1–1025 for Gen 9)
- `name`: Canonical slug form (lowercase, hyphenated)
- `types`: Array of 1–2 types
- `base_stats`: Object with 6 stats (hyphenated keys: `special-attack`, `special-defense`)

---

### Move Object

```json
{
  "name": "thunderbolt",
  "type": "electric",
  "power": 90,
  "accuracy": 100,
  "pp": 15,
  "category": "special",
  "priority": 0,
  "flags": {
    "contact": false,
    "sound": false,
    "powder": false,
    "reflectable": true,
    "protect": true
  }
}
```

**Notes:**
- `power`: 0 for status moves
- `accuracy`: 0–100 (or > 100 for guaranteed)
- `category`: `physical`, `special`, or `status`
- `priority`: -7 to +5 (higher = goes first)
- `flags`: Boolean object indicating move classification

---

### Nature Object

```json
{
  "name": "adamant",
  "increase": "attack",
  "decrease": "special-attack",
  "multipliers": {
    "attack": 1.1,
    "special-attack": 0.9
  }
}
```

**Notes:**
- Natures modify exactly 2 stats (or none if neutral)
- `multipliers` normalizes stat names (replace `-` with `_`)
- 25 natures total (5 neutral)

---

### Field Object

```json
{
  "weather": "rain",
  "terrain": "grassy",
  "battle_mode": "singles",
  "screens": ["reflect"],
  "auras": ["dark-aura"],
  "trick_room": false,
  "tailwind": false
}
```

**Notes:**
- **Weather:** `sunny`, `rain`, `sand`, `hail`, `snow`, `harsh-sun`, `heavy-rain`, `strong-winds`
- **Terrain:** `grassy`, `psychic`, `electric`, `misty`
- **Battle Mode:** `singles`, `doubles`
- **Screens:** `reflect`, `light-screen`, `aurora-veil`
- **Auras:** `dark-aura`, `fairy-aura`, `electric-surge`, etc.

---

## Payload Examples

### Example 1: Simple Damage Calculation (Pikachu → Squirtle)

**Request:**
```json
POST /api/calc_damage
{
  "attacker": {
    "pokemon_id": 25,
    "base_stats": {
      "hp": 35, "attack": 55, "defense": 40,
      "special-attack": 50, "special-defense": 50, "speed": 90
    },
    "evs": {
      "hp": 0, "attack": 0, "defense": 0,
      "special-attack": 252, "special-defense": 0, "speed": 252
    },
    "nature": "timid",
    "ability": "static",
    "item": null
  },
  "defender": {
    "pokemon_id": 7,
    "base_stats": {
      "hp": 44, "attack": 48, "defense": 65,
      "special-attack": 50, "special-defense": 64, "speed": 43
    },
    "evs": {
      "hp": 252, "attack": 0, "defense": 4,
      "special-attack": 0, "special-defense": 252, "speed": 0
    },
    "nature": "calm",
    "ability": "torrent",
    "item": null
  },
  "move": {
    "name": "thunderbolt",
    "type": "electric",
    "power": 90,
    "accuracy": 100,
    "category": "special",
    "priority": 0,
    "flags": { "contact": false, "sound": false, "reflectable": true }
  },
  "field": {
    "weather": null,
    "terrain": null,
    "battle_mode": "singles"
  },
  "is_critical": false,
  "defender_hp": 100,
  "gen": 9
}
```

**Expected Response:**
```json
{
  "min_damage": 73,
  "max_damage": 86,
  "min_percent": 73,
  "max_percent": 86,
  "guaranteed_ko": false,
  "ohko_chance": 0,
  "hits_to_ko": 2,
  "power": 90,
  "stab": 1.0,
  "type_effectiveness": 2.0,
  "rolls": [73, 74, 75, ..., 86]
}
```

---

### Example 2: Tera-boosted Damage (Charizard → Blastoise)

**Request (Highlights):**
```json
{
  "attacker": {
    "pokemon_id": 6,
    "is_terastallized": true,
    "tera_type": "water"
  },
  "defender": {
    "pokemon_id": 9,
    "is_terastallized": false
  },
  "move": {
    "name": "aqua-jet",
    "type": "water",
    "power": 40,
    "category": "physical",
    "priority": 1
  },
  "field": {
    "weather": "rain",
    "terrain": null
  },
  "gen": 9
}
```

---

### Example 3: Double Battle with Screens & Auras

**Request (Highlights):**
```json
{
  "attacker": { ... },
  "defender": { ... },
  "move": { ... },
  "field": {
    "battle_mode": "doubles",
    "screens": ["reflect", "light-screen"],
    "auras": ["fairy-aura"],
    "weather": "sunny"
  }
}
```

---

## Error Handling

### Common Errors

#### 1. Invalid Pokémon ID

**Request:**
```
GET /api/pokemon/99999
```

**Response (404):**
```json
{
  "error": "pokemon not found"
}
```

---

#### 2. Missing Required Field in Calculation

**Request:**
```json
POST /api/calc_damage
{
  "attacker": { },
  "move": { "name": "tackle" }
}
```

**Response (400):**
```json
{
  "error": "validation failed",
  "message": "Missing required fields: defender"
}
```

---

#### 3. Calculation Failure

**Response (500):**
```json
{
  "error": "calculation failed",
  "message": "[detailed error message]"
}
```

---

## Best Practices

### 1. Cache Data

- Preload `/api/pokemon`, `/api/types`, and `/api/natures` once at startup.
- Reuse cached data for multiple requests.

```python
# Pseudo-code
cache = {
    'pokemon': requests.get('http://localhost:5000/api/pokemon').json(),
    'types': requests.get('http://localhost:5000/api/types').json(),
    'natures': requests.get('http://localhost:5000/api/natures').json()
}
```

---

### 2. Normalize Stat Names

- **Frontend → Backend:** Convert `special-attack` → `special-attack` (API expects hyphens)
- **Backend → Frontend:** May return either format; normalize on client

```python
def normalize_stat(name):
    return name.replace("_", "-")

def denormalize_stat(name):
    return name.replace("-", "_")
```

---

### 3. Validate Before Sending

- Frontend EV system (client-side): this project uses a compact EV representation in the frontend UI to simplify inputs for users. Frontend EVs are specified in "units" where:
  - Each stat accepts 0..32 units (32 = maximum per-stat in the new UI).
  - Total usable units across all stats is 66.
  - These frontend units are converted client-side to the traditional backend EV values before any API request (backend remains unchanged).

Conversion rules (frontend -> backend):
- 0 units → 0 EVs
- n units (1..32) → 4 + (n - 1) * 8 EVs (produces values in the traditional 0..252-like scale)

- Check that frontend EV units sum ≤ 66 (UI enforces this)
- Check that IVs are 0–31
- Check that Pokémon exists before requesting moves/abilities

```python
def validate_evs_frontend(evs_units):
  total_units = sum(evs_units.values())
  if total_units > 66:
    raise ValueError(f"Total EV units ({total_units}) exceeds 66")

def convert_unit_to_backend(n):
  n = int(n) if n else 0
  if n <= 0:
    return 0
  capped = min(32, n)
  return 4 + (capped - 1) * 8

def convert_evs_to_backend(evs_units):
  return {k: convert_unit_to_backend(v) for k, v in evs_units.items()}
```

---

### 4. Handle Rate Limiting

- No explicit rate limiting on the API, but be respectful
- Add small delays between batch requests
- Prefer bulk data endpoints over many single-item requests

---

### 5. Support Multiple Generations

- Always include `"gen": 9` in calc requests (or specify the target gen)
- Moves, abilities, and type matchups may vary by generation
- Future versions may support Gen 8, Gen 7, etc.

```json
{
  "gen": 9,
  "move": { "name": "dark-pulse", ... }
}
```

---

### 6. Field Data is Optional

- All field modifiers (weather, terrain, screens, auras) are optional
- If not provided, assume neutral (no weather, no terrain, etc.)
- Include only the fields that apply to the battle scenario

```json
{
  "field": {
    "weather": "rain"
    // Omit terrain, screens, auras if not applicable
  }
}
```

---

### 7. Interpret Results Carefully

- **`min_damage` / `max_damage`:** Absolute values dealt
- **`min_percent` / `max_percent`:** Percentage of defender's current HP
- **`hits_to_ko`:** Minimum rolls needed to KO (assuming current HP)
- **`guaranteed_ko`:** True if all rolls KO; false if any roll leaves HP ≥ 1
- **`ohko_chance`:** Probability of instant KO (0 if not a chance move)

---

### 8. Debug Mode

- Set `"debug": true` in calc_damage to get detailed breakdown
- Includes modifier values, ability effects, move interactions

```json
{
  "debug": true,
  "breakdown": {
    "attacker": { ... },
    "defender": { ... },
    "move_effects": { ... }
  }
}
```

---

#### 3. `POST /api/find_threats` & `POST /api/find_threats_stream`

Find all Pokémon that can OHKO or 2HKO a target defender with various configurations.

**Request Body:**
```json
{
  "defender": {
    "pokemon_id": 642,
    "base_stats": { "hp": 100, "attack": 65, "defense": 95, "special-attack": 130, "special-defense": 95, "speed": 88 },
    "evs": { "hp": 252, "attack": 0, "defense": 4, "special-attack": 0, "special-defense": 0, "speed": 252 },
    "nature": "bold",
    "types": ["psychic", "flying"],
    "ability": "magic-bounce",
    "item": null,
    "is_terastallized": false,
    "tera_type": null
  },
  "ko_mode": "OHKO",
  "field": {
    "weather": null,
    "terrain": null,
    "battle_mode": "single",
    "reflect": false,
    "light_screen": false,
    "aurora_veil": false
  },
  "analysis_options": {
    "attack_mode": "none",
    "custom_evs": 0,
    "nature_boost": false,
    "item_choice": false,
    "life_orb": false
  }
}
```

**Response (find_threats):**
```json
{
  "defender_hp": 373,
  "ko_mode": "OHKO",
  "threat_count": 42,
  "threats": [
    {
      "attacker_name": "Garchomp",
      "attacker_id": 445,
      "move_name": "earthquake",
      "move_power": 100,
      "damage_min": 280,
      "damage_max": 330,
      "ko_percent": 88,
      "guaranteed_ko": false,
      "other_moves_count": 2
    }
  ]
}
```

**Response (find_threats_stream):** Server-Sent Events (text/event-stream) format:
```
data: {"type": "init", "total": 1025, "defender_hp": 373}
data: {"type": "threat", "data": {"attacker_name": "Garchomp", ...}}
data: {"type": "progress", "processed": 100, "total": 1025, "threats_found": 5}
data: {"type": "complete", "total_threats": 42, "total_processed": 1025}
```

**Notes:**
- `ko_mode`: `"OHKO"` (one-hit KO) or `"2HKO"` (two-hit KO)
- `attack_mode`: `"none"`, `"custom"`, `"max"`, or `"default"` for attack configuration
- `find_threats_stream` returns SSE events for progressive updates (preferred for UI)
- Screen flags (`reflect`, `light_screen`, `aurora_veil`) accept explicit booleans: `true` or `false`
- **Status Codes:** `200 OK`, `400 Bad Request`, `500 Internal Server Error`

---

#### 4. `POST /api/analyze_coverage_stream`

Analyze which Pokémon a given attacker can KO with its move set, with optional defensive bulk simulation.

**Request Body:**
```json
{
  "attacker": {
    "pokemon_id": 6,
    "base_stats": { "hp": 39, "attack": 52, "defense": 43, "special-attack": 60, "special-defense": 50, "speed": 65 },
    "evs": { "hp": 0, "attack": 252, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 4 },
    "nature": "adamant",
    "types": ["fire", "flying"],
    "ability": "blaze",
    "item": null,
    "is_terastallized": false,
    "tera_type": null,
    "stages": {}
  },
  "moves": [
    { "name": "flare-blitz", "type": "fire", "power": 120, "damage_class": "physical" },
    { "name": "aerial-ace", "type": "flying", "power": 60, "damage_class": "physical" },
    { "name": "earthquake", "type": "ground", "power": 100, "damage_class": "physical" },
    { "name": "dragon-dance", "type": "dragon", "power": 0, "damage_class": "status" }
  ],
  "ko_mode": "OHKO",
  "include_no_ko": false,
  "bulk_mode": "none",
  "field": {
    "weather": null,
    "terrain": null,
    "reflect": false,
    "light_screen": false,
    "aurora_veil": false
  }
}
```

**Response (SSE stream):**
```
data: {"type": "init", "total": 1025}
data: {"type": "coverage", "data": {"defender_id": 7, "defender_name": "squirtle", "max_ko_chance": 85.5, ...}}
data: {"type": "progress", "processed": 100, "total": 1025, "coverage_found": 15}
data: {"type": "complete", "total_coverage": 120, "total_processed": 1025}
```

**Parameters:**
- `bulk_mode`: `"none"`, `"custom"`, or `"max"` — defender bulk configuration
- `custom_def_evs` / `custom_spdef_evs` / `custom_hp_evs`: EVs for defensive Pokémon (custom mode)
- `bulk_nature_mode`: `"byMove"` (adapt nature per move) or `"def"` (fixed defensive nature)
- `bulk_assault_vest`: Apply Assault Vest item to defenders
- `bulk_evoluroc`: Apply Eviolite to unevolved defenders
- **Status Codes:** `200 OK`, `400 Bad Request`, `500 Internal Server Error`

---

## Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/pokemon` | GET | List all Pokémon |
| `/api/pokemon/<id>` | GET | Get Pokémon details |
| `/api/pokemon/<id>/moves` | GET | Get Pokémon moves |
| `/api/pokemon/<id>/abilities` | GET | Get Pokémon abilities |
| `/api/types` | GET | Get type matchups |
| `/api/natures` | GET | Get nature effects |
| `/api/calc_stats` | POST | Calculate final stats |
| `/api/calc_damage` | POST | Calculate damage rolls |
| `/api/find_threats` | POST | Find all KO threats (buffered response) |
| `/api/find_threats_stream` | POST | Find all KO threats (streaming) |
| `/api/analyze_coverage_stream` | POST | Analyze coverage vs all Pokémon (streaming) |

---

**Last Updated:** 2026-03-02  
**API Version:** 1.0 (Gen 9 Stable)  
**Data Pipeline:** Automated via `run_all.py` with comprehensive logging  
**Mega Evolution:** All mega forms automatically inherit base moves  
**Screen Flags:** Reflect/Light Screen/Aurora Veil must be sent as explicit booleans (`true`/`false`) in `field`
