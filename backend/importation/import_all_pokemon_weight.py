import asyncio, json, sys
from pathlib import Path
import aiohttp

BASE = "https://pokeapi.co/api/v2"

async def fetch_all_urls(session: aiohttp.ClientSession):
    async with session.get(f"{BASE}/pokemon?limit=100000") as r:
        return (await r.json()).get("results", [])

async def fetch_weight_height(session: aiohttp.ClientSession, sem: asyncio.Semaphore, entry: dict):
    url = entry["url"]
    pk_id = int(url.rstrip("/").split("/")[-1])
    
    for attempt in range(4):
        try:
            async with sem, session.get(url) as r:
                data = await r.json()
            return pk_id, str(pk_id), {"weight_kg": data["weight"] / 10.0, "height_m": data["height"] / 10.0}
        except Exception:
            await asyncio.sleep(1.5 * (2 ** attempt))
    return None

async def build(save_to="data/all_pokemon_weight_height.json"):
    Path("data").mkdir(exist_ok=True)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20), headers={"Cache-Control": "no-cache"}) as session:
        entries = await fetch_all_urls(session)
        sem = asyncio.Semaphore(25)
        tasks = [fetch_weight_height(session, sem, e) for e in entries]

        results_list = []
        for coro in asyncio.as_completed(tasks):
            res = await coro
            if res: results_list.append(res)

        results_list.sort(key=lambda x: x[0])
        final_dict = {str_id: data for _, str_id, data in results_list}

    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(final_dict, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(build())