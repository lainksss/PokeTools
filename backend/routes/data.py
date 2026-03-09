"""Data endpoints for PokeTools API.

GET /api/pokemon - liste complète des pokémons
GET /api/pokemon/:id - détails d'un pokémon spécifique
GET /api/pokemon/:id/moves - mouvements d'un pokémon
GET /api/pokemon/:id/abilities - talents d'un pokémon
GET /api/types - liste de tous les types
GET /api/natures - liste de toutes les natures
GET /api/pokemon-names - traductions des noms
GET /api/move-names - traductions des attaques
GET /api/abilities - liste des talents avec descriptions
GET /api/items - liste des objets
GET /api/health - health check
"""

from flask import Blueprint, jsonify

# Support importing when package is `backend.routes` or when `routes` is on PYTHONPATH
try:
    from utils.data_loader import load_json
except (ImportError, ModuleNotFoundError):
    from ..utils.data_loader import load_json

bp = Blueprint('data', __name__, url_prefix='/api')


@bp.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "service": "PokeTools-backend"})


@bp.route("/pokemon", methods=["GET"])
def pokemon_list():
    """Retourne la liste complète des pokémons avec leurs stats de base."""
    pok = load_json("all_pokemon.json") or {}
    evo = load_json("pokemon_evolution.json") or {}
    results = []
    for slug, data in pok.items():
        if not data:
            continue
        evo_info = evo.get(slug, {})
        entry = {
            "id": data.get("id"),
            "name": slug,
            "types": data.get("types", []),
            "base_stats": data.get("base_stats", {}),
            "can_evolve": evo_info.get("can_evolve", False)
        }
        results.append(entry)
    # Trier par ID
    results.sort(key=lambda x: x.get("id", 0))
    return jsonify({"count": len(results), "results": results})


@bp.route("/pokemon/<int:pokemon_id>", methods=["GET"])
def pokemon_detail(pokemon_id: int):
    """Retourne les détails d'un pokémon spécifique par son ID."""
    pok = load_json("all_pokemon.json") or {}
    for slug, data in pok.items():
        if data and data.get("id") == pokemon_id:
            return jsonify({
                "id": data.get("id"),
                "name": slug,
                "types": data.get("types", []),
                "base_stats": data.get("base_stats", {})
            })
    return jsonify({"error": "pokemon not found"}), 404


@bp.route("/pokemon/<int:pokemon_id>/moves", methods=["GET"])
def pokemon_moves(pokemon_id: int):
    """Retourne la liste des moves d'un pokémon par son ID."""
    mapping = load_json("all_pokemon_moves.json") or {}
    moves = mapping.get(str(pokemon_id))
    # If not found, try to handle mega forms by falling back to the base form's moves
    if moves is None:
        try:
            all_pok = load_json("all_pokemon.json") or {}
            # find slug for this pokemon_id
            slug = None
            for s, d in all_pok.items():
                if d and d.get("id") == pokemon_id:
                    slug = s
                    break
            if slug and "-mega" in slug:
                # derive base slug by removing the '-mega' part and any '-x'/'-y' suffix
                # examples: 'charizard-mega-x' -> 'charizard', 'venusaur-mega' -> 'venusaur'
                if slug.endswith(('-x', '-y')) and "-mega-" in slug:
                    base_slug = slug.split("-mega", 1)[0]
                else:
                    base_slug = slug.replace("-mega", "")

                # lookup base id
                base_id = None
                base_entry = all_pok.get(base_slug)
                if base_entry:
                    base_id = base_entry.get("id")

                if base_id:
                    moves = mapping.get(str(base_id))
        except Exception:
            moves = None

    if moves is None:
        return jsonify({"error": "moves not found"}), 404
    
    # Charger les détails des moves
    all_moves = load_json("all_moves.json") or {}
    detailed_moves = []
    for move_slug in moves:
        move_data = all_moves.get(move_slug, {})
        detailed_moves.append({
            "name": move_slug,
            "type": move_data.get("type"),
            "power": move_data.get("power"),
            "accuracy": move_data.get("accuracy"),
            "damage_class": move_data.get("damage_class")
        })
    
    return jsonify({"pokemon_id": pokemon_id, "count": len(detailed_moves), "moves": detailed_moves})


@bp.route("/pokemon/<int:pokemon_id>/abilities", methods=["GET"])
def pokemon_abilities(pokemon_id: int):
    """Retourne la liste des talents d'un pokémon par son ID."""
    mapping = load_json("all_pokemon_abilities.json") or {}
    abilities = mapping.get(str(pokemon_id))
    if abilities is None:
        return jsonify({"error": "abilities not found"}), 404
    return jsonify({"pokemon_id": pokemon_id, "count": len(abilities), "abilities": abilities})


