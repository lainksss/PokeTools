"""
Fetch all Pokémon abilities from the live PokéAPI — including mega evolutions,
regional forms, and any future entries — using async concurrent requests.

Strategy
--------
1. One single request to /pokemon?limit=100000 to get every URL at once.
2. Fetch all individual Pokémon pages concurrently (semaphore-controlled).
3. Retry with exponential back-off on transient failures.

Output: data/all_pokemon_abilities.json
Format: { "<pokemon_id>": ["ability-slug", ...], ... }
"""

import asyncio
import json
import sys
from pathlib import Path

import aiohttp

# ── tunables ────────────────────────────────────────────────────────────────
BASE              = "https://pokeapi.co/api/v2"
MAX_CONCURRENT    = 25      # simultaneous open connections
MAX_RETRIES       = 4       # attempts per URL before giving up
BACKOFF_BASE      = 1.5     # seconds — multiplied by 2^attempt on each retry
TIMEOUT_SECS      = 20      # per-request timeout
# ────────────────────────────────────────────────────────────────────────────


async def fetch_all_urls(session: aiohttp.ClientSession) -> list[str]:
    """Single request that returns every Pokémon URL known to the API."""
    url = f"{BASE}/pokemon?limit=100000&offset=0"
    async with session.get(url) as r:
        r.raise_for_status()
        data = await r.json()
    urls = [p["url"] for p in data["results"]]
    print(f"API total count : {data['count']}")
    print(f"URLs retrieved  : {len(urls)}")
    return urls


async def fetch_abilities_for(
    session: aiohttp.ClientSession,
    sem: asyncio.Semaphore,
    url: str,
) -> tuple[str, list[str]] | None:
    """
    Fetch one Pokémon page and return (pokemon_id, [ability_slug, ...]).
    Retries up to MAX_RETRIES times with exponential back-off.
    Returns None on permanent failure (logged to stderr).
    """
    pokemon_id = url.rstrip("/").split("/")[-1]

    for attempt in range(MAX_RETRIES):
        try:
            async with sem, session.get(url) as r:
                r.raise_for_status()
                data = await r.json()

            abilities = [a["ability"]["name"] for a in data["abilities"]]
            return pokemon_id, abilities

        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            wait = BACKOFF_BASE * (2 ** attempt)
            print(
                f"  [WARN] id={pokemon_id} attempt {attempt+1}/{MAX_RETRIES} "
                f"— {exc!r}  (retry in {wait:.1f}s)",
                file=sys.stderr,
            )
            await asyncio.sleep(wait)

    print(f"  [ERROR] Giving up on id={pokemon_id} after {MAX_RETRIES} attempts.", file=sys.stderr)
    return None


async def build(save_to: str = "data/all_pokemon_abilities.json") -> None:
    Path("data").mkdir(exist_ok=True)

    timeout = aiohttp.ClientTimeout(total=TIMEOUT_SECS)
    headers = {"User-Agent": "pokemon-abilities-fetcher/2.0"}

    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        urls = await fetch_all_urls(session)

        sem      = asyncio.Semaphore(MAX_CONCURRENT)
        tasks    = [fetch_abilities_for(session, sem, u) for u in urls]

        results  = {}
        done     = 0
        total    = len(tasks)

        for coro in asyncio.as_completed(tasks):
            result = await coro
            done  += 1
            if result is not None:
                pid, abilities = result
                results[pid] = abilities
            if done % 100 == 0 or done == total:
                print(f"  → {done}/{total} done  ({len(results)} ok)")

    # Sort numerically so the file is stable across runs
    sorted_results = dict(sorted(results.items(), key=lambda kv: int(kv[0])))

    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(sorted_results, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved {len(sorted_results)} Pokémon → {save_to}")

    # Sanity checks
    for check_id, label in [("1", "Bulbasaur"), ("10283", "Méga Aligatueur")]:
        val = sorted_results.get(check_id, "MISSING")
        print(f"  {label:20s} ({check_id:>5}) : {val}")


def main() -> None:
    asyncio.run(build())


if __name__ == "__main__":
    main()