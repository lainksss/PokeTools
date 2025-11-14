# Data — PokeTools

This folder contains the JSON datasets used by the backend.

Files of interest
- `all_pokemon.json` — main Pokémon dataset (id, types, base_stats, forms...)
- `all_moves.json` — move database (power, type, damage_class, accuracy)
- `all_pokemon_moves.json` — mapping from Pokémon -> moves
- `all_pokemon_abilities.json` — mapping from Pokémon -> abilities
- `all_natures.json` — nature effects (increase/decrease)
- `all_pokemon_names_multilang.json` — translated names for UI

Updating data
- Scripts that import or generate these files are in `backend/importation/`.
- If you update source data, run the appropriate import script and validate the output JSON.

Validation
- Keep the following invariants:
  - `base_stats` contains keys for `hp, attack, defense, special-attack, special-defense, speed` (or normalized forms)
  - `types` is an array of one or two type slugs
  - Moves include `power` (int or null), `type`, and `damage_class` (physical/special/status)

If you need help converting a dataset into the expected shape, tell me which file and I can prepare a small import helper.
