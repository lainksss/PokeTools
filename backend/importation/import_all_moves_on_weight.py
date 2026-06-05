import asyncio, json, sys
from pathlib import Path
import aiohttp

BASE = "https://pokeapi.co/api/v2"

async def fetch_all_urls(session: aiohttp.ClientSession):
    async with session.get(f"{BASE}/move?limit=100000") as r:
        return (await r.json()).get("results", [])

async def fetch_weight_move(session: aiohttp.ClientSession, sem: asyncio.Semaphore, entry: dict):
    url, name = entry["url"], entry["name"]
    move_id = int(url.rstrip("/").split("/")[-1])
    if name.lower() == "transform": return None

    for attempt in range(4):
        try:
            async with sem, session.get(url) as r:
                detail = await r.json()
            
            for effect_entry in detail.get("effect_entries", []):
                if effect_entry["language"]["name"] == "en" and "weight" in effect_entry["effect"].lower():
                    return move_id, name, {
                        "id": detail["id"], "power": detail["power"], "type": detail["type"]["name"],
                        "pp": detail["pp"], "accuracy": detail["accuracy"], "effect": effect_entry["effect"]
                    }
            return None
        except Exception:
            await asyncio.sleep(1.5 * (2 ** attempt))
    return None

async def build(save_to="data/all_pokemon_weight_moves.json"):
    Path("data").mkdir(exist_ok=True)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20), headers={"Cache-Control": "no-cache"}) as session:
        entries = await fetch_all_urls(session)
        sem = asyncio.Semaphore(25)
        tasks = [fetch_weight_move(session, sem, e) for e in entries]

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