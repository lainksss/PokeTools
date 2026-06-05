import asyncio, json, sys
from pathlib import Path
import aiohttp

BASE = "https://pokeapi.co/api/v2"
HEADERS = {"User-Agent": "pokemon-evolution-async/3.0", "Cache-Control": "no-cache"}

async def fetch_all_urls(session: aiohttp.ClientSession):
    async with session.get(f"{BASE}/pokemon?limit=100000") as r:
        return (await r.json()).get("results", [])

def check_evolution(chain, name):
    if chain["species"]["name"] == name: return bool(chain["evolves_to"])
    for evo in chain["evolves_to"]:
        res = check_evolution(evo, name)
        if res is not None: return res
    return None

async def check_can_evolve(session: aiohttp.ClientSession, sem: asyncio.Semaphore, entry: dict):
    name, pk_id = entry["name"], int(entry["url"].rstrip("/").split("/")[-1])
    
    for attempt in range(4):
        try:
            async with sem, session.get(f"{BASE}/pokemon-species/{name}/") as r:
                if r.status == 404: return None
                species_data = await r.json()
                
            if not species_data.get("evolution_chain"):
                return pk_id, name, {"id": pk_id, "can_evolve": False}
                
            async with session.get(species_data["evolution_chain"]["url"]) as r:
                chain_data = await r.json()
            
            return pk_id, name, {"id": pk_id, "can_evolve": bool(check_evolution(chain_data["chain"], name))}
        except Exception:
            await asyncio.sleep(1.5 * (2 ** attempt))
    return None

async def build(save_to="data/pokemon_evolution.json"):
    Path("data").mkdir(exist_ok=True)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20), headers=HEADERS) as session:
        entries = await fetch_all_urls(session)
        sem = asyncio.Semaphore(25)
        tasks = [check_can_evolve(session, sem, e) for e in entries]

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