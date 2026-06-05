import asyncio
import json
import sys
from pathlib import Path
import aiohttp

BASE = "https://pokeapi.co/api/v2"
MAX_CONCURRENT, MAX_RETRIES, BACKOFF_BASE, TIMEOUT_SECS = 25, 4, 1.5, 20
HEADERS = {"User-Agent": "pokemon-move-fetcher-async/3.0", "Cache-Control": "no-cache", "Pragma": "no-cache"}

async def fetch_all_urls(session: aiohttp.ClientSession):
    async with session.get(f"{BASE}/move?limit=100000") as r:
        return (await r.json()).get("results", [])

async def fetch_move_detail(session: aiohttp.ClientSession, sem: asyncio.Semaphore, entry: dict):
    url, name = entry["url"], entry["name"]
    move_id = int(url.rstrip("/").split("/")[-1]) # Extraction de l'ID pour le tri

    for attempt in range(MAX_RETRIES):
        try:
            async with sem, session.get(url) as r:
                data = await r.json()
            
            meta = data.get("meta") or {}
            multi_hit = {"min": meta.get("min_hits"), "max": meta.get("max_hits")} if meta.get("min_hits") and meta.get("max_hits") else None
            
            move = {
                "type": data["type"]["name"], "power": data["power"], "accuracy": data["accuracy"],
                "damage_class": data["damage_class"]["name"], "multi_hit": multi_hit,
                "crit": meta.get("crit_rate") == 6, "targets": 1
            }

            t_name = data.get("target", {}).get("name", "")
            if t_name in ["all-opponents", "all-other-pokemon"]: move["targets"] = 2
            elif t_name in ["entire-field", "all-pokemon"]: move["targets"] = 3
            
            return move_id, name, move
        except Exception as exc:
            await asyncio.sleep(BACKOFF_BASE * (2 ** attempt))
    return None

async def build(save_to="data/all_moves.json"):
    Path("data").mkdir(exist_ok=True)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECS), headers=HEADERS) as session:
        entries = await fetch_all_urls(session)
        sem = asyncio.Semaphore(MAX_CONCURRENT)
        tasks = [fetch_move_detail(session, sem, e) for e in entries]

        results_list = []
        for coro in asyncio.as_completed(tasks):
            res = await coro
            if res: results_list.append(res)

        # Le tri magique par ID
        results_list.sort(key=lambda x: x[0])
        final_dict = {name: data for _, name, data in results_list}

    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(final_dict, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(build())