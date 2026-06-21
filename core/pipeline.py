"""Orchestrates a single niche scan end-to-end."""
from collectors.reddit_collector import collect_reddit
from collectors.youtube_collector import collect_youtube
from analysis.analyzer import analyze
from core import cache


def rank_communities(reddit_comms: list[dict], items: list[dict]) -> list[dict]:
    """Rank communities by how often they appear, enriched with subscriber counts."""
    counts: dict[str, int] = {}
    for it in items:
        c = it.get("community")
        if c:
            counts[c] = counts.get(c, 0) + 1

    out = []
    seen = set()
    for rc in reddit_comms:
        out.append({
            "name": rc["name"],
            "subscribers": rc.get("subscribers", 0),
            "mentions": counts.get(rc["name"], 0),
        })
        seen.add(rc["name"])
    for c, n in counts.items():
        if c not in seen:
            out.append({"name": c, "subscribers": 0, "mentions": n})

    out.sort(key=lambda x: (x["mentions"], x["subscribers"]), reverse=True)
    return out[:8]


def scan(niche: str, use_cache: bool = True) -> dict:
    niche = (niche or "").strip()
    if not niche:
        return {"niche": niche, "error": "Please provide a niche.", "topics": [], "communities": []}

    if use_cache:
        cached = cache.get(niche)
        if cached:
            cached["cached"] = True
            return cached

    reddit = collect_reddit(niche)
    youtube = collect_youtube(niche)
    items = reddit["items"] + youtube["items"]

    if not items:
        return {
            "niche": niche,
            "error": "No data collected. Add Reddit and/or YouTube API keys to .env.",
            "topics": [],
            "communities": [],
        }

    topics = analyze(niche, items)
    communities = rank_communities(reddit["communities"], items)

    report = {
        "niche": niche,
        "stats": {
            "scanned": len(items),
            "topics": len(topics),
            "communities": len(communities),
        },
        "topics": topics,
        "communities": communities,
        "cached": False,
    }
    cache.set(niche, report)
    return report
