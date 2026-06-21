"""Simple 24h file cache so you don't burn API quota re-scanning a niche."""
import json
import os
import time

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
TTL_SECONDS = 60 * 60 * 24  # 24 hours


def _path(niche: str) -> str:
    safe = "".join(c for c in niche.lower() if c.isalnum()) or "niche"
    return os.path.join(CACHE_DIR, f"{safe}.json")


def get(niche: str):
    p = _path(niche)
    if os.path.exists(p) and (time.time() - os.path.getmtime(p)) < TTL_SECONDS:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return None


def set(niche: str, report: dict) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(_path(niche), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
