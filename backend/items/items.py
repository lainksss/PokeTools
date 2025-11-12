"""Item registry and effect computation for Pokémon held items.

This module contains all held items and their effects on damage calculation,
including type-boosting items, berries, choice items, and special items.
"""
from typing import Dict, Optional, Tuple

# Item registry - all held items with their effects
ITEMS: Dict[str, Dict] = {
    # Type-boosting items (+20%)
    "charcoal": {"type_boost": "fire"},
    "magnet": {"type_boost": "electric"},
    "sharp-beak": {"type_boost": "flying"},
    "black-belt": {"type_boost": "fighting"},
    "mystic-water": {"type_boost": "water"},
    "miracle-seed": {"type_boost": "grass"},
    "never-melt-ice": {"type_boost": "ice"},
    "poison-barb": {"type_boost": "poison"},
    "hard-stone": {"type_boost": "rock"},
    "soft-sand": {"type_boost": "ground"},
    "spell-tag": {"type_boost": "ghost"},
    "twisted-spoon": {"type_boost": "psychic"},
    "dragon-fang": {"type_boost": "dragon"},
    "black-glasses": {"type_boost": "dark"},
    "metal-coat": {"type_boost": "steel", "evolves": {"onix": "steelix", "scyther": "scizor"}},
    "silk-scarf": {"type_boost": "normal"},
    "silver-powder": {"type_boost": "bug"},
    "fairy-feather": {"type_boost": "fairy"},
    
    # Incenses (+20% type boost)
    "odd-incense": {"type_boost": "psychic"},
    "rose-incense": {"type_boost": "grass"},
    "sea-incense": {"type_boost": "water"},
    "wave-incense": {"type_boost": "water"},
    "rock-incense": {"type_boost": "rock"},
    "full-incense": {"priority_modifier": -1},
    
    # Plates (+20% type boost)
    "flame-plate": {"type_boost": "fire"},
    "splash-plate": {"type_boost": "water"},
    "meadow-plate": {"type_boost": "grass"},
    "zap-plate": {"type_boost": "electric"},
    "icicle-plate": {"type_boost": "ice"},
    "fist-plate": {"type_boost": "fighting"},
    "toxic-plate": {"type_boost": "poison"},
    "earth-plate": {"type_boost": "ground"},
    "sky-plate": {"type_boost": "flying"},
    "mind-plate": {"type_boost": "psychic"},
    "insect-plate": {"type_boost": "bug"},
    "stone-plate": {"type_boost": "rock"},
    "spooky-plate": {"type_boost": "ghost"},
    "draco-plate": {"type_boost": "dragon"},
    "dread-plate": {"type_boost": "dark"},
    "iron-plate": {"type_boost": "steel"},
    "pixie-plate": {"type_boost": "fairy"},
    
    # Special orbs for legendaries
    "adamant-orb": {"species": "dialga", "types": ["dragon", "steel"]},
    "lustrous-orb": {"species": "palkia", "types": ["dragon", "water"]},
    "griseous-orb": {"species": "giratina", "types": ["dragon", "ghost"]},
    "soul-dew": {"species": ["latios", "latias"], "types": ["psychic", "dragon"]},
    
    # Clamperl evolution items
    "deep-sea-tooth": {"species": "clamperl", "stat_mult": {"special_attack": 2.0}},
    "deep-sea-scale": {"species": "clamperl", "stat_mult": {"special_defense": 2.0}},
    
    # Pikachu item
    "light-ball": {"species": "pikachu", "stat_mult": {"attack": 2.0, "special_attack": 2.0}},
    
    # Cubone/Marowak item
    "thick-club": {"species": ["cubone", "marowak"], "stat_mult": {"attack": 2.0}},
    
    # Choice items (+50% stat)
    "choice-band": {"stat_mult": {"attack": 1.5}},
    "choice-specs": {"stat_mult": {"special_attack": 1.5}},
    "choice-scarf": {"stat_mult": {"speed": 1.5}},
    
    # Power items
    "muscle-band": {"category_boost": "physical"},
    "wise-glasses": {"category_boost": "special"},
    
    # Expert Belt (+20% super effective)
    "expert-belt": {"super_effective_boost": True},
    
    # Life Orb (+30% power)
    "life-orb": {"power_mult": 1.3},
    
    # Eviolite (+50% defenses for non-fully evolved)
    "eviolite": {"unevolved_def_boost": True},
    
    # Assault Vest (+50% Sp.Def)
    "assault-vest": {"stat_mult": {"special_defense": 1.5}},
    
    # Normal Gem (+50% first Normal move)
    "normal-gem": {"one_use_type_boost": "normal", "gem_mult": 1.5},
    
    # Loaded Dice
    "loaded-dice": {"multi_hit_minimum": 4},
    
    # Iron Ball / Macho Brace (halves speed)
    "iron-ball": {"stat_mult": {"speed": 0.5}, "grounds": True},
    "macho-brace": {"stat_mult": {"speed": 0.5}},
    
    # Balloon
    "air-balloon": {"ground_immunity": True, "one_use": True},
    
    # Booster Energy
    "booster-energy": {"paradox_boost": True, "one_use": True},
    
    # Ogerpon Masks
    "hearthflame-mask": {"species": "ogerpon", "category_boost": "physical", "type_boost_mult": 1.2},
    "wellspring-mask": {"species": "ogerpon", "category_boost": "physical", "type_boost_mult": 1.2},
    "cornerstone-mask": {"species": "ogerpon", "category_boost": "physical", "type_boost_mult": 1.2},
    
    # Type-resist berries (halve super effective damage, one use)
    "chople-berry": {"resist_type": "fighting"},
    "coba-berry": {"resist_type": "flying"},
    "kebia-berry": {"resist_type": "poison"},
    "shuca-berry": {"resist_type": "ground"},
    "charti-berry": {"resist_type": "rock"},
    "tanga-berry": {"resist_type": "bug"},
    "kasib-berry": {"resist_type": "ghost"},
    "haban-berry": {"resist_type": "dragon"},
    "colbur-berry": {"resist_type": "dark"},
    "babiri-berry": {"resist_type": "steel"},
    "occa-berry": {"resist_type": "fire"},
    "passho-berry": {"resist_type": "water"},
    "wacan-berry": {"resist_type": "electric"},
    "rindo-berry": {"resist_type": "grass"},
    "yache-berry": {"resist_type": "ice"},
    "roseli-berry": {"resist_type": "fairy"},
    "payapa-berry": {"resist_type": "psychic"},
    "chilan-berry": {"resist_type": "normal"},
}


