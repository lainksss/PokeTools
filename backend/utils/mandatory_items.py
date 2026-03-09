"""Utility function to handle mandatory items, abilities, and entry stages for special Pokémon forms.

Certain forms (e.g. Zacian/Zamazenta crowned) are represented by swapping the species and move
sets when a rusted item is equipped.  The frontend detects the rusted item and replaces the
user's selected Pokémon with the crowned form; the backend still enforces the same item/
ability requirements and also handles transformation of `iron-head` into Behemoth Blade/Bash
by mutating the move object during damage calculations.  This module forces both the item
and ability and optionally adds stage boosts for abilities like Intrepid Sword and Dauntless
Shield.  It does *not* double‑apply the transformation logic.
"""

# Mandatory configuration per exact Pokémon slug (checked before suffix patterns)
_MANDATORY_CONFIGS_EXACT = {
    'zacian-crowned': {
        'item': 'rusted-sword',
        'ability': 'intrepid-sword',
        # The ability itself grants +1 Attack stage, so we do **not** add it here.
    },
    'zamazenta-crowned': {
        'item': 'rusted-shield',
        'ability': 'dauntless-shield',
        # Dauntless Shield ability handles the defense boost internally.
    },
}

# Mandatory configuration by slug suffix (applied if no exact match)
_MANDATORY_CONFIGS_SUFFIX = {
    '-mega': {'item': 'mega-gem'},
    '-primal': {'item': 'primal-gem'},
}


def get_mandatory_config(pokemon_name):
    """
    Get full mandatory configuration (item, ability, entry_stages) for a Pokémon.

    Args:
        pokemon_name (str): The name/slug of the Pokémon

    Returns:
        dict or None: Config dict with at least 'item', optionally 'ability' and 'entry_stages'
    """
    if not pokemon_name:
        return None

    name = pokemon_name.lower()

    # Exact match first (more specific — crowned before mega/primal)
    if name in _MANDATORY_CONFIGS_EXACT:
        return _MANDATORY_CONFIGS_EXACT[name]

    # Suffix patterns
    for suffix, config in _MANDATORY_CONFIGS_SUFFIX.items():
        if suffix in name:
            return config

    return None


def get_mandatory_item(pokemon_name):
    """Return the mandatory item slug for a Pokémon, or None."""
    config = get_mandatory_config(pokemon_name)
    return config.get('item') if config else None


def get_mandatory_ability(pokemon_name):
    """Return the mandatory ability slug for a Pokémon, or None."""
    config = get_mandatory_config(pokemon_name)
    return config.get('ability') if config else None


def has_mandatory_item(pokemon_name):
    """Check if a Pokémon has a mandatory item."""
    return get_mandatory_item(pokemon_name) is not None


def force_mandatory_item(actor_data):
    """
    Force the mandatory item, ability, and entry stage boosts on an actor if applicable.

    For Mega/Primal forms: forces their gem item.
    For Zacian-Crowned: forces rusted-sword + intrepid-sword ability + +1 Attack stage.
    For Zamazenta-Crowned: forces rusted-shield + dauntless-shield ability + +1 Defense stage.

    Args:
        actor_data (dict): The actor payload (must contain 'name' key)

    Returns:
        dict: The modified actor_data
    """
    if not actor_data or not isinstance(actor_data, dict):
        return actor_data

    pokemon_name = actor_data.get('name')
    config = get_mandatory_config(pokemon_name)

    if config:
        if 'item' in config:
            actor_data['item'] = config['item']
        if 'ability' in config:
            actor_data['ability'] = config['ability']
        if 'entry_stages' in config:
            # Add entry stage boosts on top of existing user stages
            stages = dict(actor_data.get('stages') or {})
            for stat, bonus in config['entry_stages'].items():
                stages[stat] = stages.get(stat, 0) + bonus
            actor_data['stages'] = stages

    # If we've just forced a gem item, we may need to adjust the species name + stats
    item = actor_data.get('item')
    name = actor_data.get('name', '')
    if item in ('mega-gem', 'primal-gem') and name:
        # avoid transforming if already in a special suffix
        if '-mega' not in name and '-primal' not in name and 'crowned' not in name:
            base = name.split('-')[0]
            all_pok = load_json("all_pokemon.json") or {}
            suffix = '-mega' if item == 'mega-gem' else '-primal'
            # gather candidates matching base + suffix
            candidates = [slug for slug in all_pok if slug.startswith(base + suffix)]
            if candidates:
                # pick the one with highest base stat total
                best = max(candidates, key=lambda s: sum(all_pok[s].get('base_stats', {}).values()))
                # update actor_data with new species info
                actor_data['name'] = best
                actor_data['base_stats'] = all_pok[best].get('base_stats')
                actor_data['types'] = all_pok[best].get('types')
                actor_data['id'] = all_pok[best].get('id')
    # Handle item removal: revert mega/primal forms back to base
    if item != 'mega-gem' and '-mega' in name:
        base = name.split('-mega')[0]
        all_pok = load_json("all_pokemon.json") or {}
        if base in all_pok:
            actor_data['name'] = base
            actor_data['base_stats'] = all_pok[base].get('base_stats')
            actor_data['types'] = all_pok[base].get('types')
            actor_data['id'] = all_pok[base].get('id')
    if item != 'primal-gem' and '-primal' in name:
        base = name.split('-primal')[0]
        all_pok = load_json("all_pokemon.json") or {}
        if base in all_pok:
            actor_data['name'] = base
            actor_data['base_stats'] = all_pok[base].get('base_stats')
            actor_data['types'] = all_pok[base].get('types')
            actor_data['id'] = all_pok[base].get('id')

    return actor_data

