import asyncio, json, sys
from pathlib import Path
import aiohttp

BASE = "https://pokeapi.co/api/v2"

async def fetch_all_type_entries(session: aiohttp.ClientSession):
    async with session.get(f"{BASE}/type?limit=1000") as r:
        return (await r.json()).get("results", [])

async def fetch_type_relation(session: aiohttp.ClientSession, sem: asyncio.Semaphore, entry: dict):
    url, type_name = entry["url"], entry["name"]
    type_id = int(url.rstrip("/").split("/")[-1])

    for attempt in range(4):
        try:
            async with sem, session.get(url) as r:
                data = await r.json()

            rel = data["damage_relations"]
            relations = {
                "weak_to": [d["name"] for d in rel["double_damage_from"]],
                "resistant_to": [d["name"] for d in rel["half_damage_from"]],
                "immune_to": [d["name"] for d in rel["no_damage_from"]],
                "strong_against": [d["name"] for d in rel["double_damage_to"]],
                "weak_against": [d["name"] for d in rel["half_damage_to"]],
                "no_damage_to": [d["name"] for d in rel["no_damage_to"]],
            }
            return type_id, type_name, relations
        except Exception:
            await asyncio.sleep(1.5 * (2 ** attempt))
    return None

async def build(save_to="data/all_types.json"):
    Path("data").mkdir(exist_ok=True)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20), headers={"Cache-Control": "no-cache"}) as session:
        entries = await fetch_all_type_entries(session)
        sem = asyncio.Semaphore(20)
        tasks = [fetch_type_relation(session, sem, e) for e in entries]

        results_list = []
        for coro in asyncio.as_completed(tasks):
            res = await coro
            if res: results_list.append(res)

        results_list.sort(key=lambda x: x[0])
        final_dict = {name: data for _, name, data in results_list}

    with open(save_to, "w", encoding="utf-8") as f:
        json.dump(final_dict, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(build())