@bp.route("/pokemon-abilities-all", methods=["GET"])
def pokemon_abilities_all():
    """Retourne le mapping complet de tous les pokémons vers leurs talents pour le frontend.
    
    Chaque Pokémon a une liste de talents, le premier étant le talent primaire.
    Format: { "pokemon_id": ["ability1", "ability2", ...], ... }
    """
    mapping = load_json("all_pokemon_abilities.json") or {}
    # Convert string keys to integers for cleaner frontend usage
    result = {}
    for pokemon_id_str, abilities in mapping.items():
        try:
            pokemon_id = int(pokemon_id_str)
            # Ensure abilities is a list with at least one ability (primary)
            if abilities and len(abilities) > 0:
                result[pokemon_id] = abilities
        except (ValueError, TypeError):
            continue
    return jsonify({"count": len(result), "abilities_map": result})


@bp.route("/types", methods=["GET"])
def types():
    """Retourne la liste de tous les types."""
    types_data = load_json("all_types.json") or {}
    type_names = sorted(list(types_data.keys()))
    return jsonify({"count": len(type_names), "types": type_names})


@bp.route("/pokemon-names", methods=["GET"])
def pokemon_names():
    """Retourne les traductions des noms de Pokémon."""
    names_data = load_json("all_pokemon_names_multilang.json") or {}
    return jsonify(names_data)


@bp.route("/move-names", methods=["GET"])
def move_names():
    """Retourne les traductions des noms d'attaques (toutes langues)."""
    moves_data = load_json("all_move_names_multilang.json") or {}
    return jsonify(moves_data)


@bp.route("/move/<string:move_slug>", methods=["GET"])
def move_detail(move_slug: str):
    """Return full move details from all_moves.json for the given slug.

    Example: GET /api/move/bullet-seed
    """
    all_moves = load_json("all_moves.json") or {}
    mv = all_moves.get(move_slug)
    if mv is None:
        return jsonify({"error": "move not found"}), 404
    # Attach the slug as name for convenience
    resp = {"name": move_slug}
    resp.update(mv)
    return jsonify(resp)


@bp.route("/abilities", methods=["GET"])
def abilities():
    """Return a list of ability objects with slug, en/fr names and descriptions.

    The source of truth for slugs is `all_pokemon_abilities.json` which maps
    pokemon IDs to ability slugs. Translations/descriptions are read from
    `all_ability_translations.json` (indexed by numeric id). We attempt to
    match translation entries to slugs by comparing the English name (lowercased)
    to the slug with hyphens replaced by spaces.
    """
    # Load raw sources
    abilities_mapping = load_json("all_pokemon_abilities.json") or {}
    ability_translations = load_json("all_ability_translations.json") or {}

    # Build unique slug set from abilities_mapping
    slug_set = set()
    for k, v in abilities_mapping.items():
        if isinstance(v, list):
            for slug in v:
                if slug:
                    slug_set.add(slug)

    results = []
    # Create a list of translation entries for faster lookup
    entries = []
    for aid, data in (ability_translations.items() if isinstance(ability_translations, dict) else []):
        try:
            en = data.get("names", {}).get("en")
            fr = data.get("names", {}).get("fr")
            desc_en = data.get("descriptions", {}).get("en", "")
            desc_fr = data.get("descriptions", {}).get("fr", "")
            entries.append({"id": aid, "en": en, "fr": fr, "desc_en": desc_en, "desc_fr": desc_fr})
        except Exception:
            continue

    for slug in sorted(slug_set):
        # normalize slug to compare with English name
        norm = slug.replace("-", " ").lower()
        found = None
        for e in entries:
            if not e.get("en"):
                continue
            if e.get("en").lower() == norm:
                found = e
                break

        if found:
            obj = {
                "slug": slug,
                "en": found.get("en") or slug,
                "fr": found.get("fr") or found.get("en") or slug,
                "description_en": found.get("desc_en") or "",
                "description_fr": found.get("desc_fr") or ""
            }
        else:
            # fallback: use slug as name
            obj = {
                "slug": slug,
                "en": slug,
                "fr": slug,
                "description_en": "",
                "description_fr": ""
            }
        results.append(obj)

    return jsonify({"abilities": results, "count": len(results)})


@bp.route("/items", methods=["GET"])
def items():
    """Return localized items registry for frontend consumption."""
    items_data = load_json("all_items.json") or {}
    # Transform object to array with slugs
    items_list = []
    for slug, data in items_data.items():
        item_obj = {
            "slug": slug,
            "en": data.get("en", slug),
            "fr": data.get("fr", slug),
            "description_en": data.get("description", {}).get("en", ""),
            "description_fr": data.get("description", {}).get("fr", "")
        }
        items_list.append(item_obj)
    return jsonify({"items": items_list, "count": len(items_list)})


@bp.route("/natures", methods=["GET"])
def natures():
    """Retourne la liste de toutes les natures avec leurs effets."""
    natures_data = load_json("all_natures.json") or {}
    results = []
    for name, data in natures_data.items():
        results.append({
            "name": name,
            "increase": data.get("increase"),
            "decrease": data.get("decrease")
        })
    # Trier alphabétiquement
    results.sort(key=lambda x: x.get("name", ""))
    return jsonify({"count": len(results), "natures": results})
