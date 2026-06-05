import argparse, asyncio, json, sys
from pathlib import Path
import aiohttp

BASE, MAX_CONCURRENT, MAX_RETRIES, BACKOFF_BASE, TIMEOUT_SECS = "https://pokeapi.co/api/v2", 25, 4, 1.5, 20
DATA_DIR = Path(__file__).resolve().parents[2] / "data"

def load_move_list(moves_file=None):
    path = moves_file if moves_file else DATA_DIR / "all_moves.json"
    with open(path, "r", encoding="utf-8") as f: return list(json.load(f).keys())

async def fetch_move_meta(session, sem, name):
    for attempt in range(MAX_RETRIES):
        try:
            async with sem, session.get(f"{BASE}/move/{name}/") as r: 
                data = await r.json()
                
            meta = data.get("meta") or {}
            move_id = data.get("id", 999999) # Sert uniquement au tri !
            
            ailment, flinch, stat = int(meta.get("ailment_chance") or 0), int(meta.get("flinch_chance") or 0), int(meta.get("stat_chance") or 0)
            flags = {"has_secondary": (ailment > 0 or flinch > 0 or stat > 0), "has_flinch": flinch > 0, "has_ailment": ailment > 0, "has_stat_change": stat > 0}
            
            # Retourne l'ID pour le tri, et le nom en anglais pour la clé
            return move_id, name, flags
        except Exception: await asyncio.sleep(BACKOFF_BASE * (2 ** attempt))
    return None

async def build(names: list, out_path: Path):
    print(f"Local items total : {len(names)}\nProcessing list   : {len(names)}")
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECS), headers={"Cache-Control": "no-cache"}) as session:
        sem = asyncio.Semaphore(MAX_CONCURRENT)
        tasks = [fetch_move_meta(session, sem, n) for n in names]
        
        results_list = []
        done, total = 0, len(tasks)

        for coro in asyncio.as_completed(tasks):
            res = await coro
            done += 1
            if res: results_list.append(res)
            if done % 100 == 0 or done == total: print(f"  → {done}/{total} done  ({len(results_list)} ok)")
            
    results_list.sort(key=lambda x: x[0])
    final_dict = {name: data for _, name, data in results_list}
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f: json.dump(final_dict, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Saved {len(final_dict)} secondary effects → {out_path}")

    for check_key, label in [("pound", "Pound"), ("thunder-punch", "Thunder Punch")]:
        print(f"  {label:20s} ({check_key:>15}) : {final_dict.get(check_key, 'MISSING')}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--moves-file"); parser.add_argument("--out", default=str(DATA_DIR / "moves_secondary_effect.json"))
    args, _ = parser.parse_known_args()
    if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(build(load_move_list(Path(args.moves_file) if args.moves_file else None), Path(args.out)))

if __name__ == "__main__": main()