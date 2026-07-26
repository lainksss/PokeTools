"""import_all_champions_pokemons.py

Récupère la liste des Pokémon disponibles dans Pokémon Champions depuis Bulbapedia,
puis enrichit chaque entrée avec un champ `pokemon_ids` contenant les IDs numériques
exacts (depuis all_pokemon.json) pour TOUTES les formes :
  - formes de base
  - formes régionales (Alolan, Galarian, Hisuian, Paldean…)
  - méga-évolutions (Mega X, Mega Y, etc.)
  - primals
  - toutes les autres formes alternatives (Rotom, Castform, Lycanroc…)
"""
import asyncio, json, re, sys
from pathlib import Path
import aiohttp
from bs4 import BeautifulSoup

# MediaWiki API endpoint — bypasses Cloudflare protection on the normal wiki URL
API_URL = (
    "https://bulbapedia.bulbagarden.net/w/api.php"
    "?action=parse"
    "&page=List_of_Pok%C3%A9mon_in_Pok%C3%A9mon_Champions"
    "&prop=text"
    "&format=json"
    "&formatversion=2"
)
HEADERS = {
    "User-Agent": "PokeTools-importer/1.0 (educational project; contact via GitHub)",
    "Accept": "application/json",
}

SECTION_MAP = {
    "List of Pokémon in Champions": "main",
    "Mega Evolutions":              "mega",
    "Other forms":                  "other",
    "Untransferable":               None,
}

