"""Model layer: public Reddit data source (PRAW).

Returns empty lists if credentials are missing, so the app runs YouTube-only
until Reddit API access is approved. Each item is tagged with a 'kind'
('post' or 'comment') so the analyzer can weight comments highest.
"""
from __future__ import annotations
from app.models import config


class RedditSource:
    def collect(self, niche: str, limit: int = 60) -> dict:
        """Return {'items': [...], 'communities': [...]}."""
        if not config.HAS_REDDIT:
            print("[reddit] No credentials - skipping. Set REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET in .env")
            return {"items": [], "communities": []}

        import praw

        reddit = praw.Reddit(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_CLIENT_SECRET,
            user_agent=config.REDDIT_USER_AGENT,
        )

        items: list[dict] = []
        communities: dict[str, dict] = {}

        try:
            for sub in reddit.subreddits.search(niche, limit=6):
                communities[sub.display_name] = {
                    "name": f"r/{sub.display_name}",
                    "subscribers": sub.subscribers or 0,
                }
        except Exception as e:
            print(f"[reddit] subreddit search failed: {e}")

        try:
            for post in reddit.subreddit("all").search(
                niche, sort="relevance", time_filter="year", limit=limit
            ):
                permalink = post.permalink
                items.append({
                    "source": "reddit",
                    "kind": "post",
                    "text": f"{post.title}. {(post.selftext or '')[:500]}",
                    "score": int(post.score or 0),
                    "url": "https://reddit.com" + permalink,
                    "community": f"r/{post.subreddit.display_name}",
                })
                try:
                    post.comments.replace_more(limit=0)
                    for c in post.comments[:3]:
                        if len(getattr(c, "body", "")) > 40:
                            items.append({
                                "source": "reddit",
                                "kind": "comment",
                                "text": c.body[:500],
                                "score": int(c.score or 0),
                                "url": "https://reddit.com" + permalink,
                                "community": f"r/{post.subreddit.display_name}",
                            })
                except Exception as e:
                    print(f"[reddit] comment fetch failed: {e}")
        except Exception as e:
            print(f"[reddit] post search failed: {e}")

        print(f"[reddit] collected {len(items)} items, {len(communities)} communities")
        return {"items": items, "communities": list(communities.values())}
