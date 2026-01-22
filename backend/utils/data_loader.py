"""Lazy-loaded JSON data cache for PokeTools API."""

import json
from pathlib import Path

# Setup paths
HERE = Path(__file__).resolve().parent.parent
ROOT = HERE.parent
DATA_DIR = ROOT / "data"

_CACHE = {}


def load_json(filename: str):
    """Load and cache JSON files from the data directory."""
    if filename in _CACHE:
        return _CACHE[filename]
    
    path = DATA_DIR / filename
    if not path.exists():
        return None
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            _CACHE[filename] = data
            return data
    except Exception:
        return None


def clear_cache():
    """Clear the data cache (useful for testing)."""
    global _CACHE
    _CACHE = {}
