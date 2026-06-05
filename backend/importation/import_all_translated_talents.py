import asyncio, json, sys
from pathlib import Path
import aiohttp

BASE, MAX_CONCURRENT, MAX_RETRIES, BACKOFF_BASE, TIMEOUT_SECS = "https://pokeapi.co/api/v2", 25, 4, 1.5, 20
HEADERS = {"User-Agent": "pokemon-script/3.0", "Cache-Control": "no-cache"}

async def fetch_all_urls(session: aiohttp.ClientSession):
    async with session.get(f"{BASE}/ability?limit=100000") as r: data = await r.json()
    urls = data.get("results", [])
    print(f"API total count : {data.get('count', len(urls))}\nURLs retrieved  : {len(urls)}")
    return urls

async def fetch_ability_translations(session: aiohttp.ClientSession, sem: asyncio.Semaphore, entry: dict):
    url = entry["url"]
    ability_id_str = url.rstrip("/").split("/")[-1]
    sort_id = int(ability_id_str)
    
    for attempt in range(MAX_RETRIES):
        try:
            async with sem, session.get(url) as r: data = await r.json()
            names = {e["language"]["name"]: e["name"] for e in data["names"]}
            descriptions = {}
            for e in data["flavor_text_entries"]:
                lang = e["language"]["name"]
                if lang not in descriptions: descriptions[lang] = e["flavor_text"].replace("\n", " ").replace("\f", " ").strip()
            return sort_id, ability_id_str, {"names": names, "descriptions": descriptions}
        except Exception: await asyncio.sleep(BACKOFF_BASE * (2 ** attempt))
    return None

async def build(save_to="data/all_ability_translations.json"):
    Path("data").mkdir(exist_ok=True)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECS), headers=HEADERS) as session:
        entries = await fetch_all_urls(session)
        
        # --- LA FAMEUSE CORRECTION EST ICI ---
        sem = asyncio.Semaphore(MAX_CONCURRENT)
        tasks = [fetch_ability_translations(session, sem, e) for e in entries]
        # ------------------------------------
        
        results, done, total = {}, 0, len(tasks)

        for coro in asyncio.as_completed(tasks):
            res = await coro
            done += 1
            if res: results[res[0]] = (res[1], res[2])
            if done % 50 == 0 or done == total: print(f"  → {done}/{total} done  ({len(results)} ok)")

    sorted_results = dict(sorted(results.items(), key=lambda kv: kv[0]))
    final_dict = {val[0]: val[1] for val in sorted_results.values()}
    with open(save_to, "w", encoding="utf-8") as f: json.dump(final_dict, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved {len(final_dict)} ability translations → {save_to}")

    for check_key, label in [("1", "ID 1"), ("2", "ID 2")]:
        val = str(final_dict.get(check_key, "MISSING"))
        print(f"  {label:20s} ({check_key:>12}) : {val[:55] + '...' if len(val) > 55 else val}")

if __name__ == "__main__":
    if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(build())