"""View layer: shape raw analysis data into the API response (ScanReport)."""
from __future__ import annotations


def build_stats(items: list[dict], topics: list, communities: list, videos_total: int) -> dict:
    comments = sum(1 for it in items if it.get("kind") == "comment")
    titles = sum(1 for it in items if it.get("kind") == "video_title")
    return {
        "scanned": len(items),
        "topics": len(topics),
        "communities": len(communities),
        "videos": videos_total,
        "comments": comments,
        "titles": titles,
    }


def build_report(niche, items, topics, communities, videos, videos_total, cached=False) -> dict:
    return {
        "niche": niche,
        "stats": build_stats(items, topics, communities, videos_total),
        "topics": topics,
        "videos": videos,
        "communities": communities,
        "cached": cached,
        "error": None,
    }


def error_report(niche, message) -> dict:
    return {
        "niche": niche,
        "error": message,
        "stats": build_stats([], [], [], 0),
        "topics": [],
        "videos": [],
        "communities": [],
        "cached": False,
    }
