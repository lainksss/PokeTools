import asyncio, json, sys
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
    import re
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
    import re
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

    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    from collections import Counter
    by_sec = Counter(e["section"] for e in entries)
    print(f"[OK] Saved {len(entries)} entries -> {save_to}")
    for sec, n in by_sec.items():
        print(f"  {sec:8s}: {n}")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(build())