def clean(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip()

def parse_page(html: str) -> list[dict]:
    """
    Parse the rendered HTML from the MediaWiki API.

    Table structure (per row):
      col 0 : td  — Ndex  e.g. "#0003"
      col 1 : th  — sprite image  (skip)
      col 2 : td  — Pokémon name + optional form in <small>
      col 3 : td  — Type 1
      col 4 : td  — Type 2  (may be missing for mono-type)
      col N-2 : td — Normally available? (Yes / No / Transfer only)
      col N-1 : td — Version added  e.g. "1.0.2"
      col N   : td — Learnset link  (skip)
    """
    soup = BeautifulSoup(html, "html.parser")
    entries, seen = [], set()
    current_section = "main"
    current_ndex = ""

    for el in soup.find_all(["h2", "h3", "h4", "table"]):
        # ── Section detection ──────────────────────────────────────────
        if el.name in ("h2", "h3", "h4"):
            txt = clean(el.get_text())
            for key, label in SECTION_MAP.items():
                if key in txt:
                    current_section = label
                    break

        # ── Table parsing ──────────────────────────────────────────────
        elif el.name == "table" and "roundtable" in el.get("class", []):
            if current_section is None:
                continue

            for tr in el.find_all("tr"):
                cells = tr.find_all(["td", "th"])
                if not cells:
                    continue
                # Skip pure header rows
                if all(c.name == "th" for c in cells):
                    continue

                texts = [clean(c.get_text(" ", strip=True)) for c in cells]

                # ── Ndex (col 0, td) ──────────────────────────────────
                ndex_match = re.match(r"^#(\d+)", texts[0])
                if ndex_match:
                    current_ndex = str(int(ndex_match.group(1)))  # strip leading zeros
                elif not current_ndex:
                    continue  # no Ndex yet → skip

                # After Ndex we expect: [sprite_th, name_td, type1_td, ...]
                # col 0 = ndex td
                # col 1 = sprite th  → skip (no useful text)
                # col 2 = name td
                # col 3 = type1 td
                # col 4 = type2 td  (or avail if mono-type)
                # ...
                # col -3 = avail
                # col -2 = version
                # col -1 = learnset (skip)
                if len(cells) < 5:
                    continue

                # Name cell = cells[2]
                name_cell = cells[2]
                name_link = name_cell.find("a")
                name = clean(name_link.get_text()) if name_link else texts[2]
                # Form is in a <small> tag inside the name cell
                small = name_cell.find("small")
                form = clean(small.get_text()) if small else ""

                type1 = texts[3]
                # version is always second-to-last col, learnset is last
                version   = texts[-2]
                avail_raw = texts[-3]
                # type2 is texts[4] unless there's no separate type2 column
                type2 = texts[4] if len(cells) >= 7 else ""

                # Validate version looks like "X.Y.Z"
                if not re.match(r"^\d+\.\d+", version):
                    version = ""

                normally_available = avail_raw.lower() not in ("no", "transfer only", "")

                key = (current_ndex, name, form, current_section)
                if key in seen:
                    continue
                seen.add(key)

                entries.append({
                    "ndex":               current_ndex,
                    "name":               name,
                    "form":               form,
                    "type1":              type1,
                    "type2":              type2,
                    "normally_available": normally_available,
                    "version_added":      version,
                    "section":            current_section,
                })

    return entries


# ── Mots à ignorer lors de la construction du suffixe de slug ─────────────────
# Le nom du Pokémon, "form", "forme", "mode", "pattern", "variety", "trim", etc.
STOP_WORDS = {
    "form", "forme", "mode", "pattern", "variety", "trim",
    "regional", "breed",
}


def form_to_slug_suffix(name_slug: str, form_str: str) -> str | None:
    """Convertit le champ 'form' en suffixe de slug à ajouter après le nom de base.

    Exemples:
      name='venusaur',  form='Mega Venusaur'   -> 'mega'
      name='charizard', form='Mega Charizard X' -> 'mega-x'
      name='raichu',    form='Alolan Form'      -> 'alolan'
      name='aegislash', form='Blade Forme'      -> 'blade'
      name='rotom',     form='Heat Rotom'       -> 'heat'
      name='maushold',  form='Family of Four'   -> 'family-of-four'
      name='lycanroc',  form='Midday Form'      -> 'midday'
    """
    raw = form_str.strip().lower()
    # Split en tokens (mots séparés par espaces/ponctuation)
    tokens = re.split(r"[\s\-_/()]+", raw)

    # Retire les parties du nom de base et les stop words
    name_parts = set(name_slug.split("-"))
    suffix_tokens = [
        t for t in tokens
        if t and t not in STOP_WORDS and t not in name_parts
    ]

    if not suffix_tokens:
        return None

    return "-".join(suffix_tokens)


def resolve_pokemon_ids(entries: list[dict]) -> list[dict]:
    """Enrichit chaque entrée avec un champ `pokemon_ids` contenant les IDs
    Pokémon résolus depuis all_pokemon.json.

    Stratégie :
      - Si form == "" : chercher le slug exact du nom de base (id == ndex)
      - Si form != "" : construire un slug candidat (nom + suffixe de forme)
        et chercher dans all_pokemon.json. Recherche partielle en fallback.
    """
    # Chemin vers all_pokemon.json (relatif à la racine du projet)
    root = Path(__file__).parent.parent.parent
    pokemon_path = root / "data" / "all_pokemon.json"
    if not pokemon_path.exists():
        print(f"[WARN] {pokemon_path} not found — pokemon_ids will be empty")
        for entry in entries:
            entry["pokemon_ids"] = []
        return entries

    with open(pokemon_path, encoding="utf-8") as f:
        all_pokemon: dict = json.load(f)

    # Index : ndex_id -> liste de (slug, poke_id)
    id_to_slugs: dict[int, list] = {}
    for slug, data in all_pokemon.items():
        if not data:
            continue
        poke_id = data.get("id")
        if poke_id:
            id_to_slugs.setdefault(poke_id, []).append((slug, poke_id))

    for entry in entries:
        try:
            ndex = int(entry.get("ndex", 0))
        except (ValueError, TypeError):
            entry["pokemon_ids"] = []
            continue
        if not ndex:
            entry["pokemon_ids"] = []
            continue

        form = (entry.get("form") or "").strip()
        name_slug = (entry.get("name") or "").strip().lower().replace(" ", "-")

        resolved: list[int] = []

        if not form:
            # Forme de base : slug exact = nom de base
            matched = False
            for slug, poke_id in id_to_slugs.get(ndex, []):
                if slug == name_slug:
                    resolved.append(poke_id)
                    matched = True
                    break
            if not matched:
                # Fallback : n'importe quel slug avec le bon ndex
                for slug, poke_id in id_to_slugs.get(ndex, []):
                    resolved.append(poke_id)
                    break
        else:
            # Forme alternative : construire le slug candidat
            suffix = form_to_slug_suffix(name_slug, form)

            if suffix:
                candidate = f"{name_slug}-{suffix}"
                # 1. Correspondance exacte
                if candidate in all_pokemon and all_pokemon[candidate]:
                    resolved.append(all_pokemon[candidate]["id"])
                else:
                    # 2. Recherche partielle : slug contient le nom ET tous les tokens du suffixe
                    suffix_tokens = suffix.split("-")
                    for slug, data in all_pokemon.items():
                        if (data and name_slug in slug and
                                all(tok in slug for tok in suffix_tokens)):
                            resolved.append(data["id"])
                    if not resolved:
                        # 3. Dernier fallback : forme de base (id == ndex)
                        for slug, poke_id in id_to_slugs.get(ndex, []):
                            resolved.append(poke_id)
                            break
            else:
                # Suffixe vide → forme de base
                for slug, poke_id in id_to_slugs.get(ndex, []):
                    resolved.append(poke_id)
                    break

        entry["pokemon_ids"] = sorted(set(resolved))

    return entries


async def fetch_page(session: aiohttp.ClientSession) -> str:
    """Fetch rendered HTML via the MediaWiki JSON API (no Cloudflare protection)."""
    for attempt in range(4):
        try:
            async with session.get(API_URL) as r:
                r.raise_for_status()
                data = await r.json(content_type=None)
            # The API wraps the rendered HTML inside data["parse"]["text"]
            html = data["parse"]["text"]
            if not html:
                raise ValueError("Empty HTML returned by MediaWiki API")
            return html
        except Exception as e:
            wait = 1.5 * (2 ** attempt)
            print(f"  [WARN] attempt {attempt+1}/4 — {e!r}  (retry in {wait:.1f}s)")
            await asyncio.sleep(wait)
    raise RuntimeError("Could not fetch Bulbapedia page after 4 attempts.")


async def build(save_to: str = "data/all_champions_pokemons.json") -> None:
    Path("data").mkdir(exist_ok=True)

    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout, headers=HEADERS) as session:
        print("Fetching Bulbapedia page…")
        html = await fetch_page(session)

    entries = parse_page(html)

    # Enrichir chaque entrée avec les IDs Pokémon résolus
    print("Resolving pokemon_ids from all_pokemon.json…")
    entries = resolve_pokemon_ids(entries)

    # Statistiques rapides
    with_ids = sum(1 for e in entries if e.get("pokemon_ids"))
    without_ids = len(entries) - with_ids
    if without_ids:
        print(f"  [WARN] {without_ids} entries could not be resolved to a pokemon_id")
        for e in entries:
            if not e.get("pokemon_ids"):
                print(f"    - ndex={e['ndex']} name={e['name']!r} form={e['form']!r}")

    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    from collections import Counter
    by_sec = Counter(e["section"] for e in entries)
    print(f"[OK] Saved {len(entries)} entries ({with_ids} with pokemon_ids) -> {save_to}")
    for sec, n in by_sec.items():
        print(f"  {sec:8s}: {n}")


