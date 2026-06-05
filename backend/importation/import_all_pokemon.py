import asyncio, json, sys
from pathlib import Path
import aiohttp

BASE = "https://pokeapi.co/api/v2"

async def fetch_all_urls(session: aiohttp.ClientSession):
    async with session.get(f"{BASE}/pokemon?limit=100000") as r:
        return (await r.json()).get("results", [])

async def fetch_pokemon_detail(session: aiohttp.ClientSession, sem: asyncio.Semaphore, entry: dict):
    url, pk_name = entry["url"], entry["name"]
    pk_id = int(url.rstrip("/").split("/")[-1])
    
    for attempt in range(4):
        try:
            async with sem, session.get(url) as r:
                data = await r.json()

            stats = {s["stat"]["name"]: s["base_stat"] for s in data.get("stats", [])}
            detail = {"id": data.get("id"), "types": [t["type"]["name"] for t in sorted(data.get("types", []), key=lambda x: x["slot"])], "base_stats": stats}
            return pk_id, pk_name, detail
        except Exception:
            await asyncio.sleep(1.5 * (2 ** attempt))
    return None

async def build(save_to="data/all_pokemon.json"):
    Path("data").mkdir(exist_ok=True)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20), headers={"Cache-Control": "no-cache"}) as session:
        entries = await fetch_all_urls(session)
        sem = asyncio.Semaphore(25)
        tasks = [fetch_pokemon_detail(session, sem, e) for e in entries]

        results_list = []
        for coro in asyncio.as_completed(tasks):
            res = await coro
            if res: results_list.append(res)

        results_list.sort(key=lambda x: x[0])
        final_dict = {name: data for _, name, data in results_list}

    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(final_dict, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(build())