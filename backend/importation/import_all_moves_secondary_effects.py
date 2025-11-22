"""Export a JSON mapping of moves -> secondary-effect flags for Sheer Force.

This script queries the PokeAPI move endpoint for each move listed in
`data/all_moves.json` (or from an explicit list) and records whether the
move has any secondary effects according to the `meta` object.

Output format (JSON):
{
  "tackle": {
    "has_secondary": false,
    "has_flinch": false,
    "has_ailment": false,
    "has_stat_change": false
  },
  "thunder-punch": { ... }
}

Usage:
  python export_moves_secondary_effects.py          # process all moves from data/all_moves.json
  python export_moves_secondary_effects.py --out data/moves_secondary_effect.json --continue
  python export_moves_secondary_effects.py --limit 200 --rate 0.2

The script is polite to the API (configurable `--rate`) and supports
`--continue` to skip moves already present in the output file.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any, Iterable

import requests

BASE = "https://pokeapi.co/api/v2"
MOVE_ENDPOINT = BASE + "/move/"
# Resolve repository root (two levels up from backend/importation -> repo root)
HERE = Path(__file__).resolve().parents[2]
DATA_DIR = HERE / "data"


def fetch_move_meta(session: requests.Session, name: str, timeout: float = 10.0) -> Dict[str, Any]:
    url = MOVE_ENDPOINT + f"{name}/"
    r = session.get(url, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return data.get("meta") or {}


def has_secondary_effect(meta: Dict[str, Any]) -> Dict[str, bool]:
    if not meta:
        return {
            "has_secondary": False,
            "has_flinch": False,
            "has_ailment": False,
            "has_stat_change": False,
        }

    # PokeAPI move.meta contains numeric fields like ailment_chance, flinch_chance, stat_chance
    # Some moves may omit fields -> default to 0
    ailment = int(meta.get("ailment_chance") or 0)
    flinch = int(meta.get("flinch_chance") or 0)
    stat = int(meta.get("stat_chance") or 0)

    return {
        "has_secondary": (ailment > 0 or flinch > 0 or stat > 0),
        "has_flinch": flinch > 0,
        "has_ailment": ailment > 0,
        "has_stat_change": stat > 0,
    }


def load_move_list(moves_file: Path | None = None) -> Iterable[str]:
    if moves_file and moves_file.exists():
        with open(moves_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            # data may be dict: name->details
            if isinstance(data, dict):
                return list(data.keys())
            # or list of names
            if isinstance(data, list):
                return data
    # fallback: read all_moves.json
    all_moves_path = DATA_DIR / "all_moves.json"
    if not all_moves_path.exists():
        raise SystemExit(f"Missing {all_moves_path}; run import_all_attacks.py first")
    with open(all_moves_path, "r", encoding="utf-8") as f:
        all_moves = json.load(f)
    return list(all_moves.keys())


def save_json(data: Dict[str, Any], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} entries to {path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export moves secondary-effect flags for Sheer Force")
    parser.add_argument("--moves-file", help="Optional JSON file with move list (dict or list)")
    parser.add_argument("--out", default=str(DATA_DIR / "moves_secondary_effect.json"), help="Output JSON path")
    parser.add_argument("--rate", type=float, default=0.12, help="Seconds to wait between requests")
    parser.add_argument("--retries", type=int, default=3, help="Retry attempts per move")
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout per request")
    parser.add_argument("--continue", dest="cont", action="store_true", help="Continue and skip existing entries in output file")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of moves processed (0 = all)")
    args = parser.parse_args(argv)

    moves_file = Path(args.moves_file) if args.moves_file else None
    out_path = Path(args.out)

    names = list(load_move_list(moves_file))
    if args.limit and args.limit > 0:
        names = names[: args.limit]

    existing: Dict[str, Any] = {}
    if out_path.exists():
        try:
            with open(out_path, "r", encoding="utf-8") as f:
                existing = json.load(f) or {}
        except Exception:
            existing = {}

    session = requests.Session()
    session.headers.update({"User-Agent": "pokemon-secondary-export/1.0 (by you)"})

    result: Dict[str, Any] = dict(existing) if args.cont else {}

    total = len(names)
    for i, name in enumerate(names, start=1):
        if args.cont and name in result:
            print(f"Skipping existing: {name} ({i}/{total})")
            continue

        success = False
        for attempt in range(1, args.retries + 1):
            try:
                meta = fetch_move_meta(session, name, timeout=args.timeout)
                flags = has_secondary_effect(meta)
                result[name] = flags
                success = True
                break
            except Exception as e:
                print(f"[WARN] {name} fetch failed (attempt {attempt}/{args.retries}): {e}")
                if attempt < args.retries:
                    time.sleep(0.5 * attempt)
                    continue
        if not success:
            print(f"[ERROR] Failed to fetch move {name} after {args.retries} attempts; skipping")
        if i % 50 == 0:
            print(f"Processed {i}/{total} moves")
        time.sleep(args.rate)

    save_json(result, out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
