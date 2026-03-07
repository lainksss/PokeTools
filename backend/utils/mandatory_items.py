"""Utility function to handle mandatory items for Mega and Primal forms."""


def get_mandatory_item(pokemon_name):
    """
    Determine the mandatory item for a Pokémon based on its name.
    
    Args:
        pokemon_name (str): The name/slug of the Pokémon (e.g., "charizard-mega-x", "kyogre-primal")
    
    Returns:
        str or None: The item slug ("mega-gem" or "primal-gem") or None if not mandatory
    """
    if not pokemon_name:
        return None
    
    name = pokemon_name.lower()
    
    if '-mega' in name:
        return 'mega-gem'
    
    if '-primal' in name:
        return 'primal-gem'
    
    return None


def has_mandatory_item(pokemon_name):
    """
    Check if a Pokémon has a mandatory item.
    
    Args:
        pokemon_name (str): The name/slug of the Pokémon
    
    Returns:
        bool: True if the Pokémon has a mandatory item
    """
    return get_mandatory_item(pokemon_name) is not None


def force_mandatory_item(actor_data):
    """
    Force the mandatory item on an actor (attacker or defender) if applicable.
    
    This modifies the actor_data in place to ensure the correct item is set.
    
    Args:
        actor_data (dict): The actor payload (must contain 'name' key)
    
    Returns:
        dict: The modified actor_data
    """
    if not actor_data or not isinstance(actor_data, dict):
        return actor_data
    
    pokemon_name = actor_data.get('name')
    mandatory_item = get_mandatory_item(pokemon_name)
    
    if mandatory_item:
        actor_data['item'] = mandatory_item
    
    return actor_data
