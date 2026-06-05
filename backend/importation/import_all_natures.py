import asyncio, json, sys
from pathlib import Path
import aiohttp

BASE = "https://pokeapi.co/api/v2"

async def fetch_all_urls(session: aiohttp.ClientSession):
    async with session.get(f"{BASE}/nature?limit=100000") as r:
        return (await r.json()).get("results", [])

async def fetch_nature_detail(session: aiohttp.ClientSession, sem: asyncio.Semaphore, entry: dict):
    url, name = entry["url"], entry["name"]
    nature_id = int(url.rstrip("/").split("/")[-1])

    for attempt in range(4):
        try:
            async with sem, session.get(url) as r:
                info = await r.json()
            return nature_id, name, {
                "increase": info['increased_stat']['name'] if info['increased_stat'] else None,
                "decrease": info['decreased_stat']['name'] if info['decreased_stat'] else None
            }
        except Exception:
            await asyncio.sleep(1.5 * (2 ** attempt))
    return None

async def build(save_to="data/all_natures.json"):
    Path("data").mkdir(exist_ok=True)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20), headers={"Cache-Control": "no-cache"}) as session:
        entries = await fetch_all_urls(session)
        sem = asyncio.Semaphore(25)
        tasks = [fetch_nature_detail(session, sem, e) for e in entries]

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