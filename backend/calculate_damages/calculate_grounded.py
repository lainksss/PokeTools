from typing import Dict


def is_grounded(pokemon: Dict, field: Dict = None) -> bool:
    """Determine if a Pokémon is grounded (affected by terrain).
    
    A Pokémon is ungrounded if any of the following apply:
    - It has the Flying type
    - It has the Ability Levitate
    - It is holding an Air Balloon
    - It is under the effect of Magnet Rise or Telekinesis
    
    A Pokémon is grounded if:
    - Gravity is in effect (overrides all ungrounding effects)
    - It is under the effect of Smack Down or Ingrain
    - Or none of the ungrounding conditions apply
    
    Args:
        pokemon: Dict with keys like 'types', 'ability', 'item', 'magnet_rise', 'telekinesis', etc.
        field: Optional Dict with keys like 'gravity'
    
    Returns:
        True if the Pokémon is grounded, False otherwise
    """
    if field is None:
        field = {}
    
    # Gravity forces all Pokémon to be grounded
    if field.get("gravity"):
        return True
    
    # Smack Down and Ingrain force grounded status
    if pokemon.get("smack_down") or pokemon.get("ingrain"):
        return True
    
    # Check ungrounding conditions
    types = pokemon.get("types", [])
    ability = pokemon.get("ability", "")
    item = pokemon.get("item", "")
    
    # Flying type makes Pokémon ungrounded
    if "flying" in types:
        return False
    
    # Levitate ability makes Pokémon ungrounded
    if ability == "levitate":
        return False
    
    # Air Balloon makes Pokémon ungrounded (until popped)
    if item == "air-balloon" and not pokemon.get("air_balloon_popped"):
        return False
    
    # Magnet Rise makes Pokémon ungrounded
    if pokemon.get("magnet_rise"):
        return False
    
    # Telekinesis makes Pokémon ungrounded
    if pokemon.get("telekinesis"):
        return False
    
    # Default: grounded
    return True