def get_item(slug: Optional[str]) -> Optional[Dict]:
    """Get item definition by slug."""
    if not slug:
        return None
    key = str(slug).lower().replace("_", "-")
    return ITEMS.get(key)


def apply_item_stat_modifiers(
    attacker: Dict,
    defender: Dict,
    move: Dict,
) -> Tuple[Dict, Dict]:
    """Apply stat modifications from held items BEFORE damage calculation.
    
    Returns modified (attacker, defender) dicts.
    """
    import copy
    attacker = copy.deepcopy(attacker)
    defender = copy.deepcopy(defender)
    
    attacker_item = get_item(attacker.get("item"))
    defender_item = get_item(defender.get("item"))
    category = move.get("damage_class", "physical")
    
    # Apply attacker item stat boosts
    if attacker_item:
        # Check for species-specific items first
        has_species_requirement = "species" in attacker_item
        
        if has_species_requirement:
            # Species-specific stat boosts (Light Ball, Thick Club, etc.)
            species = attacker.get("species", "").lower()
            item_species = attacker_item["species"]
            if isinstance(item_species, list):
                is_match = species in item_species
            else:
                is_match = species == item_species
            
            if is_match and "stat_mult" in attacker_item:
                for stat, mult in attacker_item["stat_mult"].items():
                    if stat in attacker:
                        attacker[stat] = int(attacker[stat] * mult)
        else:
            # Generic stat multipliers (Choice items, etc.) - only if NO species requirement
            if "stat_mult" in attacker_item:
                for stat, mult in attacker_item["stat_mult"].items():
                    if stat in attacker:
                        attacker[stat] = int(attacker[stat] * mult)
        
        # Iron Ball grounds Flying types
        if attacker_item.get("grounds"):
            attacker["is_grounded"] = True
    
    # Apply defender item stat boosts
    if defender_item:
        if "stat_mult" in defender_item:
            for stat, mult in defender_item["stat_mult"].items():
                if stat in defender:
                    defender[stat] = int(defender[stat] * mult)
        
        # Eviolite boost
        if defender_item.get("unevolved_def_boost") and defender.get("can_evolve"):
            defender["defense"] = int(defender.get("defense", 0) * 1.5)
            defender["special_defense"] = int(defender.get("special_defense", 0) * 1.5)
    
    return attacker, defender


