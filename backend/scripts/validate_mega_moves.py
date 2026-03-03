import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

# Locate the repository data directory by walking upwards until a `data/` folder is found.
here = Path(__file__).resolve().parent
curr = here
DATA = None
while True:
    candidate = curr / "data"
    if candidate.exists() and candidate.is_dir():
        DATA = candidate
        break
    if curr.parent == curr:
        break
    curr = curr.parent

if DATA is None:
    raise SystemExit("data/ directory not found from script location; please run from repo tree")

all_pok = json.load(open(DATA / "all_pokemon.json", encoding='utf-8'))
MOVES_FILE = DATA / "all_pokemon_moves.json"
all_moves = json.load(open(MOVES_FILE, encoding='utf-8'))

def parse_args():
    p = argparse.ArgumentParser(description="Validate (and optionally fill) mega moves")
    p.add_argument("--apply", action="store_true", help="Apply changes: copy base moves into mega entries and write file")
    p.add_argument("--merge-mega", action="store_true", help="Alias for --apply (kept for backward compatibility)")
    p.add_argument("--dry-run", action="store_true", help="Only show what would be changed (default if --apply not used)")
    p.add_argument("--no-backup", action="store_true", help="When applying, don't create a backup of the original moves file")
    return p.parse_args()


args = parse_args()
# support legacy flag name
if getattr(args, 'merge_mega', False):
    args.apply = True

fails = []
checked = 0
written = []
for slug, entry in all_pok.items():
    if not slug or "-mega" not in slug:
        continue
    checked += 1
    mega_id = entry.get("id")
    mega_moves = all_moves.get(str(mega_id))
    # try derive base slug
    if slug.endswith(('-x','-y')) and '-mega-' in slug:
        base_slug = slug.split('-mega', 1)[0]
    else:
        base_slug = slug.replace('-mega', '')
    base_entry = all_pok.get(base_slug)
    base_id = base_entry.get('id') if base_entry else None
    base_moves = all_moves.get(str(base_id)) if base_id else None

    if mega_moves is None and base_moves is None:
        fails.append((slug, mega_id, base_slug, base_id, 'no moves for mega nor base'))
    elif mega_moves is None and base_moves:
        # acceptable: mega should at least inherit base moves (our API now falls back)
        # If requested, copy base moves into the mega entry
        if args.apply:
            if mega_id:
                all_moves[str(mega_id)] = base_moves
                written.append((slug, mega_id, base_slug, base_id, len(base_moves)))
            else:
                # can't write without mega id — record as a failure
                fails.append((slug, mega_id, base_slug, base_id, 'mega has no id, cannot write moves'))
        else:
            # dry-run / no-op: report what would be done
            written.append((slug, mega_id, base_slug, base_id, len(base_moves)))
    else:
        # mega_moves exists; check if it contains at least all base moves
        if base_moves:
            missing = [m for m in base_moves if m not in (mega_moves or [])]
            if missing:
                # record failure for reporting
                fails.append((slug, mega_id, base_slug, base_id, f'missing {len(missing)} moves'))
                # if requested, add missing base moves to the mega's move list (merge)
                if args.apply:
                    if mega_id:
                        combined = list(mega_moves or [])
                        # preserve order from base_moves for missing entries
                        for m in base_moves:
                            if m not in combined:
                                combined.append(m)
                        all_moves[str(mega_id)] = combined
                        written.append((slug, mega_id, base_slug, base_id, len(missing)))
                    else:
                        fails.append((slug, mega_id, base_slug, base_id, 'mega has no id, cannot merge moves'))

print(f"Checked {checked} mega entries")
print(f"Checked {checked} mega entries")
print(f"Planned writes: {len(written)} (args.apply={args.apply})")
if written:
    if args.apply:
        print(f"Will write {len(written)} mega entries into {MOVES_FILE}")
    else:
        print(f"Would write {len(written)} mega entries (dry-run). Use --apply to perform these changes")
if not fails:
    print("All mega entries either have moves or their base has moves — OK")
else:
    print(f"Found {len(fails)} problems:")
    for it in fails[:50]:
            print(it)

    if args.apply and written:
        # backup
        if not args.no_backup:
            ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            bak = MOVES_FILE.with_name(MOVES_FILE.name + ".bak." + ts)
            shutil.copy2(MOVES_FILE, bak)
            print(f"Backup of moves file created at: {bak}")

        # write file
        with open(MOVES_FILE, "w", encoding="utf-8") as f:
            json.dump(all_moves, f, indent=2, ensure_ascii=False)
        print(f"Applied changes: updated {len(written)} mega entries in {MOVES_FILE}")

        # remove fixed problems from the failure list so exit code reflects remaining issues
        try:
            fixed_slugs = {w[0] for w in written}
            fails = [f for f in fails if f[0] not in fixed_slugs]
        except Exception:
            # if something unexpected happens, leave fails as-is
            pass

# exit code for CI
import sys
sys.exit(0 if not fails else 2)