def enrich_existing(save_to: str = "data/all_champions_pokemons.json") -> None:
    """Enrichit le fichier JSON existant avec pokemon_ids sans ré-importer depuis Bulbapedia."""
    path = Path(save_to)
    if not path.exists():
        # Essai avec chemin relatif à la racine du projet
        root = Path(__file__).parent.parent.parent
        path = root / save_to
    if not path.exists():
        print(f"[ERROR] {save_to} not found — run the full import first")
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        entries = json.load(f)

    print(f"Loaded {len(entries)} entries from {path}")
    print("Resolving pokemon_ids from all_pokemon.json…")
    entries = resolve_pokemon_ids(entries)

    with_ids = sum(1 for e in entries if e.get("pokemon_ids"))
    without_ids = len(entries) - with_ids
    if without_ids:
        print(f"  [WARN] {without_ids} entries could not be resolved to a pokemon_id")
        for e in entries:
            if not e.get("pokemon_ids"):
                print(f"    - ndex={e['ndex']:>4s}  name={e['name']!r:20s}  form={e['form']!r}")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    print(f"[OK] Enriched {len(entries)} entries ({with_ids} with pokemon_ids) -> {path}")


if __name__ == "__main__":
    if "--enrich-only" in sys.argv:
        # Mode sans import réseau : enrichit le fichier existant
        enrich_existing()
    else:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(build())