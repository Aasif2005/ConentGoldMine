"""Controller layer: orchestrate sources -> analyzer -> view for a niche scan."""
from __future__ import annotations
from app.models import cache
from app.models.youtube_source import YouTubeSource
from app.models.reddit_source import RedditSource
from app.services.analyzer import Analyzer
from app.views import serializers


class ScanController:
    def __init__(self):
        self.youtube = YouTubeSource()
        self.reddit = RedditSource()
        self.analyzer = Analyzer()

    def scan(self, niche: str, use_cache: bool = True) -> dict:
        niche = (niche or "").strip()
        if not niche:
            return serializers.error_report(niche, "Please provide a niche.")

        if use_cache:
            cached = cache.get(niche)
            if cached:
                cached["cached"] = True
                return cached

        # Models: gather raw signal from each source.
        reddit = self.reddit.collect(niche)
        youtube = self.youtube.collect(niche)
        items = reddit["items"] + youtube["items"]

        if not items:
            return serializers.error_report(
                niche,
                "No data collected. Add a YouTube and/or Reddit API key to .env.",
            )

        # Service: cluster into ranked topics (comments weighted highest).
        topics = self.analyzer.analyze(niche, items)

        # Controller-level shaping that needs cross-source data.
        communities = self._rank_communities(reddit["communities"], items)
        all_videos = youtube.get("videos", [])
        videos = sorted(all_videos, key=lambda v: v.get("views", 0), reverse=True)[:12]

        # View: assemble the API response.
        report = serializers.build_report(
            niche, items, topics, communities, videos, len(all_videos), cached=False
        )
        cache.set(niche, report)
        return report

    @staticmethod
    def _rank_communities(reddit_comms: list[dict], items: list[dict]) -> list[dict]:
        counts: dict[str, int] = {}
        for it in items:
            c = it.get("community")
            if c:
                counts[c] = counts.get(c, 0) + 1
        out: list[dict] = []
        seen: set[str] = set()
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