def compute_item_damage_multiplier(
    attacker_item_slug: Optional[str],
    defender_item_slug: Optional[str],
    move: Dict,
    attacker: Dict,
    defender: Dict,
    type_effectiveness: float,
    category: str,
) -> Tuple[float, Dict]:
    """Compute damage multiplier from held items.
    
    Returns (multiplier, effects_dict).
    """
    multiplier = 1.0
    effects = {}
    
    attacker_item = get_item(attacker_item_slug)
    defender_item = get_item(defender_item_slug)
    
    move_type = move.get("type", "").lower()
    attacker_species = attacker.get("species", "").lower()
    
    # Attacker item boosts
    if attacker_item:
        # Type-boosting items (+20%)
        if "type_boost" in attacker_item:
            if move_type == attacker_item["type_boost"]:
                multiplier *= 1.2
                effects["item_type_boost"] = attacker_item_slug
        
        # Species-specific type boosts (Orbs for legendaries)
        if "species" in attacker_item and "types" in attacker_item:
            item_species = attacker_item["species"]
            if isinstance(item_species, list):
                is_match = attacker_species in item_species
            else:
                is_match = attacker_species == item_species
            
            if is_match and move_type in attacker_item["types"]:
                multiplier *= 1.2
                effects["species_item_boost"] = attacker_item_slug
        
        # Category boosts (Muscle Band +10%, Wise Glasses +10%)
        if "category_boost" in attacker_item:
            if category == attacker_item["category_boost"]:
                multiplier *= 1.1
                effects["category_boost"] = attacker_item_slug
        
        # Ogerpon Masks (check species + physical category)
        if attacker_item.get("type_boost_mult") and attacker_species == "ogerpon":
            if category == "physical":
                multiplier *= attacker_item["type_boost_mult"]
                effects["ogerpon_mask_boost"] = attacker_item_slug
        
        # Expert Belt (+20% on super effective)
        if attacker_item.get("super_effective_boost") and type_effectiveness > 1.0:
            multiplier *= 1.2
            effects["expert_belt"] = True
        
        # Life Orb (+30%)
        if "power_mult" in attacker_item:
            multiplier *= attacker_item["power_mult"]
            effects["life_orb"] = True
        
        # Normal Gem (one-use +50%)
        if "one_use_type_boost" in attacker_item:
            if move_type == attacker_item["one_use_type_boost"]:
                gem_mult = attacker_item.get("gem_mult", 1.5)
                multiplier *= gem_mult
                effects["gem_consumed"] = attacker_item_slug
    
    # Defender item (resist berries)
    if defender_item and "resist_type" in defender_item:
        if move_type == defender_item["resist_type"] and type_effectiveness > 1.0:
            multiplier *= 0.5
            effects["berry_consumed"] = defender_item_slug
            effects["berry_halved_damage"] = True
    
    return multiplier, effects
